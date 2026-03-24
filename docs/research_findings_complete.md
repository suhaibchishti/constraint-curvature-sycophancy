# Research Findings: Complete Results Summary

All results from Paper 1 (taxonomy + ablation) and Phase 3 (distributional analysis).
This document serves as the single source of truth for all numbers going into the merged NeurIPS paper.

Generated: 2026-03-23

---

## 1. Paper 1: Taxonomy & Single-Shot Evaluation (N=3,000)

### 1.1 S1 Rates by Model

| Model | S1 Rate | S2 Rate | C Rate | H Rate | R Rate |
|-------|---------|---------|--------|--------|--------|
| Mistral v0.1 | 13.6% | 0.2% | 72.4% | 3.6% | 10.2% |
| Mistral v0.2 | 5.4% | 0.0% | 76.0% | 6.8% | 11.4% |
| Llama 3 | 2.6% | 0.0% | 70.0% | 1.8% | 25.6% |
| Llama 3.1 | 0.0% | 0.0% | 58.8% | 4.8% | 36.4% |
| Qwen 1.5 | 4.2% | 0.0% | 74.0% | 0.8% | 21.0% |
| Qwen 2.5 | 1.2% | 0.0% | 78.0% | 10.4% | 10.4% |

### 1.2 Alignment Outcomes

- **Effective alignment (Mistral):** S1 13.6% → 5.4% (Δ=−8.2pp, p<0.001), refusal stable
- **Effective alignment (Qwen):** S1 4.2% → 1.2% (Δ=−3.0pp, p=0.005), refusal ↓ 50%
- **Over-constraint (Llama):** S1 2.6% → 0.0% (p<0.001), but refusal 25.6% → 36.4% (+42%)

### 1.3 Framing Ablation (fp16, dual-judge validated)

**Headline (N=135 S1 pairs):**

| Neutral Result | Count | % | Interpretation |
|----------------|-------|---|----------------|
| S1 → CORRECT | 71 | 53% | Model knew the answer; framing overrode correction |
| S1 → PARTIAL | 45 | 33% | Model had partial knowledge; framing tipped it |
| S1 → WRONG | 19 | 14% | Genuine epistemic gap |

**86% of sycophancy involves knowledge the model already has.**

**Per-model decomposition:**

| Model | CORRECT | PARTIAL | WRONG | Total S1 | % Knows |
|-------|---------|---------|-------|----------|---------|
| Mistral v0.1 | 40 | 20 | 8 | 68 | 88% |
| Mistral v0.2 | 17 | 9 | 1 | 27 | 96% |
| Llama 3 | 5 | 7 | 1 | 13 | 92% |
| Qwen 1.5 | 6 | 6 | 9 | 21 | 57% |
| Qwen 2.5 | 3 | 3 | 0 | 6 | 100% |

**Dual-judge validation:** 23 S1 WRONG cases re-labeled by GPT-4o. 83% agreement (19 confirmed WRONG, 2 → PARTIAL, 2 → CORRECT).

**Quantization note:** Re-ran at fp16 (was NF4). 70% label agreement on S1 pairs. Headline stable (CORRECT 51%→53%, WRONG 13%→14%).

### 1.4 Prompt Pressure Classification (N=500 prompts)

| Category | N | S1 Rate |
|----------|---|---------|
| OPINION | 23 | 0.0% |
| FLATTERY | 37 | 0.0% |
| HIGH_PRESSURE | 96 | 1.6% |
| NEUTRAL | 119 | 5.0% |
| LEADING | 225 | 6.7% |

---

## 2. Phase 3: Distributional Analysis (N=31,500)

### 2.1 Experimental Design

- 50 core facts × 5 framings × 6 models × 3 temperatures (0.0, 0.3, 0.7) × 10 samples
- fp16 precision, SageMaker ml.g5.xlarge
- Labeled via OpenAI Batch API (GPT-4o-mini, single batch, zero errors)

### 2.2 S1 Rate by Framing (all models aggregated)

| Framing | N | S1 | S1% | S2 | S2% | R | R% |
|---------|---|----|----|----|----|---|----|
| neutral | 6,300 | 605 | 9.6% | 72 | 1.1% | 0 | 0.0% |
| opinion | 6,300 | 708 | 11.2% | 34 | 0.5% | 34 | 0.5% |
| leading | 6,300 | 662 | 10.5% | 6 | 0.1% | 21 | 0.3% |
| authority | 6,300 | 852 | 13.5% | 320 | 5.1% | 493 | 7.8% |
| original | 6,300 | 921 | 14.6% | 20 | 0.3% | 256 | 4.1% |

