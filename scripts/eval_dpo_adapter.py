#!/usr/bin/env python3
"""
Evaluate DPO-trained adapter on sycophancy dataset.
Modified version of processing_job_single.py for adapter evaluation.
"""
import os
import sys
import json
import subprocess

# Install dependencies FIRST before any imports that depend on them
print("Installing dependencies...")
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "-q",
    "typing_extensions>=4.8.0",  # Fix TypeIs import error
    "transformers>=4.36.0",
    "peft>=0.6.0",
    "bitsandbytes>=0.41.0",
    "accelerate>=0.24.0",
    "pyyaml"
])

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

# Add repo to path
sys.path.insert(0, '/opt/ml/processing/input/repo')

from src.cc_eval.generate import generate_outputs, write_jsonl
from src.cc_eval.judge import taxonomy_judge, Judgement
from src.cc_eval.metrics import compute_metrics, default_refusal_phrases, write_report
from src.cc_eval.prompts import load_yaml_items

# Environment variables
BASE_MODEL = os.environ.get("BASE_MODEL", "mistralai/Mistral-7B-v0.1")
ADAPTER_PATH = os.environ.get("ADAPTER_PATH")  # S3 path to adapter
ADAPTER_TYPE = os.environ.get("ADAPTER_TYPE", "sharp")
SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", "You are a helpful assistant.")
OUTPUT_DIR = "/opt/ml/processing/output"

print(f"Evaluating {ADAPTER_TYPE} adapter")
print(f"Base model: {BASE_MODEL}")
print(f"Adapter: {ADAPTER_PATH}")

# Load base model with 4-bit quantization
print("Loading base model...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# Load adapter
print(f"Loading {ADAPTER_TYPE} adapter...")
model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model = model.merge_and_unload()  # Merge for inference

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token

# Load eval sets
print("Loading evaluation sets...")
syco_items = load_yaml_items("/opt/ml/processing/input/repo/evals/sycophancy_set_500.yaml")
border_items = load_yaml_items("/opt/ml/processing/input/repo/evals/borderline_safety_set.yaml")

# Convert to dict format for generate_outputs
syco_prompts = [{"id": it.id, "category": it.category, "expected": it.expected, "prompt": it.prompt} for it in syco_items]
border_prompts = [{"id": it.id, "category": it.category, "expected": it.expected, "prompt": it.prompt} for it in border_items]

# Generate responses
print(f"Generating responses for {len(syco_prompts)} sycophancy prompts...")
syco_rows = generate_outputs(
    tokenizer,
    model, 
    syco_prompts,
    max_new_tokens=256,
    temperature=0.2,
    top_p=0.95,
    seed=1,
    system_prompt=SYSTEM_PROMPT
)

print(f"Generating responses for {len(border_prompts)} borderline prompts...")
border_rows = generate_outputs(
    tokenizer,
    model,
    border_prompts,
    max_new_tokens=256,
    temperature=0.2,
    top_p=0.95,
    seed=1,
    system_prompt=SYSTEM_PROMPT
)

# Compute metrics
print("Computing metrics...")
syco_metrics = compute_metrics(syco_rows, refusal_phrases=default_refusal_phrases())
border_metrics = compute_metrics(border_rows, refusal_phrases=default_refusal_phrases())

# Save results
print("Saving results...")
os.makedirs(OUTPUT_DIR, exist_ok=True)

write_jsonl(f"{OUTPUT_DIR}/sycophancy.{ADAPTER_TYPE}.seed1.jsonl", syco_rows)
write_jsonl(f"{OUTPUT_DIR}/borderline.{ADAPTER_TYPE}.seed1.jsonl", border_rows)
write_report(f"{OUTPUT_DIR}/sycophancy.{ADAPTER_TYPE}.seed1.metrics.json", syco_metrics)
write_report(f"{OUTPUT_DIR}/borderline.{ADAPTER_TYPE}.seed1.metrics.json", border_metrics)

# Summary
summary = {
    "adapter_type": ADAPTER_TYPE,
    "base_model": BASE_MODEL,
    "sycophancy_metrics": syco_metrics,
    "borderline_metrics": border_metrics
}

with open(f"{OUTPUT_DIR}/summary.{ADAPTER_TYPE}.json", 'w') as f:
    json.dump(summary, f, indent=2)

print("\n" + "="*60)
print(f"✅ {ADAPTER_TYPE.upper()} ADAPTER EVALUATION COMPLETE")
print("="*60)
print(f"Sycophancy rate: {syco_metrics.get('sycophancy_rate_broad', 0):.1%}")
print(f"S1 count: {syco_metrics.get('label_distribution', {}).get('S1', 0)}")
print(f"S2 count: {syco_metrics.get('label_distribution', {}).get('S2', 0)}")
print(f"Refusal rate: {syco_metrics.get('refusal_rate', 0):.1%}")
print("="*60)
