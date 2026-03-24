# Research Implementation Plan

## Status: Phase 3 Complete → Merged Paper in Progress

Updated: 2026-03-23

---

## Publication Strategy

### Decision: Merge Paper 1 + Paper 2 into Single NeurIPS Submission

Paper 1 alone = workshop-tier (static snapshot, 500 prompts, single-shot).
Paper 2 alone = missing foundation (no taxonomy validation, no ablation grounding for KDG).
Merged = complete scientific arc: observation → ablation → distributional mechanism.

### Publication Pipeline

| Paper | Target | Status | Timeline |
|-------|--------|--------|----------|
| **Merged Paper** (Paper 1 + Phase 3) | NeurIPS 2026 Main | Writing | Submit late May 2026 |
| arXiv preprint | arXiv cs.CL/cs.AI | After NeurIPS draft | Before submission (priority claim) |
| **Paper 2: Multi-Turn** | ICLR 2027 | Not started | Experiments Q3 2026 |
| **Paper 3: Mechanistic** | Future | Not started | After Paper 2 |

---

## Completed Work

### Phase 1: Taxonomy & Single-Shot Evaluation ✅

- 500 false-premise prompts, 6 models, 3,000 responses
- S1/S2/C/H/R taxonomy with human validation (κ=0.752)
- Two alignment outcomes identified (effective vs over-constraint)
- Statistical significance tests (chi-squared, Cohen's h)

### Phase 2: Framing Ablation ✅

- 89 S1-producing prompts re-tested as neutral questions
- 576 responses (96 prompts × 6 models), fp16 precision
- N=135 S1 pairs: 53% CORRECT, 33% PARTIAL, 14% WRONG
- Dual-judge validation: 83% GPT-4o agreement on WRONG
- Quantization transparency: re-ran NF4→fp16, 70% agreement, stable headline
- Prompt pressure classification: 500 prompts into 5 framing types

### Phase 3: Distributional Analysis ✅

- 31,500 responses: 50 facts × 5 framings × 6 models × 3 temps × 10 samples
- fp16 precision, SageMaker ml.g5.xlarge, 14h timeout
- Labeled via OpenAI Batch API (single batch, zero errors)
- KDG metric: 3,600 fact-framing combinations computed
- Entropy analysis: 4,500 prompt contexts computed
- Framing sensitivity: per-model S1/R rates by framing
- Figures: KDG and entropy bar charts

### Infrastructure ✅

- SageMaker pipeline (launch, generate, checkpoint, S3 upload)
- OpenAI labeling pipeline (sync, async, batch modes)
- HuggingFace dataset (v2 fp16, v1 NF4 archived)
- All code committed to `setup/eval-harness` and `phase3/behavioral-distributions`

---

## Current: Merged Paper Writing

### Outline

See `docs/merged_paper_outline.md` for full section-by-section outline.

Narrative arc:
1. **Sec 3** — Taxonomy + ablation: 86% of sycophancy involves latent knowledge
2. **Sec 4** — KDG + framing sensitivity: knowledge suppression is framing-dependent and model-specific
3. **Sec 5** — Entropy + temperature: these are probabilistic basins, not deterministic walls

### Key Numbers Reference

See `docs/research_findings_complete.md` for all numbers with tables.

### Track B Decision: First-Token Logits

**Include as behavioral observation only.** Frame as: "first-token distribution predicts final label." Do NOT claim mechanistic interpretability — that invites hostile reviewers asking for activation patching and probing. Save real mechanistic work for Paper 3.

Compute cost: ~$2 (1,500 forward passes, ~1 hour). Decision: include if time permits before deadline, otherwise defer.

### Remaining Tasks

- [ ] Write merged paper (LaTeX, NeurIPS format)
- [ ] Generate all figures for merged paper
- [ ] Track B first-token analysis (optional, ~$2 compute)
- [ ] Internal review pass
- [ ] arXiv preprint upload (need endorsement for first-time cs.CL/cs.AI)
- [ ] NeurIPS OpenReview submission

---

## Future: Paper 2 — Multi-Turn Challenge-Response

### Research Question

Of the 86% of sycophantic responses where models possess the correct knowledge (proven by neutral ablation), how many cave when the user pushes back?

### Experimental Design

1. Take all (prompt, model) pairs where model corrected under neutral framing (C or H)
2. Present the original confirmatory-framed prompt
3. If model corrects → user pushes back: "Are you sure? I really thought X was true"
4. Measure cave-in rate: does the model abandon its correct answer?

### Why This is Clean

- We already proved the model has the knowledge (ablation CORRECT/PARTIAL)
- Any cave-in is 100% undeniably reward-shaped social compliance
- Directly tests Sharma et al.'s core finding in a controlled setting
- Single-turn data is the baseline; multi-turn is the intervention

### Variables

- Number of pushback turns (1, 2, 3)
- Pushback intensity ("Are you sure?" vs "That's wrong, X is true" vs "As an expert, I can tell you X")
- Same 6 models for continuity

### Compute Estimate

- ~135 S1 pairs × 6 models × 3 pushback intensities × 3 turns = ~7,300 conversations
- ~2-3 hours SageMaker compute (~$4)
- Labeling: ~7,300 API calls (~$1)

### Timeline

- Experiments: Q3 2026 (after NeurIPS submission)
- Writing: Q4 2026
- Target: ICLR 2027 (deadline typically October)

---

## Future: Paper 3 — Mechanistic Interpretability

### Research Questions

- Where in the model does framing override knowledge? (probing, causal tracing)
- Can sycophancy be steered via activation editing? (steering vectors)
- Do first-token logits predict downstream behavior? (routing analysis)
- Are Vennemeyer et al.'s linear directions for agreement/praise consistent with our KDG profiles?

### Prerequisites

- Merged paper published (establishes behavioral ground truth)
- Multi-turn paper in progress (establishes social compliance baseline)
- Familiarity with TransformerLens / nnsight / pyvene

### Timeline

- 2027, after Paper 2

---

## Repository Structure

```
main                              ← Public-facing (frozen after merge)
├── setup/eval-harness            ← Paper 1 code + fp16 ablation
└── phase3/behavioral-distributions ← Phase 3 code + merged paper
```

### Key File Locations

| File | Branch | Description |
|------|--------|-------------|
| `docs/merged_paper_outline.md` | phase3 | NeurIPS paper outline |
| `docs/research_findings_complete.md` | phase3 | All numbers, single source of truth |
| `docs/fp16_migration_reference.md` | setup/eval-harness | NF4→fp16 comparison |
| `docs/paper_final.md` | setup/eval-harness | Paper 1 standalone (superseded by merge) |
| `phase3/outputs/metrics/` | phase3 | KDG and entropy results |
| `phase3/outputs/labels/` | phase3 | 31,500 labeled responses |
| `huggingface_upload/` | setup/eval-harness | HuggingFace dataset (v2 fp16) |
| `artifacts/full_ablation_labels.json` | setup/eval-harness | fp16 ablation labels |
| `artifacts/fp16_dual_judge_results.json` | setup/eval-harness | Dual-judge results |

### AWS Resources

- SageMaker notebook: `cc-eval-notebook` (ml.g5.xlarge) — **STOPPED**
- S3 bucket: `cc-eval-500330120558-us-east-1`
- Processing job quota: 6 × ml.g5.xlarge
- OpenAI: Tier 2, 30K RPD, 10M batch tokens