**Key findings:**
- Original framing has highest S1 (14.6%) — the prompts as-written are the worst case
- Authority is close (13.5%) and uniquely drives S2 confabulation (5.1%) and refusal (7.8%)
- Neutral baseline is 9.6% — even without framing, models still sycophant on some facts
- Opinion (11.2%) is between neutral and authority — model-specific effects (see 2.4)

### 2.3 S1 Rate by Model × Framing

| Model | Neutral | Opinion | Leading | Authority | Original |
|-------|---------|---------|---------|-----------|----------|
| Mistral v0.1 | 6.4% | 11.8% | 12.5% | **45.3%** | 25.8% |
| Mistral v0.2 | 8.3% | 17.9% | 19.0% | 8.4% | 17.9% |
| Llama 3 | 8.7% | 7.0% | 3.4% | 11.5% | 10.9% |
| Llama 3.1 | 5.9% | 3.0% | 0.1% | 0.0% | 3.0% |
| Qwen 1.5 | **19.3%** | **20.1%** | **23.0%** | 5.0% | 22.3% |
| Qwen 2.5 | 9.0% | 7.6% | 5.0% | 10.9% | 7.9% |

**Standout findings:**
- **Mistral v0.1 + authority = 45.3% S1** — nearly half of all responses are sycophantic
- **Qwen 1.5 = high baseline** — 19–23% S1 across neutral/opinion/leading/original, but only 5% under authority (authority triggers correction in Qwen 1.5)
- **Llama 3.1 + authority = 0% S1, 38.8% R** — complete refusal under authority framing
- **Llama 3.1 + leading = 0.1% S1** — near-zero sycophancy under leading questions

### 2.4 The Sharma Replication: Opinion Framing Effects

Opinion ("I believe X") vs Neutral, per model:

| Model | Neutral S1% | Opinion S1% | Δ | Direction |
|-------|-------------|-------------|---|-----------|
| Mistral v0.1 | 6.4% | 11.8% | **+5.4pp** | ↑ More sycophantic |
| Mistral v0.2 | 8.3% | 17.9% | **+9.6pp** | ↑ More sycophantic |
| Llama 3 | 8.7% | 7.0% | −1.7pp | ↓ Less sycophantic |
| Llama 3.1 | 5.9% | 3.0% | −2.9pp | ↓ Less sycophantic |
| Qwen 1.5 | 19.3% | 20.1% | +0.8pp | → Flat |
| Qwen 2.5 | 9.0% | 7.6% | −1.4pp | ↓ Less sycophantic |

**Sharma et al. predicted opinion framing universally increases sycophancy. We find:**
- True for Mistral (both versions) — opinion triggers deference
- False for Llama and Qwen 2.5 — opinion triggers correction instinct
- Neutral for Qwen 1.5 — sycophancy is capability-driven, framing doesn't matter
- Mistral v0.2 is *more* opinion-sensitive than v0.1 (+9.6pp vs +5.4pp) — alignment made it more deferential to user beliefs

### 2.5 Authority Framing: The Triple Threat

Authority framing uniquely triggers three failure modes simultaneously:

| Metric | Authority | Next Highest | Ratio |
|--------|-----------|-------------|-------|
| S1 (sycophancy) | 13.5% | 14.6% (original) | 0.9× |
| S2 (confabulation) | **5.1%** | 1.1% (neutral) | **4.6×** |
| R (refusal) | **7.8%** | 4.1% (original) | **1.9×** |

Authority framing doesn't just increase sycophancy — it uniquely drives confabulation (models fabricate supporting details for the authority's claim) and refusal (models refuse to engage with authority-framed false premises).

### 2.6 Knowledge Deployment Gap (KDG)

**Definition:** KDG = P(correct|neutral) − P(correct|framed), where correct = label ∈ {C, H}

**Top KDG values (mean across 150 fact-temperature combinations):**

| Model | Framing | KDG | Interpretation |
|-------|---------|-----|----------------|
| Mistral v0.1 | authority | **+0.611** | Massive knowledge suppression |
| Llama 3.1 | authority | +0.323 | Knowledge suppressed by refusal |
| Mistral v0.1 | original | +0.224 | Moderate suppression |
| Mistral v0.2 | original | +0.145 | Reduced by alignment |
| Mistral v0.2 | leading | +0.129 | |
| Llama 3.1 | original | +0.121 | |
| Qwen 1.5 | authority | **−0.116** | Authority *improves* correctness |
| Mistral v0.2 | opinion | +0.105 | Opinion suppresses knowledge |

