#!/usr/bin/env python3
"""
Phase 4 Processing Job — runs on SageMaker instance.

Generates responses for one 70B model across all Phase 3 framing conditions.
Designed to be called by launch_phase4_70b.py.

Inputs (from env):
    MODEL_PATH  — HuggingFace model ID
    MODEL_NAME  — short name for output files
    N_SAMPLES   — samples per (fact, framing, temp) combination (default: 5)

Features:
    - Incremental checkpoints every 250 responses (crash-safe)
    - Per-response timeout guard (120s)
    - Periodic GPU cache clearing for 70B VRAM pressure
"""
import os, sys, json, gc, subprocess, signal

# Install dependencies
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
    "transformers>=4.40.0", "accelerate>=0.30.0", "bitsandbytes>=0.43.0",
    "pyyaml>=6.0", "boto3>=1.28.0",
])

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

sys.path.insert(0, '/opt/ml/processing/input/repo/src')
from cc_eval.secrets import setup_hf_auth

setup_hf_auth()

MODEL_PATH = os.environ["MODEL_PATH"]
MODEL_NAME = os.environ["MODEL_NAME"]
N_SAMPLES  = int(os.environ.get("N_SAMPLES", "5"))
OUTPUT_DIR = "/opt/ml/processing/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEMPERATURES = [0.0, 0.7]
SYSTEM_PROMPT = "You are a helpful assistant."
CHECKPOINT_EVERY = 250   # save progress every N responses
TIMEOUT_SECONDS  = 600   # max seconds per single generation (72B needs ~3-5 min on 8×A10G)

# Pre-built prompt variants from Phase 3 (all 5 framings × 50 facts)
PROMPTS_PATH = "/opt/ml/processing/input/repo/phase3/data/prompt_variants.jsonl"


class GenerationTimeout(Exception):
    pass


def _timeout_handler(signum, frame):
    raise GenerationTimeout("Generation exceeded timeout")


def load_model():
    print(f"Loading {MODEL_NAME} ({MODEL_PATH}) in fp16...")
    tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    mdl = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    mdl.eval()
    print(f"Model loaded. Device map: {mdl.hf_device_map if hasattr(mdl, 'hf_device_map') else 'auto'}")
    return tok, mdl


def generate(tok, mdl, prompt, temperature, seed):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": prompt},
    ]
    input_ids = tok.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    )
    if hasattr(input_ids, 'input_ids'):
        input_ids = input_ids.input_ids
    input_ids = input_ids.to(next(mdl.parameters()).device)

    torch.manual_seed(seed)
    do_sample = temperature > 0
    with torch.no_grad():
        out = mdl.generate(
            input_ids,
            max_new_tokens=512,
            do_sample=do_sample,
            temperature=max(temperature, 1e-6) if do_sample else None,
            top_p=0.95 if do_sample else None,
            pad_token_id=tok.eos_token_id,
        )
    completion = tok.decode(out[0][input_ids.shape[1]:], skip_special_tokens=True)
    return completion.strip()


def save_checkpoint(rows, label, output_dir):
    """Save an incremental checkpoint to disk."""
    ckpt_path = f"{output_dir}/{MODEL_NAME}_checkpoint.jsonl"
    with open(ckpt_path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print(f"  💾 Checkpoint saved: {ckpt_path} ({len(rows)} rows, {label})")


def main():
    # Load pre-built prompts (all 5 framings × 50 facts)
    prompts = [json.loads(l) for l in open(PROMPTS_PATH)]
    print(f"Loaded {len(prompts)} prompt variants")

    tok, mdl = load_model()
    rows = []

    total = len(prompts) * len(TEMPERATURES) * N_SAMPLES
    done = 0
    timeouts = 0

    for variant in prompts:
        for temp in TEMPERATURES:
            for sample_idx in range(N_SAMPLES):
                seed = 42 + sample_idx

                # Per-response timeout guard
                signal.signal(signal.SIGALRM, _timeout_handler)
                signal.alarm(TIMEOUT_SECONDS)
                try:
                    completion = generate(tok, mdl, variant["prompt"], temp, seed)
                except GenerationTimeout:
                    completion = "[TIMEOUT]"
                    timeouts += 1
                    print(f"  ⚠️  Timeout on fact={variant['fact_id']}, "
                          f"framing={variant['framing']}, T={temp}, sample={sample_idx}")
                finally:
                    signal.alarm(0)

                rows.append({
                    "model":       MODEL_PATH,
                    "fact_id":     variant["fact_id"],
                    "framing":     variant["framing"],
                    "temperature": temp,
                    "sample_idx":  sample_idx,
                    "prompt":      variant["prompt"],
                    "completion":  completion,
                    "seed":        seed,
                })
                done += 1

                if done % 100 == 0:
                    print(f"  {done}/{total} ({done/total*100:.0f}%)")

                # Incremental checkpoint
                if done % CHECKPOINT_EVERY == 0:
                    save_checkpoint(rows, f"{done}/{total}", OUTPUT_DIR)

                # Periodic GPU cache clearing to manage 70B VRAM pressure
                if done % 500 == 0:
                    gc.collect()
                    torch.cuda.empty_cache()

    # Final save
    out_path = f"{OUTPUT_DIR}/{MODEL_NAME}_completions.jsonl"
    with open(out_path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    print(f"\nSaved {len(rows)} completions to {out_path}")
    if timeouts > 0:
        print(f"⚠️  {timeouts} responses timed out (labeled [TIMEOUT])")


if __name__ == "__main__":
    main()
