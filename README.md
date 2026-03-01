# Constraint Curvature & Sycophancy

Evaluation harness to test the hypothesis that **constraint boundary curvature** affects model sycophancy rates.

## Hypothesis

Models trained with sharper constraint boundaries (Model A) will exhibit higher sycophancy than models with softer boundaries (Model B), while maintaining similar refusal rates on borderline-safe prompts.

## Quick Start

### Local Development (Pipeline Testing)
```bash
pip install -r requirements.txt
PYTHONPATH=src python -m cc_eval.cli \
  --model-a gpt2 \
  --model-b gpt2 \
  --outdir artifacts
```

### Production Evaluation (SageMaker)
```bash
# Deploy infrastructure
aws cloudformation deploy \
  --template-file infrastructure/sagemaker.yaml \
  --stack-name cc-eval \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides NotebookInstanceType=ml.g5.xlarge

# Run evaluation (see notebooks/run_eval.ipynb)
```

## Repository Structure

```
constraint-curvature-sycophancy/
├── evals/                    # Evaluation datasets (YAML)
├── src/cc_eval/              # Core evaluation code
├── infrastructure/           # CloudFormation templates
├── notebooks/                # SageMaker notebooks
├── scripts/                  # Helper scripts
└── artifacts/                # Generated outputs (gitignored)
```

## Architecture

1. **Generate**: Run Model A and Model B on eval sets
2. **Judge**: Classify outputs (refusal, sycophancy)
3. **Measure**: Compute metrics (sycophancy rate, refusal rate)
4. **Gate**: Validate hypothesis (A > B on sycophancy, A ≈ B on refusal)

## Cost Estimate

- SageMaker ml.g5.xlarge: ~$1.41/hour
- Typical eval run: 2-3 minutes (~$0.10)
- Storage (S3): negligible
