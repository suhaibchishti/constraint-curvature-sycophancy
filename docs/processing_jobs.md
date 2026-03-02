# SageMaker Processing Jobs

For long-running evaluations (N=500), use SageMaker Processing Jobs instead of notebooks.

## Benefits

- ✅ No notebook timeout
- ✅ Runs independently in background
- ✅ Auto-saves to S3
- ✅ Can monitor/stop remotely
- ✅ Better cost efficiency

## Quick Start

### From SageMaker Notebook

```python
# Upload code and launch job
!python scripts/launch_job.py
```

### From Local (with AWS credentials)

```bash
cd constraint-curvature-sycophancy
python scripts/launch_job.py
```

## Configuration

Edit `scripts/launch_job.py`:

```python
MODEL_A = "meta-llama/Llama-2-7b-chat-hf"
MODEL_B = "meta-llama/Meta-Llama-3-8B-Instruct"
SYSTEM_PROMPT = "You are a helpful assistant."
INSTANCE_TYPE = "ml.g5.xlarge"
```

## Monitor Job

**Console:** https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/processing-jobs

**CLI:**
```bash
aws sagemaker list-processing-jobs --region us-east-1 --max-results 5
```

## Check Results

Results auto-upload to S3:

```bash
# List recent runs
aws s3 ls s3://cc-eval-500330120558-us-east-1/artifacts/ | tail -5

# Download latest
LATEST=$(aws s3 ls s3://cc-eval-500330120558-us-east-1/artifacts/ | tail -1 | awk '{print $2}')
aws s3 cp s3://cc-eval-500330120558-us-east-1/artifacts/${LATEST}summary.json - | jq .
```

## Cost

- ml.g5.xlarge: $1.41/hour
- N=500 eval: ~2.5 hours = ~$3.50
- Auto-stops when complete

## Troubleshooting

**Job fails immediately:**
- Check IAM role has S3 + ECR permissions
- Verify model IDs are correct
- Check CloudWatch logs

**Out of memory:**
- Ensure `USE_QUANTIZATION=true`
- Try ml.g5.2xlarge (48GB VRAM)

**Timeout:**
- Increase `max_runtime_in_seconds` in launch_job.py
- Default: 4 hours (14400 seconds)
