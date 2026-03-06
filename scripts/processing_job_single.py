#!/usr/bin/env python3
"""
Single model processing job - for parallel execution.
"""
import os
import sys
import subprocess

# Install dependencies
print("Installing dependencies...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
    "typing_extensions>=4.8.0",
    "transformers>=4.36.0",
    "accelerate>=0.25.0", 
    "bitsandbytes>=0.41.0",
    "pyyaml>=6.0",
    "boto3>=1.28.0",
    "tiktoken>=0.5.0",
    "transformers_stream_generator>=0.0.4"
])

import json
from datetime import datetime

sys.path.insert(0, '/opt/ml/processing/input/repo/src')

from cc_eval.secrets import setup_hf_auth
from cc_eval.config import default_refusal_phrases
from cc_eval.prompts import load_yaml_items
from cc_eval.load_model import load_hf_model
from cc_eval.generate import generate_outputs, write_jsonl
from cc_eval.metrics import compute_metrics, write_report
import torch
import gc

# Setup HF auth
setup_hf_auth()

def main():
    # Get config from environment
    MODEL_PATH = os.environ.get("MODEL_PATH")
    MODEL_NAME = os.environ.get("MODEL_NAME")
    SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", "You are a helpful assistant.")
    USE_QUANTIZATION = os.environ.get("USE_QUANTIZATION", "true").lower() == "true"
    
    CODE_DIR = "/opt/ml/processing/input/repo"
    OUTPUT_DIR = "/opt/ml/processing/output"
    
    SYCO_EVAL = f"{CODE_DIR}/evals/sycophancy_set_500.yaml"
    BORDER_EVAL = f"{CODE_DIR}/evals/borderline_safety_set.yaml"
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"RUNNING: {MODEL_NAME}")
    print(f"{'='*60}")
    print(f"Model: {MODEL_PATH}")
    print(f"Quantization: {USE_QUANTIZATION}")
    print(f"{'='*60}\n")
    
    # Load model
    print(f"Loading model...")
    tok, mdl = load_hf_model(MODEL_PATH, use_quantization=USE_QUANTIZATION)
    
    # Run sycophancy eval
    print(f"Running sycophancy eval (500 prompts)...")
    items = load_yaml_items(SYCO_EVAL)
    prompts = [{"id": it.id, "category": it.category, "expected": it.expected, "prompt": it.prompt} for it in items]
    rows = generate_outputs(tok, mdl, prompts, max_new_tokens=256, temperature=0.2, top_p=0.95, seed=1, system_prompt=SYSTEM_PROMPT)
    
    syc_jsonl = f"{OUTPUT_DIR}/sycophancy.{MODEL_NAME}.seed1.jsonl"
    write_jsonl(syc_jsonl, rows)
    
    syc_metrics = compute_metrics(rows, refusal_phrases=default_refusal_phrases())
    write_report(f"{OUTPUT_DIR}/sycophancy.{MODEL_NAME}.seed1.metrics.json", syc_metrics)
    
    # Run borderline eval
    print(f"Running borderline eval (50 prompts)...")
    items = load_yaml_items(BORDER_EVAL)
    prompts = [{"id": it.id, "category": it.category, "expected": it.expected, "prompt": it.prompt} for it in items]
    rows = generate_outputs(tok, mdl, prompts, max_new_tokens=256, temperature=0.2, top_p=0.95, seed=1, system_prompt=SYSTEM_PROMPT)
    
    bor_jsonl = f"{OUTPUT_DIR}/borderline.{MODEL_NAME}.seed1.jsonl"
    write_jsonl(bor_jsonl, rows)
    
    bor_metrics = compute_metrics(rows, refusal_phrases=default_refusal_phrases())
    write_report(f"{OUTPUT_DIR}/borderline.{MODEL_NAME}.seed1.metrics.json", bor_metrics)
    
    # Save summary
    summary = {
        "model": MODEL_PATH,
        "model_name": MODEL_NAME,
        "sycophancy_rate_broad": syc_metrics["sycophancy_rate_broad"],
        "refusal_rate": bor_metrics["refusal_rate"],
        "label_distribution": syc_metrics["label_distribution"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(f"{OUTPUT_DIR}/summary.{MODEL_NAME}.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ {MODEL_NAME} COMPLETE")
    print(f"{'='*60}")
    print(f"Sycophancy rate: {syc_metrics['sycophancy_rate_broad']:.1%}")
    print(f"Refusal rate: {bor_metrics['refusal_rate']:.1%}")
    print(f"Label distribution: {syc_metrics['label_distribution']}")

if __name__ == "__main__":
    main()
