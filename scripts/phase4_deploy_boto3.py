#!/usr/bin/env python3
import argparse, boto3, json, os

REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
ROLE = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
IMAGE_URI = f"763104351884.dkr.ecr.{REGION}.amazonaws.com/huggingface-pytorch-tgi-inference:2.2.0-tgi2.2.0-gpu-py310-cu122-ubuntu22.04"

BUCKET_BY_REGION = {
    "us-east-1": "cc-eval-500330120558-us-east-1",
    "us-west-2": "sagemaker-us-west-2-500330120558",
}

MODELS = {
    "llama": {"model_id": "meta-llama/Llama-3.1-70B-Instruct", "ep_name": "phase4-llama-70b", "prefix": "models/llama3.1-70b"},
    "qwen":  {"model_id": "Qwen/Qwen2.5-72B-Instruct", "ep_name": "phase4-qwen-72b", "prefix": "models/qwen2.5-72b"},
}

def get_hf_token():
    # Secret is always in us-east-1, regardless of where cluster is deployed
    client = boto3.client("secretsmanager", region_name="us-east-1")
    return json.loads(client.get_secret_value(SecretId="cc-eval-hf-token")["SecretString"])["HF_TOKEN"]

def deploy(model_key, from_s3=False):
    cfg = MODELS[model_key]
    sm = boto3.client("sagemaker", region_name=REGION)
    
    env = {
        "HF_MODEL_ID": cfg["model_id"],
        "HF_TASK": "text-generation",
        "SM_NUM_GPUS": "8",
        "MAX_INPUT_LENGTH": "2048",
        "MAX_TOTAL_TOKENS": "2560",
        "MAX_BATCH_PREFILL_TOKENS": "4096",
        "HUGGING_FACE_HUB_TOKEN": get_hf_token(),
    }
    
    container_def = {"Image": IMAGE_URI, "Environment": env}

    if from_s3:
        bucket = BUCKET_BY_REGION.get(REGION, f"sagemaker-{REGION}-500330120558")
        s3_uri = f"s3://{bucket}/{cfg['prefix']}/"
        print(f"Using S3 weights: {s3_uri}")
        # THIS is the magic API dictionary that the SDK was failing to build
        container_def["ModelDataSource"] = {
            "S3DataSource": {
                "S3Uri": s3_uri,
                "S3DataType": "S3Prefix",
                "CompressionType": "None"
            }
        }
    
    print(f"Creating Model: {cfg['ep_name']}...")
    try: sm.delete_model(ModelName=cfg['ep_name'])
    except Exception: pass
    
    sm.create_model(
        ModelName=cfg["ep_name"],
        ExecutionRoleArn=ROLE,
        PrimaryContainer=container_def
    )
    
    print("Creating Endpoint Config...")
    try: sm.delete_endpoint_config(EndpointConfigName=cfg['ep_name'])
    except Exception: pass
    
    sm.create_endpoint_config(
        EndpointConfigName=cfg["ep_name"],
        ProductionVariants=[{
            "VariantName": "AllTraffic",
            "ModelName": cfg["ep_name"],
            "InitialInstanceCount": 1,
            "InstanceType": "ml.g5.48xlarge",
            "InitialVariantWeight": 1.0,
            "ContainerStartupHealthCheckTimeoutInSeconds": 900
        }]
    )
    
    print("Creating Endpoint (takes ~10-15 mins)...")
    try: sm.delete_endpoint(EndpointName=cfg['ep_name'])
    except Exception: pass
    
    sm.create_endpoint(
        EndpointName=cfg["ep_name"],
        EndpointConfigName=cfg["ep_name"]
    )
    print(f"\n✅ Created. Monitor deployment progress in AWS SageMaker console!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=["llama", "qwen"])
    parser.add_argument("--from-s3", action="store_true")
    args = parser.parse_args()
    deploy(args.model, from_s3=args.from_s3)
