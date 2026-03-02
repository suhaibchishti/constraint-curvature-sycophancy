#!/usr/bin/env python3
"""
SageMaker Processing Job for constraint-curvature evaluation.
Runs eval pipeline and uploads results to S3.
"""
import os
import sys
import subprocess

# Install dependencies
print("Installing dependencies...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
    "transformers>=4.36.0",
    "accelerate>=0.25.0", 
    "bitsandbytes>=0.41.0",
    "pyyaml>=6.0",
    "boto3>=1.28.0"
])
print("Dependencies installed")

import json
from datetime import datetime

# Add src to path
sys.path.insert(0, '/opt/ml/processing/input/repo/src')

from cc_eval.secrets import setup_hf_auth
from cc_eval.config import default_refusal_phrases
from cc_eval.prompts import load_yaml_items
from cc_eval.load_model import load_hf_model
from cc_eval.generate import generate_outputs, write_jsonl
from cc_eval.metrics import compute_metrics, write_report
from cc_eval.gate import gate, GateThresholds
import torch
import gc

# Setup HuggingFace authentication
setup_hf_auth()

def run_eval(model_name, model_path, eval_path, out_prefix, use_quantization=True, system_prompt=None):
    print(f"\n{'='*60}")
    print(f"Running {model_name} on {eval_path}")
    print(f"{'='*60}")
    
    items = load_yaml_items(eval_path)
    prompts = [{"id": it.id, "category": it.category, "expected": it.expected, "prompt": it.prompt} for it in items]
    
    print(f"Loading model: {model_path}")
    tok, mdl = load_hf_model(model_path, use_quantization=use_quantization)
    
    print(f"Generating {len(prompts)} completions...")
    rows = generate_outputs(tok, mdl, prompts, max_new_tokens=256, temperature=0.2, top_p=0.95, seed=1, system_prompt=system_prompt)
    
    out_jsonl = f"{out_prefix}.{model_name}.seed1.jsonl"
    write_jsonl(out_jsonl, rows)
    print(f"Saved outputs to {out_jsonl}")
    
    m = compute_metrics(rows, refusal_phrases=default_refusal_phrases())
    write_report(f"{out_prefix}.{model_name}.seed1.metrics.json", m)
    
    # Clean up
    del mdl, tok
    gc.collect()
    torch.cuda.empty_cache()
    
    return m

def main():
    # Configuration
    MODEL_A_PATH = os.environ.get("MODEL_A_PATH", "meta-llama/Llama-2-7b-chat-hf")
    MODEL_B_PATH = os.environ.get("MODEL_B_PATH", "meta-llama/Meta-Llama-3-8B-Instruct")
    SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", "You are a helpful assistant.")
    USE_QUANTIZATION = os.environ.get("USE_QUANTIZATION", "true").lower() == "true"
    
    # Paths
    CODE_DIR = "/opt/ml/processing/input/repo"
    OUTPUT_DIR = "/opt/ml/processing/output"
    
    SYCO_EVAL = f"{CODE_DIR}/evals/sycophancy_set_500.yaml"
    BORDER_EVAL = f"{CODE_DIR}/evals/borderline_safety_set.yaml"
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\n{'='*60}")
    print("CONFIGURATION")
    print(f"{'='*60}")
    print(f"Model A: {MODEL_A_PATH}")
    print(f"Model B: {MODEL_B_PATH}")
    print(f"System Prompt: {SYSTEM_PROMPT}")
    print(f"Quantization: {USE_QUANTIZATION}")
    print(f"{'='*60}\n")
    
    # Run sycophancy eval
    prefix_syc = os.path.join(OUTPUT_DIR, "sycophancy")
    mA_syc = run_eval("A", MODEL_A_PATH, SYCO_EVAL, prefix_syc, USE_QUANTIZATION, SYSTEM_PROMPT)
    mB_syc = run_eval("B", MODEL_B_PATH, SYCO_EVAL, prefix_syc, USE_QUANTIZATION, SYSTEM_PROMPT)
    
    # Run borderline safety eval
    prefix_bor = os.path.join(OUTPUT_DIR, "borderline")
    mA_bor = run_eval("A", MODEL_A_PATH, BORDER_EVAL, prefix_bor, USE_QUANTIZATION, SYSTEM_PROMPT)
    mB_bor = run_eval("B", MODEL_B_PATH, BORDER_EVAL, prefix_bor, USE_QUANTIZATION, SYSTEM_PROMPT)
    
    # Gate check
    gate_input_A = {"sycophancy_rate_broad": mA_syc["sycophancy_rate_broad"], "refusal_rate": mA_bor["refusal_rate"]}
    gate_input_B = {"sycophancy_rate_broad": mB_syc["sycophancy_rate_broad"], "refusal_rate": mB_bor["refusal_rate"]}
    
    ok, msgs = gate(gate_input_A, gate_input_B, GateThresholds())
    
    summary = {
        "model_a": gate_input_A,
        "model_b": gate_input_B,
        "gate_ok": ok,
        "messages": msgs,
        "label_distribution_a": mA_syc["label_distribution"],
        "label_distribution_b": mB_syc["label_distribution"],
        "timestamp": datetime.now().isoformat(),
        "config": {
            "model_a_path": MODEL_A_PATH,
            "model_b_path": MODEL_B_PATH,
            "system_prompt": SYSTEM_PROMPT,
            "quantization": USE_QUANTIZATION
        }
    }
    
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*60)
    print("GATE RESULTS")
    print("="*60)
    for msg in msgs:
        print(msg)
    print("="*60)
    print(f"Overall: {'✅ PASS' if ok else '❌ FAIL'}")
    print("\nLabel Distribution:")
    print(f"Model A: {mA_syc['label_distribution']}")
    print(f"Model B: {mB_syc['label_distribution']}")
    print("="*60)

if __name__ == "__main__":
    main()
