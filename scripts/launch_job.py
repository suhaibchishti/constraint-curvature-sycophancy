#!/usr/bin/env python3
"""
Launch SageMaker Processing Job for evaluation.
Run from SageMaker notebook or local with AWS credentials.
"""
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from datetime import datetime

# Configuration
ROLE = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role"  # Update if needed
BUCKET = "cc-eval-500330120558-us-east-1"
INSTANCE_TYPE = "ml.g5.xlarge"
INSTANCE_COUNT = 1

# Model configuration
MODEL_A = "meta-llama/Llama-2-7b-chat-hf"
MODEL_B = "meta-llama/Meta-Llama-3-8B-Instruct"
SYSTEM_PROMPT = "You are a helpful assistant."

# Create processor
processor = ScriptProcessor(
    role=ROLE,
    image_uri=f"763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.0.0-gpu-py310",
    instance_type=INSTANCE_TYPE,
    instance_count=INSTANCE_COUNT,
    base_job_name="cc-eval",
    volume_size_in_gb=30,
    max_runtime_in_seconds=14400,  # 4 hours
    env={
        "MODEL_A_PATH": MODEL_A,
        "MODEL_B_PATH": MODEL_B,
        "SYSTEM_PROMPT": SYSTEM_PROMPT,
        "USE_QUANTIZATION": "true"
    }
)

# Timestamp for output
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
output_path = f"s3://{BUCKET}/artifacts/{timestamp}"

print(f"Launching processing job...")
print(f"Model A: {MODEL_A}")
print(f"Model B: {MODEL_B}")
print(f"Output: {output_path}")

# Run processing job
processor.run(
    code="scripts/processing_job.py",
    source_dir=".",  # Upload entire repo
    outputs=[
        ProcessingOutput(
            output_name="results",
            source="/opt/ml/processing/output",
            destination=output_path
        )
    ],
    wait=False,  # Don't block - job runs in background
    logs=True
)

print(f"\n✅ Job launched!")
print(f"Monitor at: https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/processing-jobs")
print(f"Results will be at: {output_path}")
