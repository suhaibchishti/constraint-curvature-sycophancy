#!/usr/bin/env python3
"""
Phase 4: Deploy TGI endpoint for one 70B model.

Usage:
    python scripts/phase4_deploy_endpoint.py --model llama
    python scripts/phase4_deploy_endpoint.py --model qwen
"""
import argparse, boto3, json, time
from sagemaker.huggingface import HuggingFaceModel
import sagemaker

ROLE   = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
REGION = "us-east-1"

MODELS = {
    "llama": {
        "model_id":       "meta-llama/Llama-3.1-70B-Instruct",
        "endpoint_name":  "phase4-llama-70b",
    },
    "qwen": {
        "model_id":       "Qwen/Qwen2.5-72B-Instruct",
        "endpoint_name":  "phase4-qwen-72b",
    },
}

def get_hf_token():
    client = boto3.client("secretsmanager", region_name=REGION)
    secret = json.loads(client.get_secret_value(SecretId="cc-eval-hf-token")["SecretString"])
    return secret["HF_TOKEN"]


def deploy(model_key):
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
    }

    model = HuggingFaceModel(
        image_uri=sagemaker.image_uris.retrieve(
            "huggingface-llm", REGION,
            version="2.2.0",
            instance_type="ml.g5.48xlarge",
        ),
        env=hub,
        role=ROLE,
        sagemaker_session=sess,
    )

    print(f"Deploying {cfg['model_id']} → endpoint: {cfg['endpoint_name']}")
    print("This takes ~10-15 minutes...")

    predictor = model.deploy(
        initial_instance_count=1,
        instance_type="ml.g5.48xlarge",
        endpoint_name=cfg["endpoint_name"],
        container_startup_health_check_timeout=900,
    )

    print(f"\n✅ Endpoint ready: {cfg['endpoint_name']}")
    print(f"Run: python scripts/phase4_generate.py --model {model_key}")
    return predictor


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=["llama", "qwen"])
    args = parser.parse_args()
    deploy(args.model)
