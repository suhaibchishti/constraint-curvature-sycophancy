#!/usr/bin/env python3
"""
Launch two parallel processing jobs - one per model.
Faster than sequential execution.
"""
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from datetime import datetime

# Configuration
ROLE = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
BUCKET = "cc-eval-500330120558-us-east-1"
INSTANCE_TYPE = "ml.g5.xlarge"

# Models - Mistral v0.1 vs v0.2 validation (N=500)
# Validates the 9% sycophancy delta observed at N=50
MODEL_A = "mistralai/Mistral-7B-Instruct-v0.1"  # Predicted sharper boundary, higher S1
MODEL_B = "mistralai/Mistral-7B-Instruct-v0.2"  # Predicted smoother boundary, lower S1
SYSTEM_PROMPT = "You are a helpful assistant."

timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

def launch_job(model_path, model_name, job_suffix):
    """Launch a processing job for a single model"""
    
    processor = ScriptProcessor(
        role=ROLE,
        image_uri=f"763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.0.0-gpu-py310",
        command=["python3"],
        instance_type=INSTANCE_TYPE,
        instance_count=1,
        base_job_name=f"mistral-{model_name}",
        volume_size_in_gb=30,
        max_runtime_in_seconds=21600,  # 6 hours buffer
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
        logs=False  # Don't block on logs
    )
    
    return processor.latest_job.name

# Launch both jobs
print("="*60)
print("LAUNCHING PARALLEL PROCESSING JOBS")
print("="*60)

job_a = launch_job(MODEL_A, "mistral-v01", "A")
job_b = launch_job(MODEL_B, "mistral-v02", "B")

print("\n" + "="*60)
print("✅ Both jobs launched!")
print("="*60)
print(f"Job A (Mistral v0.1): {job_a}")
print(f"Job B (Mistral v0.2): {job_b}")
print(f"\nResults will be at: s3://{BUCKET}/artifacts/{timestamp}/")
print("\nMonitor at:")
print(f"  https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/processing-jobs")
print(f"\nValidating: N=50 showed 9% delta (13% vs 4%). Expecting similar at N=500.")
print("Expected completion: ~2 hours")
