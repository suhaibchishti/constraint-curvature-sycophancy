# Deployment Guide

## Prerequisites

- AWS CLI configured
- HuggingFace account with token: https://huggingface.co/settings/tokens
- Access approved for gated models (Llama-2, Llama-3)

## Deploy Infrastructure

```bash
aws cloudformation deploy \
  --template-file infrastructure/sagemaker.yaml \
  --stack-name cc-eval \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    NotebookInstanceType=ml.g5.xlarge \
    VolumeSize=50 \
    HFToken=hf_YOUR_TOKEN_HERE
```

**Replace `hf_YOUR_TOKEN_HERE` with your actual token!**

This creates:
- ✅ SageMaker notebook instance (ml.g5.xlarge, A10G GPU)
- ✅ S3 bucket for artifacts (`cc-eval-{account}-{region}`)
- ✅ Secrets Manager secret (`cc-eval-hf-token`)
- ✅ IAM role with S3 + Secrets Manager permissions

## Verify Deployment

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name cc-eval --query 'Stacks[0].StackStatus'

# Get notebook URL
aws sagemaker describe-notebook-instance \
  --notebook-instance-name cc-eval-notebook \
  --query 'Url' --output text

# Verify secret
aws secretsmanager get-secret-value \
  --secret-id cc-eval-hf-token \
  --query 'SecretString' --output text | jq .
```

## Update HF Token

If you need to rotate the token:

```bash
aws secretsmanager update-secret \
  --secret-id cc-eval-hf-token \
  --secret-string '{"HF_TOKEN":"hf_NEW_TOKEN"}'
```

## Cleanup

```bash
# Delete stack (keeps S3 bucket by default)
aws cloudformation delete-stack --stack-name cc-eval

# Delete S3 bucket if needed
aws s3 rb s3://cc-eval-{account}-{region} --force
```

## Cost Estimate

- **Notebook (stopped):** $0/hour
- **Notebook (running):** $1.41/hour
- **S3 storage:** ~$0.023/GB/month
- **Secrets Manager:** $0.40/month
- **Processing job:** $1.41/hour (only when running)

**Typical eval run:** ~2.5 hours = ~$3.50