**Key findings:**
- Mistral v0.1 authority KDG=0.61 is the highest — 61% knowledge suppression
- Qwen 2.5 has near-zero KDG across all framings — most robust model
- Qwen 1.5 has *negative* KDG under authority — authority framing actually helps it correct
- Alignment reduces KDG: Mistral v0.1→v0.2 authority KDG drops dramatically

### 2.6.1 KDG Decomposition: Sycophancy-Driven vs Refusal-Driven

| Model | Framing | KDG_total | KDG_S1 | KDG_R | Dominant driver |
|-------|---------|-----------|--------|-------|-----------------|
| Mistral v0.1 | authority | +0.608 | **+0.390** | +0.000 | S1 (sycophancy) |
| Mistral v0.1 | original | +0.200 | +0.194 | +0.006 | S1 |
| Mistral v0.2 | original | +0.121 | +0.096 | +0.026 | S1 |
| Mistral v0.2 | leading | +0.116 | +0.107 | +0.010 | S1 |
| Mistral v0.2 | opinion | +0.108 | +0.096 | +0.012 | S1 |
| Llama 3.1 | authority | +0.308 | **−0.059** | **+0.388** | R (refusal) |
| Llama 3.1 | original | +0.130 | −0.030 | +0.181 | R (refusal) |
| Llama 3 | authority | +0.110 | +0.029 | +0.082 | Mixed |
| Qwen 1.5 | authority | −0.131 | −0.143 | +0.000 | Negative (authority helps) |

**Critical distinction:** Mistral v0.1 authority KDG=0.61 is genuine knowledge suppression via sycophancy (KDG_S1=+0.39). Llama 3.1 authority KDG=0.31 is knowledge suppression via refusal (KDG_R=+0.39, KDG_S1 is actually *negative*). Same metric value, mechanistically different failures. The paper must report both components.

### 2.7 Entropy Analysis

**Mean entropy by model × temperature:**

| Model | T=0.0 | T=0.3 | T=0.7 |
|-------|-------|-------|-------|
| Mistral v0.1 | 0.000 | 0.071 | 0.053 |
| Mistral v0.2 | 0.000 | 0.110 | 0.102 |
| Llama 3 | 0.000 | **0.141** | 0.101 |
| Llama 3.1 | 0.000 | 0.080 | 0.101 |
| Qwen 1.5 | 0.000 | 0.083 | 0.068 |
| Qwen 2.5 | 0.000 | 0.062 | 0.065 |

**Key findings:**
- T=0 is always deterministic (entropy=0) — expected
- Meta-Llama-3 has highest entropy at T=0.3 (0.141) — most behaviorally variable
- Mistral v0.1 has lowest non-zero entropy (0.053–0.071) — most deterministic sycophant
- Qwen 2.5 has low, stable entropy across temperatures — consistent behavior

### 2.8 Temperature Effects on S1

| Temperature | N | S1 | S1% |
|-------------|---|----|----|
| T=0.0 | 1,500 | 184 | 12.3% |
| T=0.3 | 15,000 | 2,018 | 13.5% |
| T=0.7 | 15,000 | 1,546 | 10.3% |

T=0.3 has the highest S1 rate — slight randomness pushes models toward sycophancy. T=0.7 reduces it — more randomness allows escape from sycophantic basins.

### 2.9 Basin Escape: Temperature as Escape Velocity

For the 184 (model, fact, framing) combos that are deterministically S1 at T=0:

| Temperature | N samples | Stay S1 | Escape to C | Escape to H | Total escape |
|-------------|-----------|---------|-------------|-------------|--------------|
| T=0.0 | 184 | 184 (100%) | 0 | 0 | 0% |
| T=0.3 | 1,840 | 1,498 (81.4%) | 156 (8.5%) | 85 (4.6%) | 18.6% |
| T=0.7 | 1,840 | 1,161 (63.1%) | 342 (18.6%) | 265 (14.4%) | **36.9%** |

**This is the key finding:** 37% of deterministically sycophantic responses escape the basin at T=0.7. The model's latent knowledge is fighting the RLHF agreement attractor, and temperature provides the escape energy.

The escape trajectory is S1 → H → C. Hedge (H) is the transition state — the model is conflicted, hedging before correcting.

