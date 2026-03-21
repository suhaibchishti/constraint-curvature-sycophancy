# FP16 Migration Reference

Comparison of quantized (NF4) vs fp16 ablation results for Paper 1.
Both runs use the same 96 prompts × 6 models = 576 total responses.
S1-filtered pairs (N=135) are identical — determined by original 500-prompt labels, not the ablation run.

Generated: 2026-03-21

---

## 1. Headline Decomposition (N=135 S1 pairs, after dual judge)

| Metric | Old (NF4 + dual judge) | New (fp16 + dual judge) | Delta |
|--------|----------------------|------------------------|-------|
| S1 → CORRECT | 69 (51%) | 71 (53%) | +2 |
| S1 → PARTIAL | 49 (36%) | 45 (33%) | −4 |
| S1 → WRONG | 17 (13%) | 19 (14%) | +2 |
| Knows answer (C+P) | 118 (87%) | 116 (86%) | −2 |

**Conclusion:** Core finding unchanged. ~86% of sycophancy involves models that possess full or partial knowledge.

---

## 2. Per-Model Decomposition (after dual judge)

### Old (NF4)

| Model | CORRECT | PARTIAL | WRONG | Total S1 | % Knows |
|-------|---------|---------|-------|----------|---------|
| Mistral v0.1 | 41 | 22 | 5 | 68 | 93% |
| Mistral v0.2 | 17 | 10 | 0 | 27 | 100% |
| Llama 3 | 5 | 7 | 1 | 13 | 92% |
| Qwen 1.5 | 5 | 6 | 10 | 21 | 52% |
| Qwen 2.5 | 1 | 4 | 1 | 6 | 83% |

### New (fp16)

| Model | CORRECT | PARTIAL | WRONG | Total S1 | % Knows |
|-------|---------|---------|-------|----------|---------|
| Mistral v0.1 | 40 | 20 | 8 | 68 | 88% |
| Mistral v0.2 | 17 | 9 | 1 | 27 | 96% |
| Llama 3 | 5 | 7 | 1 | 13 | 92% |
| Qwen 1.5 | 6 | 6 | 9 | 21 | 57% |
| Qwen 2.5 | 3 | 3 | 0 | 6 | 100% |

### Per-Model Delta

| Model | % Knows (old → new) | WRONG (old → new) | Notes |
|-------|--------------------|--------------------|-------|
| Mistral v0.1 | 93% → 88% | 5 → 8 | Still overwhelmingly framing failure |
| Mistral v0.2 | 100% → 96% | 0 → 1 | Lost perfect score, 1 WRONG |
| Llama 3 | 92% → 92% | 1 → 1 | Identical |
| Qwen 1.5 | 52% → 57% | 10 → 9 | Slightly improved, still capability-failure model |
| Qwen 2.5 | 83% → 100% | 1 → 0 | Improved to zero WRONG |

---

## 3. Dual Judge Comparison

| Metric | Old run | New run (fp16) |
|--------|---------|----------------|
| Pre-dual WRONG (all 576) | 81 | 69 |
| Pre-dual WRONG (S1-filtered) | 17 | 23 |
| GPT-4o agreement on WRONG | 42% | 83% |
| Upgraded to PARTIAL | 37 | 2 |
| Upgraded to CORRECT | 10 | 2 |
| Final WRONG (S1-filtered) | 17 | 19 |

**Note:** Old run had 81 WRONG across all 576 responses; GPT-4o only agreed with 42%, upgrading 47.
New run had 69 WRONG across all 576; GPT-4o agreed with 83% of the 23 S1-filtered WRONG, upgrading only 4.
The fp16 WRONG labels are substantially more reliable (higher inter-judge agreement).

---

## 4. By Prompt Category (S1 pairs, after dual judge)

### Old (NF4)

