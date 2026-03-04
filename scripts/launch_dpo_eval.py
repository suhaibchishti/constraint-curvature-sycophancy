#!/usr/bin/env python3
"""
Launch parallel evaluation jobs for sharp and smooth DPO adapters.
"""
import sys
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from datetime import datetime

# Configuration
ROLE = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
BUCKET = "cc-eval-500330120558-us-east-1"
INSTANCE_TYPE = "ml.g5.xlarge"
BASE_MODEL = "mistralai/Mistral-7B-v0.1"
SYSTEM_PROMPT = "You are a helpful assistant."

# Adapter paths (pass as command line argument or env variable)
if len(sys.argv) > 1:
    ADAPTER_TIMESTAMP = sys.argv[1]
else:
    import os
    ADAPTER_TIMESTAMP = os.environ.get("ADAPTER_TIMESTAMP")
    if not ADAPTER_TIMESTAMP:
        print("Error: Provide adapter timestamp as argument or ADAPTER_TIMESTAMP env variable")
        print("Usage: python launch_dpo_eval.py YYYYMMDD-HHMMSS")
        sys.exit(1)
SHARP_ADAPTER = f"s3://{BUCKET}/dpo_adapters/{ADAPTER_TIMESTAMP}/sharp/sharp_adapter"
SMOOTH_ADAPTER = f"s3://{BUCKET}/dpo_adapters/{ADAPTER_TIMESTAMP}/smooth/smooth_adapter"

timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

def launch_eval_job(adapter_type, adapter_path):
    """Launch evaluation job for trained adapter"""
    
    processor = ScriptProcessor(
        role=ROLE,
        image_uri=f"763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.0.0-gpu-py310",
        command=["python3"],
        instance_type=INSTANCE_TYPE,
        instance_count=1,
        base_job_name=f"eval-dpo-{adapter_type}",
        volume_size_in_gb=50,
        max_runtime_in_seconds=7200,  # 2 hours
        env={
            "BASE_MODEL": BASE_MODEL,
            "ADAPTER_PATH": "/opt/ml/processing/input/adapter",
            "ADAPTER_TYPE": adapter_type,
            "SYSTEM_PROMPT": SYSTEM_PROMPT,
            "USE_QUANTIZATION": "true"
        }
    )
    
    output_path = f"s3://{BUCKET}/dpo_results/{timestamp}/{adapter_type}"
    
    print(f"Launching {adapter_type} adapter evaluation...")
    print(f"  Adapter: {adapter_path}")
    print(f"  Output: {output_path}")
    
    processor.run(
        code="scripts/eval_dpo_adapter.py",
        inputs=[
            ProcessingInput(
                source=".",
                destination="/opt/ml/processing/input/repo",
                input_name="repo"
            ),
            ProcessingInput(
                source=adapter_path,
                destination="/opt/ml/processing/input/adapter",
                input_name="adapter"
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
    
    return processor.latest_job.name

# Launch both evaluation jobs
print("\n" + "="*60)
print("LAUNCHING PARALLEL DPO EVALUATION JOBS")
print("="*60)

job_sharp = launch_eval_job("sharp", SHARP_ADAPTER)
job_smooth = launch_eval_job("smooth", SMOOTH_ADAPTER)

print("\n" + "="*60)
print("✅ Both evaluation jobs launched!")
print("="*60)
print(f"Sharp evaluation: {job_sharp}")
print(f"Smooth evaluation: {job_smooth}")
print(f"\nResults will be saved to: s3://{BUCKET}/dpo_results/{timestamp}/")
print("\nMonitor at:")
print(f"  https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/processing-jobs")
print(f"\nExpected completion: ~1.5 hours")
print(f"Cost: ~$7 total")