### 2.9.1 Per-Model Basin Escape (T=0 S1 → T=0.7)

| Model | T=0 S1 combos | Escape rate | → C | → H | Basin type |
|-------|---------------|-------------|-----|-----|------------|
| Mistral v0.1 | 61 | **55%** | 222 | 75 | Wide, shallow — framing failure, easily recoverable |
| Mistral v0.2 | 37 | 28% | 43 | 60 | Narrower — alignment reduced basin width |
| Llama 3 | 17 | 47% | 16 | 64 | Moderate — escapes mostly to H (hedge) |
| Llama 3.1 | 6 | 50% | 0 | 20 | Escapes to H only, never to C — hedges but won't fully correct |
| Qwen 1.5 | 47 | **20%** | 50 | 24 | Narrow, deep — capability failure, hard to recover |
| Qwen 2.5 | 16 | 24% | 11 | 22 | Few S1 to begin with — robust alignment |

**Mistral v0.1 is the most sycophantic but most rescuable (55% escape).** Its basin is wide but shallow — temperature easily dislodges it because the knowledge is there.

**Qwen 1.5 is the least rescuable (20% escape).** Its basin is narrow but deep — even temperature can't help because the model genuinely lacks the knowledge. This confirms Paper 1's capability-failure finding (57% "knows").

**Llama 3.1 escapes only to H, never to C.** Even when temperature dislodges it from S1, it hedges rather than fully correcting — the safety training prevents confident correction.

### 2.9.2 Llama 3.1 Authority Anomaly

Llama 3.1 under authority framing: 0% S1, 38.8% R. KDG=0.308.

The KDG is driven entirely by refusal, not sycophancy. Correct rate drops from 92% (neutral) to 61% (authority) — the missing 31% went to refusal. The safety classifier cannot distinguish "authority-framed false premise needing correction" from "authority-framed harmful content needing refusal." This is the over-constraint pattern from Paper 1 manifesting at distributional scale.

### 2.10 Hedge as Transition State

H rate by framing condition:

| Framing | H Rate |
|---------|--------|
| neutral | 14.0% |
| original | 23.4% |
| leading | 23.6% |
| authority | 25.1% |
| opinion | 26.5% |

H nearly doubles from neutral to framed conditions. This is the behavioral footprint of the knowledge-deployment collision — the model has the knowledge but the framing creates friction in deploying it.

---

## 3. Basin Characterization (Behavioral, Not Mechanistic)

Combining KDG and entropy gives a behavioral profile per model:

| Model | KDG Profile | Entropy Profile | Basin Type |
|-------|-------------|-----------------|------------|
| Mistral v0.1 | Very high (authority) | Low | **Deep deterministic basin** — reliably sycophantic under authority |
| Mistral v0.2 | Moderate | Medium | **Shallow basin** — alignment reduced depth |
| Llama 3 | Moderate | **High** | **Noisy basin** — variable behavior |
| Llama 3.1 | High (authority→refusal) | Medium | **Refusal basin** — authority triggers refusal not sycophancy |
| Qwen 1.5 | Low/negative | Medium | **Flat landscape** — sycophancy is baseline, not framing-induced |
| Qwen 2.5 | **Near-zero** | **Low, stable** | **No basin** — robust alignment |

---

## 4. Cross-Paper Alignment

| Paper 1 Finding | Phase 3 Confirmation |
|-----------------|---------------------|
| Mistral v0.1 highest S1 (13.6%) | Confirmed: 6.4–45.3% depending on framing |
| Qwen 1.5 sycophancy is capability-driven (57% knows) | Confirmed: 19–23% S1 regardless of framing, flat KDG |
| Llama 3.1 over-constrains (0% S1, 36.4% R) | Confirmed: 0% S1 + 38.8% R under authority |
| 86% of sycophancy involves latent knowledge | Confirmed: KDG shows knowledge is present but suppressed |
| Leading questions are the primary trigger | Partially: original (14.6%) > authority (13.5%) > opinion (11.2%) > leading (10.5%) |

---

## 5. Validation Summary

| Validation | Method | Result |
|------------|--------|--------|
| Human vs GPT-4o-mini | 50 stratified samples | κ=0.752, 100% S1/R recall |
| Dual judge (ablation) | GPT-4o on 23 WRONG cases | 83% agreement |
| Quantization robustness | NF4 vs fp16 comparison | 70% agreement, stable headline |
| Batch labeling | 31,500 via OpenAI Batch API | Zero errors |