| Category | CORRECT | PARTIAL | WRONG | Total |
|----------|---------|---------|-------|-------|
| authority-appeal | 25 | 14 | 4 | 43 |
| conspiracy | 2 | 1 | 0 | 3 |
| false-history | 19 | 10 | 10 | 39 |
| false-premise-health | 1 | 4 | 0 | 5 |
| false-premise-science | 2 | 4 | 2 | 8 |
| flattery-trap | 0 | 1 | 0 | 1 |
| pseudoscience | 14 | 12 | 1 | 27 |
| social-pressure | 4 | 3 | 0 | 7 |
| user-preference-pressure | 2 | 0 | 0 | 2 |

### New (fp16)

| Category | CORRECT | PARTIAL | WRONG | Total |
|----------|---------|---------|-------|-------|
| authority-appeal | 24 | 15 | 4 | 43 |
| conspiracy | 2 | 1 | 0 | 3 |
| false-history | 19 | 10 | 10 | 39 |
| false-premise-health | 2 | 3 | 0 | 5 |
| false-premise-science | 2 | 3 | 3 | 8 |
| flattery-trap | 0 | 1 | 0 | 1 |
| pseudoscience | 16 | 9 | 2 | 27 |
| social-pressure | 4 | 3 | 0 | 7 |
| user-preference-pressure | 2 | 0 | 0 | 2 |

### Category Delta

| Category | WRONG old → new | Notes |
|----------|----------------|-------|
| authority-appeal | 4 → 4 | Unchanged |
| false-history | 10 → 10 | Unchanged — still highest epistemic gap (26%) |
| false-premise-science | 2 → 3 | +1 |
| pseudoscience | 1 → 2 | +1 |
| All others | 0 → 0 | Unchanged |

---

## 5. Prose Numbers to Update in Paper

These are the specific numbers that appear in the paper text and need updating:

### Abstract & Introduction
- ~~"only 13% of sycophantic responses"~~ → "only 14%"
- ~~"in 87% of cases"~~ → "in 86% of cases"
- ~~"93% CORRECT or PARTIAL neutrally"~~ → "88%"
- ~~"48% WRONG neutrally"~~ → "43% WRONG neutrally"

### Section 3.5 (Framing Ablation)
- Headline table: 69/49/17 → 71/45/19
- Percentages: 51%/36%/13% → 53%/33%/14%
- ~~"Only 13% of sycophancy reflects genuine epistemic gaps"~~ → "Only 14%"
- ~~"At least 51%"~~ → "At least 53%"
- ~~"another 36%"~~ → "another 33%"
- ~~"87% of cases"~~ → "86% of cases"

### Per-model table
- Mistral v0.1: 41/22/5 → 40/20/8, 93% → 88%
- Mistral v0.2: 17/10/0 → 17/9/1, 100% → 96%
- Llama 3: 5/7/1 → 5/7/1 (unchanged)
- Qwen 1.5: 5/6/10 → 6/6/9, 52% → 57%
- Qwen 2.5: 1/4/1 → 3/3/0, 83% → 100%

### Per-model prose
- ~~"63 of 68 previously sycophantic prompts (93%)"~~ → "60 of 68 (88%)"
- ~~"Mistral v0.2 has zero WRONG responses"~~ → "Mistral v0.2 has just 1 WRONG response"
- ~~"10 of 21 S1 responses (48%)"~~ → "9 of 21 S1 responses (43%)"
- ~~"Qwen 2.5 reduces this to 1/6 (17%)"~~ → "Qwen 2.5 reduces this to 0/6 (0%)"

### Dual judge methodology (Section 2.4)
- ~~"all 81 responses initially labeled WRONG"~~ → "all 23 S1 responses initially labeled WRONG"
- ~~"inter-judge agreement on WRONG: 42%, with 37 upgraded to PARTIAL and 10 to CORRECT"~~ → "inter-judge agreement on WRONG: 83%, with 2 upgraded to PARTIAL and 2 to CORRECT"
- ~~"A manual review of all 22 S1 boundary cases (17 confirmed-WRONG plus 5 upgraded-PARTIAL)"~~ → needs update or removal

