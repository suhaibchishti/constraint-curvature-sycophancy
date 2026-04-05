#!/usr/bin/env python3
"""
Phase 4: Deploy TGI endpoint for one 70B model.

Usage:
    python scripts/phase4_deploy_endpoint.py --model llama
    python scripts/phase4_deploy_endpoint.py --model qwen
"""
import argparse, boto3, json, os, time
from sagemaker.huggingface import HuggingFaceModel
import sagemaker

ROLE   = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

BUCKET_BY_REGION = {
    "us-east-1": "cc-eval-500330120558-us-east-1",
    "us-west-2": "sagemaker-us-west-2-500330120558",
}

MODELS = {
    "llama": {
        "model_id":      "meta-llama/Llama-3.1-70B-Instruct",
        "endpoint_name": "phase4-llama-70b",
        "s3_prefix":     "models/llama3.1-70b",
    },
    "qwen": {
        "model_id":      "Qwen/Qwen2.5-72B-Instruct",
        "endpoint_name": "phase4-qwen-72b",
        "s3_prefix":     "models/qwen2.5-72b",
    },
}

def get_hf_token():
    if os.environ.get("HF_TOKEN"):
        return os.environ["HF_TOKEN"]
    client = boto3.client("secretsmanager", region_name="us-east-1")  # secrets always in us-east-1
    secret = json.loads(client.get_secret_value(SecretId="cc-eval-hf-token")["SecretString"])
    return secret["HF_TOKEN"]


def deploy(model_key, from_s3=False):
    cfg = MODELS[model_key]
    token = get_hf_token()

    sess = sagemaker.Session(boto3.Session(region_name=REGION))

    hub = {
        "HF_MODEL_ID":                cfg["model_id"],
        "HF_TASK":                    "text-generation",
        "SM_NUM_GPUS":                "8",
        "MAX_INPUT_LENGTH":           "2048",
        "MAX_TOTAL_TOKENS":           "2560",
        "MAX_BATCH_PREFILL_TOKENS":   "4096",
        "HUGGING_FACE_HUB_TOKEN":     token,
        "TRUST_REMOTE_CODE":          "true",
    }

    model_kwargs = dict(
        image_uri=sagemaker.image_uris.retrieve(
            "huggingface-llm", REGION,
            version="2.2.0",
            instance_type="ml.g5.48xlarge",
        ),
        env=hub,
        role=ROLE,
        sagemaker_session=sess,
    )

    if from_s3:
        bucket = BUCKET_BY_REGION.get(REGION, f"sagemaker-{REGION}-500330120558")
        s3_uri = f"s3://{bucket}/{cfg['s3_prefix']}/"
        model_kwargs["model_data"] = s3_uri
        print(f"Using S3 weights: {s3_uri}")
    else:
        print(f"Downloading from HuggingFace (slow on fresh instance)")

    model = HuggingFaceModel(**model_kwargs)

    print(f"Deploying {cfg['model_id']} → endpoint: {cfg['endpoint_name']}")
    print("This takes ~10-15 minutes...")

    # Clean up any stale endpoint and config from previous failed attempts
    sm = boto3.client("sagemaker", region_name=REGION)
    for delete_fn, name in [
        (sm.delete_endpoint,        cfg["endpoint_name"]),
        (sm.delete_endpoint_config, cfg["endpoint_name"]),
    ]:
        try:
            delete_fn(**({
                "EndpointName" if "endpoint_config" not in delete_fn.__name__ else "EndpointConfigName": name
            }))
            print(f"  Cleaned up stale {delete_fn.__name__.replace('delete_', '')}: {name}")
        except Exception:
            pass

    predictor = model.deploy(
        initial_instance_count=1,
        instance_type="ml.g5.48xlarge",
        endpoint_name=cfg["endpoint_name"],
        container_startup_health_check_timeout=3600,  # 1hr max — covers download + shard loading on fresh instance
    )

    print(f"\n✅ Endpoint ready: {cfg['endpoint_name']}")
    print(f"Run: python scripts/phase4_generate.py --model {model_key}")
    return predictor


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=["llama", "qwen"])
    parser.add_argument("--from-s3", action="store_true", help="Use pre-downloaded S3 weights")
    args = parser.parse_args()
    deploy(args.model, from_s3=args.from_s3)
