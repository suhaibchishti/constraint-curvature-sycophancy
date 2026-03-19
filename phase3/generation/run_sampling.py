#!/usr/bin/env python3
"""
Phase 3 SageMaker Processing Job: Behavioral Distribution Sampling.
Generates multiple samples per prompt at varying temperatures.

Runs inside SageMaker or locally.
"""
import os
import sys
import subprocess
import json
import copy

# ---------- SageMaker bootstrap ----------
REPO_DIR = "/opt/ml/processing/input/repo"
OUT_DIR  = "/opt/ml/processing/output"
IS_SAGEMAKER = os.path.exists(REPO_DIR)

if IS_SAGEMAKER:
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
        "transformers>=4.36.0",
        "accelerate>=0.25.0",
        "bitsandbytes>=0.41.0",
        "pyyaml>=6.0",
        "boto3>=1.28.0",
        "tqdm>=4.60.0"
    ])
    print("Dependencies installed.")
    # Add repo src to path (matches processing_job.py pattern)
    sys.path.insert(0, os.path.join(REPO_DIR, "src"))
else:
    # Local fallback
    REPO_DIR = "."
    OUT_DIR  = "./phase3/outputs/generations"
    sys.path.insert(0, os.path.join(REPO_DIR, "src"))

from cc_eval.load_model import load_hf_model
from cc_eval.generate import generate_outputs

# ---------- HF auth ----------
def setup_hf_auth():
    """Authenticate with HuggingFace using env var or Secrets Manager."""
    token = os.environ.get("HF_TOKEN")
    if not token or token == "YOUR_HF_TOKEN":
        try:
            import boto3
            sm = boto3.client("secretsmanager")
            secret = json.loads(sm.get_secret_value(SecretId="cc-eval-hf-token")["SecretString"])
            token = secret["HF_TOKEN"]
            print("Loaded HF token from Secrets Manager.")
        except Exception:
            pass
    if token and token != "YOUR_HF_TOKEN":
        try:
            from huggingface_hub import login
            login(token=token, add_to_git_credential=False)
            print("HuggingFace auth successful.")
        except Exception as e:
            print(f"HF auth warning: {e}")
    else:
        print("No HF_TOKEN found, assuming public models.")

# ---------- helpers ----------
def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line.strip()))
    return rows

def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

# ---------- main ----------
def main():
    setup_hf_auth()
    
    prompt_file = os.path.join(REPO_DIR, "phase3", "data", "prompt_variants.jsonl")

    print(f"Loading prompts from {prompt_file}...")
    base_prompts = load_jsonl(prompt_file)
    print(f"Loaded {len(base_prompts)} prompts.")

    model_name = os.environ.get("MODEL_PATH", "meta-llama/Meta-Llama-3-8B-Instruct")
    use_quant = os.environ.get("USE_QUANTIZATION", "true").lower() == "true"
    print(f"Loading model: {model_name} (quantized={use_quant})")

    tokenizer, model = load_hf_model(model_name, use_quantization=use_quant)

    temperatures = [0.0, 0.3, 0.7]

    # Build job list — 1 sample at T=0 (deterministic), 10 at T>0
    jobs = []
    for temp in temperatures:
        n_samples = 1 if temp == 0.0 else 10
        for sample_idx in range(n_samples):
            for p in base_prompts:
                p_copy = copy.deepcopy(p)
                p_copy["temperature"] = temp
                p_copy["sample_idx"] = sample_idx
                jobs.append(p_copy)

    print(f"Total evaluation jobs: {len(jobs)}")

    # Group by temperature for batched generation
    grouped = {t: [] for t in temperatures}
    for j in jobs:
        grouped[j["temperature"]].append(j)

    results = []
    for temp in temperatures:
        group = grouped[temp]
        print(f"Generating {len(group)} completions at temperature={temp}...")
        out = generate_outputs(
            tokenizer=tokenizer,
            model=model,
            prompts=group,
            max_new_tokens=150,
            temperature=temp,
            top_p=0.9,
            seed=42 + int(temp * 100),
            system_prompt="You are a helpful assistant."
        )
        for r in out:
            r["model"] = model_name
        results.extend(out)

    clean_name = model_name.split("/")[-1]
    out_file = os.path.join(OUT_DIR, f"{clean_name}_distributions.jsonl")
    print(f"Saving {len(results)} outputs to {out_file}...")
    write_jsonl(out_file, results)
    print("Done.")

if __name__ == "__main__":
    main()
