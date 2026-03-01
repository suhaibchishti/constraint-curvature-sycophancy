#!/usr/bin/env bash
set -euo pipefail

MODEL_A="${1:-gpt2}"
MODEL_B="${2:-gpt2}"

python -m cc_eval.cli \
  --model-a "$MODEL_A" \
  --model-b "$MODEL_B" \
  --outdir artifacts \
  --seed 1 \
  --max-new 256 \
  --temp 0.2 \
  --top-p 0.95
