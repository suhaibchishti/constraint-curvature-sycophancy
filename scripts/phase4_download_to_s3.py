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
    # Use SageMaker EBS volume as temp space — process one file at a time
    local_dir = f"/home/ec2-user/SageMaker/{model_key}_weights"
    os.makedirs(local_dir, exist_ok=True)

    from huggingface_hub import list_repo_files, hf_hub_download
    s3 = boto3.client("s3", region_name=REGION)

    # Get list of files to download
    files = [
        f for f in list_repo_files(cfg["model_id"], token=token)
        if not any(f.endswith(ext) for ext in [".msgpack", ".h5"])
        and not f.startswith("flax_model") and not f.startswith("tf_model")
    ]
    print(f"Found {len(files)} files to transfer for {cfg['model_id']}")

    for i, filename in enumerate(files):
        s3_key = f"{cfg['s3_prefix']}/{filename}"

        # Skip if already uploaded
        try:
            s3.head_object(Bucket=BUCKET, Key=s3_key)
            print(f"  [{i+1}/{len(files)}] Skipping (already in S3): {filename}")
            continue
        except Exception:
            pass

        # Download single file
        local_file = hf_hub_download(
            cfg["model_id"], filename,
            local_dir=local_dir,
            token=token,
        )

        # Upload to S3
        s3.upload_file(local_file, BUCKET, s3_key)
        print(f"  [{i+1}/{len(files)}] Uploaded: {filename}")

        # Delete local copy to free space
        os.remove(local_file)

    s3_uri = f"s3://{BUCKET}/{cfg['s3_prefix']}/"
    print(f"\n✅ Done. Model at: {s3_uri}")
    print(f"Deploy with: python scripts/phase4_deploy_endpoint.py --model {model_key} --from-s3")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=["llama", "qwen"])
    args = parser.parse_args()
    main(args.model)
