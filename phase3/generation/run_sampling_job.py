#!/usr/bin/env python3
"""
Launch SageMaker Processing Job for Phase 3 Behavioral Distributions.
Runs 10 samples at 3 temperatures across 6 models.
"""
import argparse
import json
import boto3
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from datetime import datetime

# Configuration
ROLE = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
BUCKET = "cc-eval-500330120558-us-east-1"
INSTANCE_TYPE = "ml.g5.xlarge"
INSTANCE_COUNT = 1

MODELS = [
    "Qwen/Qwen1.5-7B-Chat",
    "Qwen/Qwen2.5-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct"
]

def get_secret():
    client = boto3.client('secretsmanager', region_name='us-east-1')
    try:
        response = client.get_secret_value(SecretId='cc-eval-hf-token')
        secret = json.loads(response['SecretString'])
        return secret['HF_TOKEN']
    except Exception as e:
        print(f"Failed to fetch HF token from Secrets Manager: {e}")
        return "YOUR_HF_TOKEN"

def launch_job(model_name):
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    clean_model_name = model_name.split('/')[-1]
    job_name = f"phase3-{clean_model_name.lower().replace('.', '-')}-{timestamp}"[:63]
    output_path = f"s3://{BUCKET}/phase3/{job_name}"
    
    hf_token = get_secret()

    processor = ScriptProcessor(
        role=ROLE,
        image_uri="763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.0.0-gpu-py310",
        command=["python3"],
        instance_type=INSTANCE_TYPE,
        instance_count=INSTANCE_COUNT,
        base_job_name="p3-dist",
        volume_size_in_gb=30,
        max_runtime_in_seconds=43200,  # 12 hours
        env={
            "MODEL_PATH": model_name,
            "USE_QUANTIZATION": "true",
            "HF_TOKEN": hf_token
        }
    )

    print(f"Launching Phase 3 sampling job for {model_name}...")
    
    processor.run(
        code="phase3/generation/run_sampling.py",
        inputs=[
            ProcessingInput(
                source=".",
                destination="/opt/ml/processing/input/repo",
                input_name="repo"
            )
        ],
        outputs=[
            ProcessingOutput(
                output_name="results",
                source="/opt/ml/processing/output",
                destination=output_path,
                s3_upload_mode="Continuous"
            )
        ],
        wait=False,
        logs=False
    )
    print(f"✅ Job launched: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, choices=MODELS + ["all"], default="all")
    args = parser.parse_args()

    if args.model == "all":
        for m in MODELS:
            launch_job(m)
    else:
        launch_job(args.model)
