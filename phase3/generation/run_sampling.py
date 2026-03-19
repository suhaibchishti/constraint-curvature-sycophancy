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
from tqdm import tqdm
import torch
from transformers import set_seed

# ---------- HF auth ----------
def setup_hf_auth():
    """Authenticate with HuggingFace using env var or Secrets Manager."""
    token = os.environ.get("HF_TOKEN")
    if token and token.startswith("{"):
        try:
            token = json.loads(token).get("HF_TOKEN", token)
        except (json.JSONDecodeError, AttributeError):
            pass
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

def append_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def load_checkpoint(path):
    """Return set of completed (id, temperature, sample_idx) tuples."""
    done = set()
    if os.path.exists(path):
        for row in load_jsonl(path):
            done.add((row["id"], row["temperature"], row["sample_idx"]))
    return done

# ---------- main ----------
BATCH_SIZE = 25  # flush to disk every N generations

def generate_one(tokenizer, model, prompt_text, temperature, seed, system_prompt):
    """Generate a single completion."""
    text = prompt_text
    if system_prompt:
        if hasattr(tokenizer, 'chat_template') and tokenizer.chat_template is not None:
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
                text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            except (ValueError, AttributeError):
                text = f"{system_prompt}\n\nUser: {text}\nAssistant:"
        else:
            text = f"{system_prompt}\n\nUser: {text}\nAssistant:"
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    input_len = inputs["input_ids"].shape[1]
    
    with torch.no_grad():
        gen = model.generate(
            **inputs, max_new_tokens=150, do_sample=(temperature > 0),
            temperature=temperature, top_p=0.9, pad_token_id=tokenizer.eos_token_id,
        )
    
    # Strictly slice off the input prompt to prevent chat template special tokens
    # from ruining the `startswith()` string check.
    new_tokens = gen[0][input_len:]
    completion = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    return completion

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
    clean_name = model_name.split("/")[-1]
    out_file = os.path.join(OUT_DIR, f"{clean_name}_distributions.jsonl")

    # Load checkpoint
    done = load_checkpoint(out_file)
    if done:
        print(f"Checkpoint: {len(done)} generations already complete, resuming...")

    # Build remaining jobs
    jobs = []
    for temp in temperatures:
        n_samples = 1 if temp == 0.0 else 10
        for sample_idx in range(n_samples):
            for p in base_prompts:
                if (p["id"], temp, sample_idx) in done:
                    continue
                p_copy = copy.deepcopy(p)
                p_copy["temperature"] = temp
                p_copy["sample_idx"] = sample_idx
                jobs.append(p_copy)

    print(f"Remaining jobs: {len(jobs)}")
    if not jobs:
        print("All generations already complete.")
        return

    # Generate with per-batch checkpointing
    buffer = []
    for job in tqdm(jobs, desc="Generating"):
        seed = 42 + int(job["temperature"] * 100)
        set_seed(seed)
        completion = generate_one(tokenizer, model, job["prompt"], job["temperature"], seed, "You are a helpful assistant.")
        job["completion"] = completion
        job["model"] = model_name
        job["seed"] = seed
        buffer.append(job)
        if len(buffer) >= BATCH_SIZE:
            append_jsonl(out_file, buffer)
            buffer = []
    if buffer:
        append_jsonl(out_file, buffer)

    total = len(load_jsonl(out_file))
    print(f"Done. Total outputs: {total}")

if __name__ == "__main__":
    main()
