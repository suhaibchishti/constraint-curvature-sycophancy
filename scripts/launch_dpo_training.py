#!/usr/bin/env python3
"""
Launch parallel DPO training jobs for sharp and smooth adapters.
"""
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from datetime import datetime

# Configuration
ROLE = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
BUCKET = "cc-eval-500330120558-us-east-1"
INSTANCE_TYPE = "ml.g5.xlarge"
BASE_MODEL = "mistralai/Mistral-7B-v0.1"

timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

def launch_training_job(adapter_type):
    """Launch DPO training job for sharp or smooth adapter"""
    
    processor = ScriptProcessor(
        role=ROLE,
        image_uri=f"763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.0.0-gpu-py310",
        command=["python3"],
        instance_type=INSTANCE_TYPE,
        instance_count=1,
        base_job_name=f"dpo-{adapter_type}",
        volume_size_in_gb=50,  # Larger for model + training
        max_runtime_in_seconds=14400,  # 4 hours
        env={
            "MODEL_PATH": BASE_MODEL,
            "ADAPTER_TYPE": adapter_type,
            "OUTPUT_DIR": "/opt/ml/processing/output"
        }
    )
    
    output_path = f"s3://{BUCKET}/dpo_adapters/{timestamp}/{adapter_type}"
    
    print(f"Launching {adapter_type} adapter training...")
    print(f"  Base model: {BASE_MODEL}")
    print(f"  Output: {output_path}")
    
    processor.run(
        code="scripts/train_dpo.py",
        inputs=[
            ProcessingInput(
                source=".",
                destination="/opt/ml/processing/input/repo",
                input_name="repo"
            ),
            ProcessingInput(
                source=f"s3://{BUCKET}/data/dpo_preferences_50pairs.json",
                destination="/opt/ml/processing/input/data",
                input_name="data"
            )
        ],
        outputs=[
            ProcessingOutput(
                output_name="adapter",
                source="/opt/ml/processing/output",
                destination=output_path
            )
        ],
        wait=False,
        logs=False
    )
    
    return processor.latest_job.name

# Upload dataset to S3
print("Uploading dataset to S3...")
s3 = boto3.client('s3')
s3.upload_file(
    'data/dpo_preferences_50pairs.json',
    BUCKET,
    'data/dpo_preferences_50pairs.json'
)
print("✅ Dataset uploaded")

# Launch both training jobs
print("\n" + "="*60)
print("LAUNCHING PARALLEL DPO TRAINING JOBS")
print("="*60)

job_sharp = launch_training_job("sharp")
job_smooth = launch_training_job("smooth")

print("\n" + "="*60)
print("✅ Both training jobs launched!")
print("="*60)
print(f"Sharp adapter: {job_sharp}")
print(f"Smooth adapter: {job_smooth}")
print(f"\nAdapters will be saved to: s3://{BUCKET}/dpo_adapters/{timestamp}/")
print("\nMonitor at:")
print(f"  https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/processing-jobs")
print(f"\nExpected completion: ~2-3 hours")
print(f"Cost: ~$8-12 total")
