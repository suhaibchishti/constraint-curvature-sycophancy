#!/usr/bin/env python3
"""
SageMaker Processing Job for framing ablation (single model).
Reads MODEL_PATH and MODEL_NAME from environment.
"""
import os, sys, subprocess

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
from cc_eval.prompts import load_yaml_items
from cc_eval.load_model import load_hf_model
from cc_eval.generate import generate_outputs, write_jsonl

setup_hf_auth()

def main():
    MODEL_PATH = os.environ.get("MODEL_PATH")
    MODEL_NAME = os.environ.get("MODEL_NAME")
    SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", "You are a helpful assistant.")
    USE_QUANTIZATION = os.environ.get("USE_QUANTIZATION", "true").lower() == "true"

    CODE_DIR = "/opt/ml/processing/input/repo"
    OUTPUT_DIR = "/opt/ml/processing/output"
    EVAL_PATH = f"{CODE_DIR}/evals/framing_ablation_neutral.yaml"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"FRAMING ABLATION: {MODEL_NAME}")
    print(f"Model: {MODEL_PATH}")
    print(f"{'='*60}\n")

    items = load_yaml_items(EVAL_PATH)
    prompts = [{"id": it.id, "category": it.category, "expected": it.expected, "prompt": it.prompt} for it in items]
    print(f"Loaded {len(prompts)} neutral prompts")

    tok, mdl = load_hf_model(MODEL_PATH, use_quantization=USE_QUANTIZATION)
    rows = generate_outputs(tok, mdl, prompts,
                            max_new_tokens=512, temperature=0.7,
                            top_p=0.95, seed=1,
                            system_prompt=SYSTEM_PROMPT)

    out_file = f"{OUTPUT_DIR}/ablation.{MODEL_NAME}.seed1.jsonl"
    write_jsonl(out_file, rows)

    summary = {
        "model": MODEL_PATH,
        "model_name": MODEL_NAME,
        "num_prompts": len(rows),
        "experiment": "framing_ablation",
        "timestamp": datetime.now().isoformat()
    }
    with open(f"{OUTPUT_DIR}/summary.{MODEL_NAME}.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ {MODEL_NAME} COMPLETE — {len(rows)} completions saved")

if __name__ == "__main__":
    main()
