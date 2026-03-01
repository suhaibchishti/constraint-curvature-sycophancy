# SageMaker Infrastructure

This directory contains CloudFormation templates for deploying the evaluation infrastructure on AWS SageMaker.

## Quick Deploy

```bash
aws cloudformation deploy \
  --template-file sagemaker.yaml \
  --stack-name cc-eval \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides NotebookInstanceType=ml.g5.xlarge
```

## What Gets Created

- **S3 Bucket**: Stores evaluation artifacts with 30-day lifecycle policy
- **SageMaker Notebook**: GPU instance (ml.g5.xlarge by default) with lifecycle config
- **IAM Role**: Execution role with S3 and SageMaker permissions

## Configuration

Before deploying, update the CloudFormation template:

1. Replace `YOUR_USERNAME` in the `DefaultCodeRepository` parameter with your GitHub username
2. Optionally adjust instance type (ml.g5.xlarge, ml.g5.2xlarge, ml.p3.2xlarge)

## Access

After deployment:

```bash
# Get notebook URL
aws cloudformation describe-stacks \
  --stack-name cc-eval \
  --query 'Stacks[0].Outputs[?OutputKey==`NotebookURL`].OutputValue' \
  --output text

# Get S3 bucket name
aws cloudformation describe-stacks \
  --stack-name cc-eval \
  --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
  --output text
```

## Cost Management

The notebook instance runs continuously and incurs charges (~$1.41/hour for ml.g5.xlarge).

**Stop when not in use:**
```bash
aws sagemaker stop-notebook-instance --notebook-instance-name cc-eval-notebook
```

**Start when needed:**
```bash
aws sagemaker start-notebook-instance --notebook-instance-name cc-eval-notebook
```

**Delete everything:**
```bash
# Empty S3 bucket first
aws s3 rm s3://$(aws cloudformation describe-stacks --stack-name cc-eval --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' --output text) --recursive

# Delete stack
aws cloudformation delete-stack --stack-name cc-eval
```

## Instance Types

| Type | GPU | VRAM | Cost/hr | Use Case |
|------|-----|------|---------|----------|
| ml.g5.xlarge | 1x A10G | 24GB | ~$1.41 | 8B models (quantized) |
| ml.g5.2xlarge | 1x A10G | 24GB | ~$1.52 | 8B models (full precision) |
| ml.p3.2xlarge | 1x V100 | 16GB | ~$3.83 | Legacy option |
