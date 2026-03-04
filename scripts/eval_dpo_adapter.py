#!/usr/bin/env python3
"""
Evaluate DPO-trained adapter on sycophancy dataset.
Modified version of processing_job_single.py for adapter evaluation.
"""
import os
import sys
import json
import subprocess
import torch

# Install dependencies
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

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

# Add repo to path
sys.path.insert(0, '/opt/ml/processing/input/repo')

from src.cc_eval.generate import generate_outputs
from src.cc_eval.judge import taxonomy_judge
from src.cc_eval.metrics import compute_metrics
from src.cc_eval.loader import load_yaml_items

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
sycophancy_set = load_yaml_items("/opt/ml/processing/input/repo/evals/sycophancy_set_500.yaml")
borderline_set = load_yaml_items("/opt/ml/processing/input/repo/evals/borderline_set_50.yaml")

# Generate responses
print(f"Generating responses for {len(sycophancy_set)} sycophancy prompts...")
sycophancy_outputs = generate_outputs(
    model, 
    tokenizer, 
    sycophancy_set,
    system_prompt=SYSTEM_PROMPT
)

print(f"Generating responses for {len(borderline_set)} borderline prompts...")
borderline_outputs = generate_outputs(
    model,
    tokenizer,
    borderline_set,
    system_prompt=SYSTEM_PROMPT
)

# Judge responses
print("Judging sycophancy responses...")
sycophancy_results = taxonomy_judge(sycophancy_outputs, eval_type="sycophancy")

print("Judging borderline responses...")
borderline_results = taxonomy_judge(borderline_outputs, eval_type="borderline")

# Compute metrics
print("Computing metrics...")
syco_metrics = compute_metrics(sycophancy_results, eval_type="sycophancy")
border_metrics = compute_metrics(borderline_results, eval_type="borderline")

# Save results
print("Saving results...")
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(f"{OUTPUT_DIR}/sycophancy.{ADAPTER_TYPE}.seed1.jsonl", 'w') as f:
    for result in sycophancy_results:
        f.write(json.dumps(result) + '\n')

with open(f"{OUTPUT_DIR}/borderline.{ADAPTER_TYPE}.seed1.jsonl", 'w') as f:
    for result in borderline_results:
        f.write(json.dumps(result) + '\n')

with open(f"{OUTPUT_DIR}/sycophancy.{ADAPTER_TYPE}.seed1.metrics.json", 'w') as f:
    json.dump(syco_metrics, f, indent=2)

with open(f"{OUTPUT_DIR}/borderline.{ADAPTER_TYPE}.seed1.metrics.json", 'w') as f:
    json.dump(border_metrics, f, indent=2)

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
