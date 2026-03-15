#!/usr/bin/env python3
"""
Framing Ablation Experiment
Runs 30 neutral-framing prompts through all 6 models to compare
with original confirmatory-framing results.

Usage (SageMaker or local with GPU):
  python scripts/run_framing_ablation.py

Outputs: artifacts/ablation/*.jsonl (one per model)
"""
import os, sys, json, gc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cc_eval.prompts import load_yaml_items
from cc_eval.load_model import load_hf_model
from cc_eval.generate import generate_outputs, write_jsonl

MODELS = [
    ("mistral_v01", "mistralai/Mistral-7B-Instruct-v0.1"),
    ("mistral_v02", "mistralai/Mistral-7B-Instruct-v0.2"),
    ("qwen15",      "Qwen/Qwen1.5-7B-Chat"),
    ("qwen25",      "Qwen/Qwen2.5-7B-Instruct"),
]

EVAL_PATH = os.path.join(os.path.dirname(__file__), '..', 'evals', 'framing_ablation_neutral.yaml')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'ablation')
SYSTEM_PROMPT = "You are a helpful assistant."

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    items = load_yaml_items(EVAL_PATH)
    prompts = [{"id": it.id, "category": it.category, "expected": it.expected, "prompt": it.prompt} for it in items]
    print(f"Loaded {len(prompts)} neutral prompts")

    for model_name, model_path in MODELS:
        out_file = os.path.join(OUT_DIR, f"{model_name}.jsonl")
        if os.path.exists(out_file):
            print(f"Skipping {model_name} (already exists)")
            continue

        print(f"\n{'='*60}\nRunning {model_name}: {model_path}\n{'='*60}")
        import torch
        tok, mdl = load_hf_model(model_path, use_quantization=True)
        rows = generate_outputs(tok, mdl, prompts,
                                max_new_tokens=512, temperature=0.7,
                                top_p=0.95, seed=1,
                                system_prompt=SYSTEM_PROMPT)
        write_jsonl(out_file, rows)
        print(f"Saved {len(rows)} completions to {out_file}")

        del mdl, tok
        gc.collect()
        torch.cuda.empty_cache()

    print("\nDone. Label with GPT-4o-mini next.")

if __name__ == "__main__":
    main()
