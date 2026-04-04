#!/usr/bin/env python3
"""
Phase 4: Generate responses from a running TGI endpoint.

Usage:
    python scripts/phase4_generate.py --model llama
    python scripts/phase4_generate.py --model qwen
"""
import argparse, boto3, json, os, time
from pathlib import Path

REGION = "us-east-1"
PROMPTS_PATH = "phase3/data/prompt_variants.jsonl"
OUTPUT_DIR = "phase4/outputs"
SYSTEM_PROMPT = "You are a helpful assistant."

MODELS = {
    "llama": {
        "endpoint_name": "phase4-llama-70b",
        "model_path":    "meta-llama/Llama-3.1-70B-Instruct",
        "model_name":    "Llama-3.1-70B-Instruct",
    },
    "qwen": {
        "endpoint_name": "phase4-qwen-72b",
        "model_path":    "Qwen/Qwen2.5-72B-Instruct",
        "model_name":    "Qwen2.5-72B-Instruct",
    },
}

TEMPERATURES = [0.0, 0.7]
N_SAMPLES = 5


CHAT_TEMPLATES = {
    "llama": (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        "{system}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
        "{user}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    ),
    "qwen": (
        "<|im_start|>system\n{system}<|im_end|>\n"
        "<|im_start|>user\n{user}<|im_end|>\n"
        "<|im_start|>assistant\n"
    ),
}


def call_endpoint(client, endpoint_name, model_key, prompt, temperature, seed):
    chat_prompt = CHAT_TEMPLATES[model_key].format(
        system=SYSTEM_PROMPT, user=prompt
    )
    payload = {
        "inputs": chat_prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": max(temperature, 0.01),
            "do_sample": temperature > 0,
            "top_p": 0.95 if temperature > 0 else 1.0,
            "seed": seed,
            "return_full_text": False,
        }
    }
    resp = client.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=json.dumps(payload),
    )
    result = json.loads(resp["Body"].read())
    if isinstance(result, list):
        return result[0].get("generated_text", "").strip()
    return result.get("generated_text", "").strip()


def main(model_key):
    cfg = MODELS[model_key]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = f"{OUTPUT_DIR}/{cfg['model_name']}_completions.jsonl"

    # Resume from checkpoint if exists
    done_keys = set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            for line in f:
                d = json.loads(line)
                done_keys.add((d["fact_id"], d["framing"], d["temperature"], d["sample_idx"]))
        print(f"Resuming — {len(done_keys)} responses already done")

    variants = [json.loads(l) for l in open(PROMPTS_PATH)]
    client = boto3.client("sagemaker-runtime", region_name=REGION)

    total = len(variants) * len(TEMPERATURES) * N_SAMPLES
    done = 0
    errors = 0

    with open(out_path, "a") as f:
        for variant in variants:
            for temp in TEMPERATURES:
                n = 1 if temp == 0 else N_SAMPLES  # T=0 is deterministic
                for sample_idx in range(n):
                    key = (variant["fact_id"], variant["framing"], temp, sample_idx)
                    if key in done_keys:
                        done += 1
                        continue

                    try:
                        completion = call_endpoint(
                            client, cfg["endpoint_name"], model_key,
                            variant["prompt"], temp, 42 + sample_idx
                        )
                    except Exception as e:
                        print(f"  ⚠ Error: {e}")
                        completion = "[ERROR]"
                        errors += 1

                    row = {
                        "model":       cfg["model_path"],
                        "fact_id":     variant["fact_id"],
                        "framing":     variant["framing"],
                        "temperature": temp,
                        "sample_idx":  sample_idx,
                        "prompt":      variant["prompt"],
                        "completion":  completion,
                        "seed":        42 + sample_idx,
                    }
                    f.write(json.dumps(row) + "\n")
                    f.flush()
                    done += 1

                    if done % 50 == 0:
                        print(f"  {done}/{total} ({done/total*100:.0f}%) — {errors} errors")

    print(f"\n✅ Done. {done} responses saved to {out_path}")
    if errors:
        print(f"⚠ {errors} errors — check [ERROR] entries")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=["llama", "qwen"])
    args = parser.parse_args()
    main(args.model)
