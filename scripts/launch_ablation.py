#!/usr/bin/env python3
"""
Launch 4 parallel processing jobs for framing ablation.
One job per model: Mistral v0.1, v0.2, Qwen 1.5, 2.5.
"""
import boto3
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from datetime import datetime

ROLE = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
BUCKET = "cc-eval-500330120558-us-east-1"
INSTANCE_TYPE = "ml.g5.xlarge"
SYSTEM_PROMPT = "You are a helpful assistant."

MODELS = [
    ("mistral-v01", "mistralai/Mistral-7B-Instruct-v0.1"),
    ("mistral-v02", "mistralai/Mistral-7B-Instruct-v0.2"),
    ("llama3",      "meta-llama/Meta-Llama-3-8B-Instruct"),
    ("llama31",     "meta-llama/Llama-3.1-8B-Instruct")
    ("qwen15",      "Qwen/Qwen1.5-7B-Chat"),
    ("qwen25",      "Qwen/Qwen2.5-7B-Instruct"),
]

timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

def launch_job(model_name, model_path):
    processor = ScriptProcessor(
        role=ROLE,
        image_uri="763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.0.0-gpu-py310",
        command=["python3"],
        instance_type=INSTANCE_TYPE,
        instance_count=1,
        base_job_name=f"ablation-{model_name}",
        volume_size_in_gb=30,
        max_runtime_in_seconds=7200,  # 2 hours (only 30 prompts)
        env={
            "MODEL_PATH": model_path,
            "MODEL_NAME": model_name,
            "SYSTEM_PROMPT": SYSTEM_PROMPT,
            "USE_QUANTIZATION": "true"
        }
    )

    output_path = f"s3://{BUCKET}/artifacts/ablation-{timestamp}/{model_name}"

    print(f"Launching {model_name} ({model_path})...")
    processor.run(
        code="scripts/ablation_processing_job.py",
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

print("=" * 60)
print("LAUNCHING FRAMING ABLATION (4 parallel jobs)")
print("=" * 60)

jobs = {}
for model_name, model_path in MODELS:
    jobs[model_name] = launch_job(model_name, model_path)

print("\n" + "=" * 60)
print("✅ All 4 jobs launched!")
print("=" * 60)
for name, job_id in jobs.items():
    print(f"  {name}: {job_id}")
print(f"\nResults: s3://{BUCKET}/artifacts/ablation-{timestamp}/")
print(f"Monitor: https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/processing-jobs")
print(f"Expected: ~20 min (only 30 prompts per model)")
