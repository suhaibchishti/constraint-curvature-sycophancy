#!/usr/bin/env python3
"""
Launch Llama 3.1 only (Llama 3 already completed)
"""
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from datetime import datetime

# Configuration
ROLE = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
BUCKET = "cc-eval-500330120558-us-east-1"
INSTANCE_TYPE = "ml.g5.xlarge"

MODEL_B = "meta-llama/Meta-Llama-3.1-8B-Instruct"
SYSTEM_PROMPT = "You are a helpful assistant."

# Use same timestamp as Llama 3 for easy comparison
timestamp = "20260305-175534"

processor = ScriptProcessor(
    role=ROLE,
    image_uri=f"763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.0.0-gpu-py310",
    command=["python3"],
    instance_type=INSTANCE_TYPE,
    instance_count=1,
    base_job_name=f"llama-llama31-8b",
    volume_size_in_gb=30,
    max_runtime_in_seconds=21600,  # 6 hours
    env={
        "MODEL_PATH": MODEL_B,
        "MODEL_NAME": "llama31-8b",
        "SYSTEM_PROMPT": SYSTEM_PROMPT,
        "USE_QUANTIZATION": "true"
    }
)

output_path = f"s3://{BUCKET}/artifacts/{timestamp}/llama31-8b"

print("\n" + "="*60)
print("LAUNCHING LLAMA 3.1 8B")
print("="*60)
print(f"Model: {MODEL_B}")
print(f"Output: {output_path}")
print("="*60 + "\n")

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

print("\n✅ Job launched: " + processor.latest_job.name)
print(f"Results will be in: {output_path}")
print("="*60)
