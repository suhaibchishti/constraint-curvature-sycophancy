# Phase 4: Scale Extension Plan
**Goal:** Address the three weaknesses identified in the NeurIPS reviewer feedback.  
**Venue target:** ICLR 2027 (September 2026 deadline)  
**Principle:** Prioritize scientific truth over deadline. Results drive the narrative.

---

## Weakness 2 — Scale Extension (Phase 4a, do first)

### Models
| Model | Size | Family | Comparison target |
|-------|------|--------|-------------------|
| Llama-3.1-70B-Instruct | 70B | Llama | Llama 3.1 8B (existing) |
| Qwen2.5-72B-Instruct | 72B | Qwen | Qwen 2.5 7B (existing) |
| Mistral-Large-2 (optional) | 123B | Mistral | Mistral v0.2 (existing) |

### Experimental Design
- Same 50 facts as Phase 3
- Same 5 framing conditions (neutral, original, leading, opinion, authority)
- Temperatures: T=0.0 and T=0.7 only (skip T=0.3 to reduce cost)
- 5 samples per combination (vs 10 in Phase 3)
- Total: `50 × 5 × 2 × 2 × 5 = 5,000` responses per model

### Infrastructure
- **Platform:** SageMaker (fp16, consistent with existing results)
- **Instance:** ml.g5.48xlarge (70B inference) or ml.p4d.24xlarge
- **Labeling:** GPT-4o-mini via OpenAI Batch API (same pipeline as Phase 3)
- **Estimated cost:** $50–100 per model

### Metrics to Compute
- KDG by framing (does authority still dominate at 70B?)
- KDG_S1 vs KDG_R decomposition (does Llama 70B remain refusal-driven?)
- Basin escape rate at T=0.7 (does the basin get shallower at scale?)
- Sharma boundary condition (does opinion framing still reverse for Llama/Qwen at 70B?)

### Expected Outcomes
| Scenario | Implication |
|----------|-------------|
| KDG decreases smoothly with scale | Clean scaling law story; 7-8B findings are efficient-model characterization |
| KDG persists at 70B | Stronger finding — deployment failure is not a small-model artifact |
| KDG_R pattern reverses at 70B | Llama over-constraint is scale-dependent; important nuance |

### Status
- [ ] SageMaker infrastructure setup
- [ ] Generation script (`scripts/run_phase4_70b.py`)
- [ ] Llama 3.1 70B run complete
- [ ] Qwen 2.5 72B run complete
- [ ] Labels generated
- [ ] Analysis complete
- [ ] Figures updated

---

## Weakness 1 — Formalize the Basin Math (Phase 4b, after 70B results)

### Proposed Addition to §3.4
Model escape probability as a function of temperature:

```
P(escape | T, m, f) = 1 - exp(-λ(m,f) · T)
```

where λ(m,f) is a model-framing-specific rate parameter estimated from T=0/0.3/0.7 observations. λ is the inverse basin depth — a concrete, interpretable parameter that grounds the "probabilistic basin" metaphor.

### Deliverables
- Table of λ values per model (fit from existing 7-8B data)
- Extend table with 70B λ values once Phase 4a is complete
- Add equation to §3.4 (KDG Metric subsection)
- Update §6 Discussion to reference λ when discussing basin depth

### Status
- [ ] Fit λ from existing 7-8B T=0/0.3/0.7 data
- [ ] Add equation to §3.4
- [ ] Add λ table to paper
- [ ] Extend with 70B values

---

## Weakness 3 — Reframe the Strawman (Phase 4c, after 70B results)

### Change
Replace in §7 Discussion opening:
> "The capability-versus-compliance debate presents a false dichotomy."

With:
> "The capability-versus-compliance debate has matured past a strict binary — most researchers suspect both contribute. Our contribution is quantifying the exact mixture ratio across model families and framing conditions, and showing that this ratio varies dramatically in ways that prior work could not measure."

### Note
Final wording depends on 70B results:
- If KDG scales smoothly → frame as "quantifying mixture ratio and its scaling behavior"
- If KDG persists at 70B → frame as "deployment failure is not a small-model artifact"

### Status
- [ ] Awaiting 70B results
- [ ] Rewrite §7 opening paragraph
- [ ] Update abstract if framing changes

---

## Timeline

| Phase | Task | Status |
|-------|------|--------|
| 4a | 70B scale run (Llama 3.1 70B + Qwen 2.5 72B) | ⬜ Not started |
| 4a | Analyze 70B results, update figures and tables | ⬜ Not started |
| 4b | Fit escape rate model, add λ equation to §3.4 | ⬜ Not started |
| 4c | Strawman reframe + §7 Discussion rewrite | ⬜ Not started |
| — | Optional: Mistral Large 123B run | ⬜ Optional |
| — | Full paper revision incorporating all three fixes | ⬜ Not started |
| — | Friend review round 3 | ⬜ Not started |
| — | Submit to ICLR 2027 | Sep 2026 |

---

## Comparison Checklist (fill in after Phase 4 complete)

| Metric | 7-8B (existing) | 70B (Phase 4a) | Δ |
|--------|----------------|----------------|---|
| Mistral authority KDG | +0.61 | TBD | TBD |
| Llama authority KDG | +0.31 | TBD | TBD |
| Llama KDG_R (authority) | +0.39 | TBD | TBD |
| Qwen 2.5 authority KDG | +0.04 | TBD | TBD |
| Overall basin escape T=0.7 | 37% | TBD | TBD |
| Mistral v0.1 escape rate | 55% | N/A (no 70B Mistral v0.1) | — |
| Sharma: Llama opinion Δ | −2.9pp | TBD | TBD |
| Sharma: Qwen 2.5 opinion Δ | −1.4pp | TBD | TBD |
