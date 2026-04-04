#!/usr/bin/env python3
"""
Phase 4: 70B Scale Extension — SageMaker Launch Script

Runs Llama 3.1 70B and Qwen 2.5 72B on the same 50 Phase 3 facts
across 5 framing conditions at T=0.0 and T=0.7 (5 samples each).

Total: 50 facts × 5 framings × 2 temps × 5 samples = 2,500 responses per model.

Usage:
    python scripts/launch_phase4_70b.py
"""
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from datetime import datetime

ROLE   = "arn:aws:iam::500330120558:role/cc-eval-sagemaker-role-us-east-1"
BUCKET = "cc-eval-500330120558-us-east-1"

# 70B models need a larger instance — ml.g5.48xlarge has 8×A10G (192GB GPU RAM)
INSTANCE_TYPE = "ml.g5.48xlarge"

MODELS = [
    ("Llama-3.1-70B-Instruct",  "meta-llama/Llama-3.1-70B-Instruct"),
    ("Qwen2.5-72B-Instruct",    "Qwen/Qwen2.5-72B-Instruct"),
]

timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')


def launch_job(model_name, model_path):
    processor = ScriptProcessor(
        role=ROLE,
        image_uri="763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.5.1-gpu-py311-cu124-ubuntu22.04-ec2-v1.8",
        command=["python3"],
        instance_type=INSTANCE_TYPE,
        instance_count=1,
        base_job_name=f"phase4-{model_name[:20].lower().replace('.', '-')}",
        volume_size_in_gb=200,
        max_runtime_in_seconds=172800,  # 48 hours (70B needs ~4-6h; margin for download/OOM retries)
        env={
            "MODEL_PATH":  model_path,
            "MODEL_NAME":  model_name,
            "N_SAMPLES":   "5",
            "PHASE":       "4",
        }
    )

    output_path = f"s3://{BUCKET}/phase4/{timestamp}/{model_name}"
    print(f"\nLaunching: {model_name}")
    print(f"  Path:   {model_path}")
    print(f"  Output: {output_path}")

    processor.run(
        code="scripts/phase4_processing_job.py",
        inputs=[
            ProcessingInput(
                source=".",
                destination="/opt/ml/processing/input/repo",
                input_name="repo"
            )
        ],
        outputs=[
            ProcessingOutput(
                source="/opt/ml/processing/output",
                destination=output_path,
                output_name="results"
            )
        ],
        wait=False,
        logs=False,
    )
    print(f"  Job submitted (async). Check SageMaker console.")


if __name__ == "__main__":
    for model_name, model_path in MODELS:
        launch_job(model_name, model_path)
    print(f"\nAll jobs submitted. Timestamp: {timestamp}")
    print(f"Results will appear at: s3://{BUCKET}/phase4/{timestamp}/")
