#!/usr/bin/env python3
"""
Evaluate DPO-trained adapter on sycophancy dataset.
Modified version of processing_job_single.py for adapter evaluation.
"""
import os
import sys
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Add repo to path
sys.path.insert(0, '/opt/ml/processing/input/repo')

from src.cc_eval.generator import Generator
from src.cc_eval.judge import Judge
from src.cc_eval.metrics import compute_metrics
from src.cc_eval.loader import load_eval_set

# Environment variables
BASE_MODEL = os.environ.get("BASE_MODEL", "mistralai/Mistral-7B-v0.1")
ADAPTER_PATH = os.environ.get("ADAPTER_PATH")  # S3 path to adapter
ADAPTER_TYPE = os.environ.get("ADAPTER_TYPE", "sharp")
SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", "You are a helpful assistant.")
OUTPUT_DIR = "/opt/ml/processing/output"

print(f"Evaluating {ADAPTER_TYPE} adapter")
print(f"Base model: {BASE_MODEL}")
print(f"Adapter: {ADAPTER_PATH}")

# Load base model
print("Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    load_in_4bit=True,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

# Load adapter
print(f"Loading {ADAPTER_TYPE} adapter...")
model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model = model.merge_and_unload()  # Merge for inference

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token

# Initialize generator
generator = Generator(model, tokenizer, system_prompt=SYSTEM_PROMPT)

# Load eval sets
print("Loading evaluation sets...")
sycophancy_set = load_eval_set("/opt/ml/processing/input/repo/evals/sycophancy.yaml")
borderline_set = load_eval_set("/opt/ml/processing/input/repo/evals/borderline.yaml")

# Generate responses
print(f"Generating responses for {len(sycophancy_set)} sycophancy prompts...")
sycophancy_results = []
for i, item in enumerate(sycophancy_set):
    if i % 50 == 0:
        print(f"  Progress: {i}/{len(sycophancy_set)}")
    
    response = generator.generate(item["prompt"])
    sycophancy_results.append({
        "prompt": item["prompt"],
        "response": response,
        "metadata": item.get("metadata", {})
    })

print(f"Generating responses for {len(borderline_set)} borderline prompts...")
borderline_results = []
for i, item in enumerate(borderline_set):
    if i % 10 == 0:
        print(f"  Progress: {i}/{len(borderline_set)}")
    
    response = generator.generate(item["prompt"])
    borderline_results.append({
        "prompt": item["prompt"],
        "response": response,
        "metadata": item.get("metadata", {})
    })

# Judge responses
print("Judging sycophancy responses...")
judge = Judge()
for result in sycophancy_results:
    result["label"] = judge.judge_sycophancy(result["prompt"], result["response"])

print("Judging borderline responses...")
for result in borderline_results:
    result["label"] = judge.judge_borderline(result["prompt"], result["response"])

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
