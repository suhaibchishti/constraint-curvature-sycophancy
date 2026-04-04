#!/usr/bin/env python3
"""
Phase 4 Processing Job — vLLM offline inference on SageMaker.

Generates responses for one 70B model across all Phase 3 framing conditions
using vLLM's offline batched inference (PagedAttention + continuous batching).

Inputs (from env):
    MODEL_PATH  — HuggingFace model ID
    MODEL_NAME  — short name for output files
    N_SAMPLES   — samples per (fact, framing, temp) combination (default: 5)
"""
import os, sys, json, subprocess

# Install vLLM 0.6.6 + force-reinstall transformers into conda env
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
    "--force-reinstall",
    "vllm==0.6.6", "transformers>=4.45.0", "boto3>=1.28.0",
])

sys.path.insert(0, '/opt/ml/processing/input/repo/src')
from cc_eval.secrets import setup_hf_auth

setup_hf_auth()

# Force vLLM v0 engine (stable multi-GPU path)
os.environ["VLLM_USE_V1"] = "0"

from vllm import LLM, SamplingParams

MODEL_PATH = os.environ["MODEL_PATH"]
MODEL_NAME = os.environ["MODEL_NAME"]
N_SAMPLES  = int(os.environ.get("N_SAMPLES", "5"))
OUTPUT_DIR = "/opt/ml/processing/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEMPERATURES = [0.0, 0.7]
SYSTEM_PROMPT = "You are a helpful assistant."
PROMPTS_PATH  = "/opt/ml/processing/input/repo/phase3/data/prompt_variants.jsonl"


def build_chat_prompt(tokenizer, prompt):
    """Apply chat template to a single user prompt."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": prompt},
    ]
    return tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=False
    )


def main():
    variants = [json.loads(l) for l in open(PROMPTS_PATH)]
    print(f"Loaded {len(variants)} prompt variants")

    # Load model once with vLLM — tensor_parallel_size=8 for 8×A10G
    print(f"Loading {MODEL_NAME} with vLLM (tensor_parallel_size=8, fp16)...")
    llm = LLM(
        model=MODEL_PATH,
        dtype="float16",
        tensor_parallel_size=8,
        trust_remote_code=True,
        max_model_len=4096,
    )
    tokenizer = llm.get_tokenizer()
    print("Model loaded.")

    rows = []

    for temp in TEMPERATURES:
        print(f"\nGenerating T={temp} ({N_SAMPLES} samples × {len(variants)} prompts)...")

        for sample_idx in range(N_SAMPLES):
            # Build all chat-formatted prompts for this sample
            if temp == 0 and sample_idx > 0:
                # T=0 is deterministic — skip duplicate samples
                break

            sampling = SamplingParams(
                temperature=temp if temp > 0 else 0,
                top_p=0.95 if temp > 0 else 1.0,
                max_tokens=512,
                seed=42 + sample_idx,  # vary per sample for T>0 diversity
            )

            formatted = [build_chat_prompt(tokenizer, v["prompt"]) for v in variants]

            # Single batched call — vLLM schedules all prompts optimally
            outputs = llm.generate(formatted, sampling)

            for variant, output in zip(variants, outputs):
                completion = output.outputs[0].text.strip()
                rows.append({
                    "model":       MODEL_PATH,
                    "fact_id":     variant["fact_id"],
                    "framing":     variant["framing"],
                    "temperature": temp,
                    "sample_idx":  sample_idx,
                    "prompt":      variant["prompt"],
                    "completion":  completion,
                    "seed":        42,
                })

            print(f"  T={temp} sample {sample_idx+1}/{N_SAMPLES} done ({len(outputs)} completions)")

    out_path = f"{OUTPUT_DIR}/{MODEL_NAME}_completions.jsonl"
    with open(out_path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    print(f"\nSaved {len(rows)} completions to {out_path}")


if __name__ == "__main__":
    main()
