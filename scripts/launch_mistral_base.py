#!/usr/bin/env python3
"""
Test Mistral-7B-v0.1 base model (no instruct tuning) to establish pre-DPO baseline.
This shows the sycophancy rate before any alignment training.
"""
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from datetime import datetime

# Configuration
ROLE = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
BUCKET = "cc-eval-500330120558-us-east-1"
INSTANCE_TYPE = "ml.g5.xlarge"

# Model - Base model with no instruct tuning
MODEL = "mistralai/Mistral-7B-v0.1"
MODEL_NAME = "mistral-base"
SYSTEM_PROMPT = "You are a helpful assistant."

timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

processor = ScriptProcessor(
    role=ROLE,
    image_uri=f"763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.0.0-gpu-py310",
    command=["python3"],
    instance_type=INSTANCE_TYPE,
    instance_count=1,
    base_job_name=f"mistral-{MODEL_NAME}",
    volume_size_in_gb=30,
    max_runtime_in_seconds=21600,  # 6 hours buffer
    env={
        "MODEL_PATH": MODEL,
        "MODEL_NAME": MODEL_NAME,
        "SYSTEM_PROMPT": SYSTEM_PROMPT,
        "USE_QUANTIZATION": "true"
    }
)

output_path = f"s3://{BUCKET}/artifacts/{timestamp}/{MODEL_NAME}"

print("="*60)
print("LAUNCHING MISTRAL BASE MODEL BASELINE")
print("="*60)
print(f"Model: {MODEL}")
print(f"Output: {output_path}")
print(f"\nExpected: >5% sycophancy (no alignment training)")
print("This establishes the pre-DPO baseline.")
print("="*60)

processor.run(
    code="scripts/processing_job_single.py",
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
            destination=output_path
        )
    ],
    wait=False,
    logs=False
)

print(f"\n✅ Job launched: {processor.latest_job.name}")
print(f"\nMonitor at:")
print(f"  https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/processing-jobs")
print(f"\nExpected completion: ~1.5 hours")
