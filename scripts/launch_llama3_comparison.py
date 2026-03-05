#!/usr/bin/env python3
"""
Launch Llama 3 vs 3.1 comparison (Phase 3 replication)
"""
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from datetime import datetime

# Configuration
ROLE = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
BUCKET = "cc-eval-500330120558-us-east-1"
INSTANCE_TYPE = "ml.g5.xlarge"

# Models - Llama 3 vs 3.1 (same size, different alignment)
MODEL_A = "meta-llama/Meta-Llama-3-8B-Instruct"
MODEL_B = "meta-llama/Meta-Llama-3.1-8B-Instruct"
SYSTEM_PROMPT = "You are a helpful assistant."

timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

def launch_job(model_path, model_name):
    """Launch a processing job for a single model"""
    
    processor = ScriptProcessor(
        role=ROLE,
        image_uri=f"763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.0.0-gpu-py310",
        command=["python3"],
        instance_type=INSTANCE_TYPE,
        instance_count=1,
        base_job_name=f"llama-{model_name}",
        volume_size_in_gb=30,
        max_runtime_in_seconds=21600,  # 6 hours
        env={
            "MODEL_PATH": model_path,
            "MODEL_NAME": model_name,
            "SYSTEM_PROMPT": SYSTEM_PROMPT,
            "USE_QUANTIZATION": "true"
        }
    )
    
    output_path = f"s3://{BUCKET}/artifacts/{timestamp}/{model_name}"
    
    print(f"Launching job for {model_name}...")
    print(f"  Model: {model_path}")
    print(f"  Output: {output_path}")
    
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
    
    return processor.latest_job.name

# Launch both jobs
print("\n" + "="*60)
print("LAUNCHING LLAMA 3 vs 3.1 COMPARISON")
print("="*60)
print(f"Timestamp: {timestamp}")
print(f"Model A: {MODEL_A}")
print(f"Model B: {MODEL_B}")
print("="*60 + "\n")

job_a = launch_job(MODEL_A, "llama3-8b")
job_b = launch_job(MODEL_B, "llama31-8b")

print("\n" + "="*60)
print("✅ Both jobs launched!")
print("="*60)
print(f"Llama 3:   {job_a}")
print(f"Llama 3.1: {job_b}")
print(f"\nResults will be in: s3://{BUCKET}/artifacts/{timestamp}/")
print("\nMonitor with:")
print(f"  aws sagemaker list-processing-jobs --sort-by CreationTime --sort-order Descending --max-results 5")
print("="*60)
