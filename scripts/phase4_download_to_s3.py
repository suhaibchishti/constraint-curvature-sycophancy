#!/usr/bin/env python3
"""
Phase 4: Download model weights from HuggingFace to S3.
Run once before deploying — eliminates the HF download bottleneck at endpoint startup.

Usage:
    python scripts/phase4_download_to_s3.py --model qwen
    python scripts/phase4_download_to_s3.py --model llama
"""
import argparse, boto3, json, os
from pathlib import Path
from huggingface_hub import snapshot_download

BUCKET = "cc-eval-500330120558-us-east-1"
REGION = "us-east-1"

MODELS = {
    "qwen":  {"model_id": "Qwen/Qwen2.5-72B-Instruct",          "s3_prefix": "models/qwen2.5-72b"},
    "llama": {"model_id": "meta-llama/Llama-3.1-70B-Instruct",   "s3_prefix": "models/llama3.1-70b"},
}


def get_hf_token():
    if os.environ.get("HF_TOKEN"):
        return os.environ["HF_TOKEN"]
    client = boto3.client("secretsmanager", region_name=REGION)
    secret = json.loads(client.get_secret_value(SecretId="cc-eval-hf-token")["SecretString"])
    return secret["HF_TOKEN"]


def main(model_key):
    cfg = MODELS[model_key]
    token = get_hf_token()
    local_dir = f"/tmp/{model_key}_weights"

    print(f"Downloading {cfg['model_id']} → {local_dir}")
    local_path = snapshot_download(
        cfg["model_id"],
        local_dir=local_dir,
        token=token,
        ignore_patterns=["*.msgpack", "*.h5", "flax_model*", "tf_model*"],
    )
    print(f"Download complete: {local_path}")

    s3 = boto3.client("s3", region_name=REGION)
    files = list(Path(local_path).rglob("*"))
    files = [f for f in files if f.is_file()]
    print(f"Uploading {len(files)} files to s3://{BUCKET}/{cfg['s3_prefix']}/")

    for i, local_file in enumerate(files):
        s3_key = f"{cfg['s3_prefix']}/{local_file.relative_to(local_path)}"
        s3.upload_file(str(local_file), BUCKET, s3_key)
        if (i + 1) % 5 == 0 or (i + 1) == len(files):
            print(f"  {i+1}/{len(files)} uploaded")

    s3_uri = f"s3://{BUCKET}/{cfg['s3_prefix']}/"
    print(f"\n✅ Done. Model at: {s3_uri}")
    print(f"Deploy with: python scripts/phase4_deploy_endpoint.py --model {model_key} --from-s3")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=["llama", "qwen"])
    args = parser.parse_args()
    main(args.model)