### Section 4 (Discussion)
- ~~"Only 13% of sycophantic responses (N=135)"~~ → "Only 14%"
- ~~"51% of S1 cases"~~ → "53%"
- ~~"another 36%"~~ → "another 33%"
- ~~"93% knows the answer neutrally"~~ → "88%"
- ~~"48% wrong neutrally"~~ → "43%"

### Section 5 (Conclusion)
- ~~"Only 13%"~~ → "Only 14%"
- ~~"in 87% of cases"~~ → "in 86%"
- ~~"93% knows the answer neutrally"~~ → "88%"
- ~~"48% wrong neutrally"~~ → "43%"

### Category-specific prose
- ~~"Authority-appeal prompts (43 S1 pairs) are predominantly framing failures (25 CORRECT)"~~ → "(24 CORRECT)"
- false-history: 11 WRONG, 28% → 10 WRONG, 26% (unchanged actually — was already 10 after dual judge)

### Figure caption
- ~~"93% knows the answer"~~ → "88%"
- ~~"48% wrong"~~ → "43%"

---

## 6. Methodology Note for Paper

Add to Section 2.4 or footnote:

> All ablation results reported in this paper use fp16 (half-precision) inference.
> Generation parameters: temperature=0.7, max_tokens=512, system_prompt="You are a helpful assistant."

---

## 7. Data Locations

### Old (NF4 quantized) — currently in paper & HuggingFace

| File | Path | Description |
|------|------|-------------|
| Ablation labels (576) | `huggingface_upload/full_ablation_labels.json` | All 96×6 neutral re-test labels |
| Dual judge results | `huggingface_upload/dual_label_wrong_results.json` | GPT-4o re-labels of WRONG cases |
| Ablation prompts | `huggingface_upload/full_ablation_prompts.json` | 96 neutral prompts + ground truth |
| Original 500-prompt labels | `huggingface_upload/gpt4o_labels_all.json` | S1/S2/C/H/R labels (unchanged) |
| Raw generations (S3) | `s3://cc-eval-500330120558-us-east-1/artifacts/full-ablation-20260315-133858/` | SageMaker output |

### New (fp16) — replacing old in paper

| File | Path | Description |
|------|------|-------------|
| Ablation labels (576) | `artifacts/full_ablation_labels.json` | All 96×6 neutral re-test labels |
| Dual judge results | `artifacts/fp16_dual_judge_results.json` | GPT-4o re-labels of 23 WRONG cases |
| WRONG cases input | `artifacts/fp16_wrong_for_dual_judge.json` | 23 S1 WRONG cases sent to GPT-4o |
| Raw generations (S3) | `s3://cc-eval-500330120558-us-east-1/artifacts/full-ablation-20260321-023358/` | SageMaker output |
| Raw generations (local) | `artifacts/full_ablation/` | Synced from S3 |

### Unchanged across both runs

| File | Path | Description |
|------|------|-------------|
| Ablation prompts | `huggingface_upload/full_ablation_prompts.json` | Same 96 prompts used in both runs |
| Original 500-prompt labels | `huggingface_upload/gpt4o_labels_all.json` | Determines S1 pairs (N=135) |
| Eval dataset | `evals/sycophancy_set_500.yaml` | 500 false-premise prompts |
| Human validation | `huggingface_upload/human_validation_results.json` | κ=0.752 (unchanged) |
| Prompt pressure labels | `huggingface_upload/prompt_pressure_labels.json` | 500 prompt classifications (unchanged) |

---

## 8. HuggingFace Dataset Update Plan

- Keep existing dataset as `v1-nf4-quantized` (or add version tag)
- Upload new fp16 results as the primary dataset
- Update README to note:
  - v1 used NF4 quantization (BitsAndBytes 4-bit)
  - v2 uses fp16 (half-precision, no quantization)
  - All paper numbers reference v2
  - v1 preserved for reproducibility and quantization-effect analysis
- Files to update/add:
  - `full_ablation_labels.json` → new fp16 version
  - `dual_label_wrong_results.json` → new fp16 dual judge results
  - Add `quantization_comparison.json` with side-by-side data (optional)
