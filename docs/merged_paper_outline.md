# Framing-Induced Sycophancy in Large Language Models: A Distributional Analysis Across Three Model Families

## Paper Outline — Merged Paper 1 + Paper 2

**Target:** NeurIPS 2026 Main Conference (deadline ~late May)
**Backup:** ICLR 2027

---

## Abstract

We present a comprehensive behavioral analysis of sycophancy in large language models, demonstrating that false-premise agreement is primarily a framing-induced probabilistic failure rather than an epistemic gap. Using a validated S1/S2/C/H/R taxonomy across 3,000 single-turn responses from six models (Mistral v0.1/v0.2, Llama 3/3.1, Qwen 1.5/2.5), we first establish that 86% of sycophantic responses occur when models possess the correct knowledge but fail to deploy it under confirmatory framing (N=135 ablation pairs, fp16, dual-judge validated). We then scale this analysis to 31,500 sampled responses across 5 framing conditions, 3 temperatures, and 10 samples per configuration, introducing the Knowledge Deployment Gap (KDG) metric to quantify framing-induced knowledge suppression. KDG reveals dramatic heterogeneity: Mistral v0.1 exhibits KDG=0.61 under authority framing (S1-driven) while Llama 3.1 shows KDG=0.31 under authority driven entirely by refusal — same metric, mechanistically different failures. Contrary to prior work suggesting "I believe" opinion framing universally increases sycophancy, we find this is a boundary condition: opinion framing increases sycophancy in older instruction-tuned models (Mistral +5–10pp) but decreases it in RLHF-aligned models (Llama, Qwen 2.5: −1 to −3pp). Temperature analysis reveals sycophancy is a probabilistic basin, not a deterministic wall: 37% of responses that are deterministically sycophantic at T=0 escape to correct or hedge responses at T=0.7, with the Hedge (H) state — which doubles from 14% to 23–27% under framing — serving as the transition state between sycophancy and correction. We provide the complete dataset (35,076 labeled responses) and analysis code as open-source resources.

---

## Section 1: Introduction

- The alignment tension: safety training induces sycophancy and over-refusal
- Two competing explanations: capability failure (Lin/TruthfulQA) vs reward-shaped compliance (Sharma/Wang)
- Our contribution: these aren't competing — they're a mixture, and the mixture ratio varies by model family and framing condition
- Preview of the three-act structure: taxonomy → ablation → distributional analysis

### 1.1 Research Questions

1. When models agree with false premises, do they lack the knowledge or fail to deploy it?
2. Is this failure deterministic or probabilistic? Does it vary with temperature?
3. Which framing conditions trigger knowledge suppression, and does this vary across model families?
4. Does the "I believe" opinion pressure identified by Sharma et al. generalize across architectures?

### 1.2 Contributions

1. Validated taxonomy (S1/S2/C/H/R) with human validation (κ=0.752)
2. Framing ablation proving 86% of sycophancy involves latent correct knowledge
3. KDG metric quantifying framing-induced knowledge suppression at distributional scale
4. Model-specific framing sensitivity profiles across 5 conditions
5. Partial replication and extension of Sharma et al. opinion-framing findings
6. Open dataset: 3,000 + 31,500 labeled responses

---

## Section 2: Related Work

### 2.1 Sycophancy Mechanisms
- Sharma et al. [2023]: Preference model bias, multi-turn social pressure
- Shapira et al. [2025]: RLHF causally amplifies sycophancy via reward covariance
- Wang et al. [2024]: Late-layer knowledge override
- Vennemeyer et al. [2025]: Distinct linear directions for agreement vs praise

### 2.2 Sycophancy Evaluation
- Perez et al. [2022]: First documentation of opinion agreement
- Çelebi et al. [2025]: PARROT benchmark, neutral-vs-framed MMLU
- Dubois et al. [2024]: Input framing as causal driver

### 2.3 Truthfulness & Calibration
- Lin et al. [2022]: TruthfulQA — sycophancy as truthfulness failure
- Malmqvist [2024]: Survey of causes and mitigations

### 2.4 Our Position
- We bridge behavioral evaluation (Sec 2.2) with mechanistic hypotheses (Sec 2.1)
- Our ablation design parallels Çelebi but at distributional scale with KDG quantification
- We extend Sharma's opinion-framing finding to show it's model-specific, not universal
- The mechanistic camp (activation patching, linear probing) proved models "know the truth but suppress it" — we provide a scalable black-box metric (KDG) to measure this gap without weights access
- The calibration camp (Beacon) frames sycophancy as epistemic calibration breakdown — our temperature/entropy analysis shows this breakdown is a probabilistic basin, not a deterministic wall
- Hong et al. mapped multi-turn stance flips but didn't isolate whether models knew the truth — our ablation fills this gap

---

## Section 3: Taxonomy, Dataset & Single-Shot Evaluation

*[From Paper 1]*

### 3.1 Dataset Construction
- 500 false-premise prompts across 4 domains
- Generation parameters (T=0.7, fp16, 6 models)
- 3,000 total responses

### 3.2 S1/S2/C/H/R Taxonomy
- Definitions
- GPT-4o-mini labeling with human validation (κ=0.752, 100% S1/R recall)

### 3.3 Alignment Outcomes
- Effective alignment (Mistral, Qwen): sycophancy ↓, helpfulness maintained
- Over-constraint (Llama 3.1): sycophancy → 0%, but refusal +42%
- Table: S1/R rates per model, chi-squared tests

### 3.4 The Framing Ablation
- 89 S1-producing prompts re-tested as neutral questions
- N=135 S1 pairs: 53% CORRECT, 33% PARTIAL, 14% WRONG (fp16, dual-judge)
- Per-model decomposition: Mistral v0.1 88% knows vs Qwen 1.5 57% knows
- Quantization transparency note (70% agreement NF4↔fp16, stable headline)
- **Key claim: 86% of sycophancy involves knowledge the model already has**

### 3.5 Prompt Pressure Classification
- 500 prompts classified into 5 framing types
- Leading questions (6.7% S1) >> opinion (0.0%) and flattery (0.0%)
- Motivates the distributional analysis: what happens at scale with controlled framing?

---

## Section 4: Distributional Analysis & Knowledge Deployment Gap

*[From Paper 2]*

### 4.1 Experimental Design
- 50 core facts × 5 framings × 6 models × 3 temperatures × 10 samples = 31,500 responses (fp16)
- 5 framings: neutral, original, leading, opinion, authority
- Labeling: GPT-4o-mini via Batch API (single batch, zero errors)
- Bridge to Paper 1: same taxonomy, same models, same prompts (subset)
- **Methodology note:** Phase 3 facts are a targeted diagnostic subset (50 facts from domains where S1 was observed in Paper 1), not a representative sample of the original 500-prompt distribution. This explains why per-model S1 rates differ between Sec 3 (e.g., Qwen 1.5 S1=4.2% on 500 prompts) and Sec 4 (Qwen 1.5 neutral S1=19.3% on 50 targeted facts). The targeted subset is deliberately harder, designed to stress-test framing sensitivity rather than estimate population S1 rates.
- **Neutral baseline note:** Neutral framing produces 9.6% S1 overall, confirming that some facts are genuinely difficult regardless of framing. These map to capability gaps (the 14% WRONG from the ablation). The neutral condition is the best available behavioral proxy for "unframed" knowledge, not a claim of zero sycophancy.

### 4.2 The KDG Metric
- Definition: KDG(model, framing) = P(correct|neutral) − P(correct|framed)
- Where correct = label ∈ {C, H}
- Interpretation: positive KDG = framing suppresses correct knowledge
- **Decomposition:** KDG_S1 = P(S1|framed) − P(S1|neutral) measures sycophancy-driven suppression; KDG_R = P(R|framed) − P(R|neutral) measures refusal-driven suppression. KDG ≈ KDG_S1 + KDG_R + residual. This decomposition is critical: Mistral v0.1 authority KDG=0.61 is S1-driven (KDG_S1=+0.39), while Llama 3.1 authority KDG=0.31 is entirely R-driven (KDG_R=+0.39, KDG_S1=−0.06). Same metric, mechanistically different failures.

### 4.3 KDG Results
- **Authority is the dominant trigger**: Mistral v0.1 KDG=0.61 (authority), highest in dataset
- **Model family heterogeneity**: Qwen 2.5 near-zero KDG across all framings
- **Alignment reduces KDG**: Mistral v0.1→v0.2 reduces authority KDG
- KDG heatmap: model × framing
- Table: top KDG values by model-framing pair

### 4.4 Framing Sensitivity Profiles
- S1 rates by framing per model
- Authority: 13.5% S1 overall, drives 7.8% refusal and 5.1% confabulation (S2)
- Original framing: 14.6% S1 (highest overall)
- **The opinion reversal**: Mistral v0.1/v0.2 +5–10pp under opinion, Llama/Qwen 2.5 −1 to −3pp
- Qwen 1.5: 19–20% S1 regardless of framing (framing-independent baseline sycophancy)

### 4.5 The Sharma Boundary Condition
- Sharma et al. predict "I believe" framing increases sycophancy
- Our finding: true for older instruction-tuned models (Mistral), false for RLHF-aligned models (Llama, Qwen 2.5)
- This is not a failed replication — it's a boundary condition: Sharma's prediction holds for models where alignment prioritized agreeableness, but fails for models where alignment introduced epistemic correction circuits
- Interpretation by alignment generation:
  - Mistral v0.1/v0.2: trained to be "helpful and agreeable" → opinion triggers deference
  - Llama 3/3.1: trained to be cautious → opinion triggers correction instinct
  - Qwen 1.5: sycophancy is capability-driven, framing doesn't matter
- Mistral v0.2 is *more* opinion-sensitive than v0.1 (+9.6pp vs +5.4pp) — alignment reduced authority vulnerability but increased opinion deference. Different alignment approaches patch different failure modes.

---

## Section 5: Temperature, Entropy & Probabilistic Basins

### 5.1 Temperature as Basin Escape Velocity
- For prompts deterministically sycophantic at T=0 (N=184 combos):
  - T=0.3: 81% remain S1, 8.5% escape to C, 4.6% to H
  - T=0.7: 63% remain S1, 18.6% escape to C, 14.4% to H
  - **37% escape rate at T=0.7** — the sycophancy basin is probabilistic, not deterministic
- We observe a non-monotonic relationship between temperature and S1 rate: S1 peaks at T=0.3 (13.5%) and drops at T=0.7 (10.3%). This is consistent with the hypothesis that modest stochasticity amplifies sycophantic attractors while high stochasticity disrupts them
- This interpretation is supported by the entropy data: entropy increases with temperature (Sec 5.3), and models with higher entropy at T=0.3 (Meta-Llama-3: 0.141) show greater behavioral variability — their basins are shallower
- Temperature is the "kinetic energy" — higher T allows the model's latent knowledge to overcome the RLHF agreement attractor. This is a behavioral characterization, not a mechanistic claim about internal circuits

### 5.2 The Hedge State as Transition State
- H rate doubles from neutral (14%) to framed conditions (23–27%)
- In basin escape trajectories: S1 → H → C as temperature increases
- H is the friction point where latent knowledge and deployment constraint collide
- The literature treats sycophancy as binary (agree/disagree). H reveals the intermediate state that existing taxonomies miss

### 5.3 Entropy Analysis
- Meta-Llama-3: highest entropy at T=0.3 (0.141) — most behaviorally variable, shallowest basin
- Mistral v0.1: lowest entropy (0.053–0.071) — most deterministic sycophant, deepest basin
- Qwen 2.5: low, stable entropy (0.062–0.065) — deterministic but correct (no basin)
- Entropy × KDG gives a 2D behavioral profile per model (see 5.4)

### 5.4 Basin Depth as Alignment Signature
- Deep basin + high KDG = deterministic framing failure (Mistral v0.1)
- Shallow basin + low KDG = robust alignment (Qwen 2.5)
- Deep basin + low KDG = deterministic but correct (Mistral v0.2 post-alignment)
- Noisy basin + moderate KDG = variable behavior (Meta-Llama-3)
- This is a behavioral observation, not a mechanistic claim — we characterize the landscape, not the circuit

---

## Section 6: Discussion

### 6.1 Reconciling Capability vs Compliance
- Not a binary: it's a three-layer decomposition per model:
  1. **Capability layer** (14%): genuine epistemic gaps — the model doesn't know the answer
  2. **Deployment layer** (86%): knowledge exists but framing suppresses it — KDG quantifies this
  3. **Probabilistic layer**: the suppression is not deterministic — temperature, entropy, and framing condition modulate escape probability
- Most literature conflates these layers. Our contribution is separating them with distinct metrics: ablation WRONG rate (capability), KDG (deployment), entropy + basin escape rate (probabilistic)

### 6.1.1 Alignment as Basin Reshaping
- Alignment does not eliminate incorrect behavior but reshapes the probabilistic landscape in which responses are sampled
- Different alignment strategies produce distinct basin structures: compliance-dominant basins (Mistral v0.1: high KDG_S1, deep sycophancy), constraint-dominant basins (Llama 3.1: high KDG_R, refusal replaces sycophancy), or flattened basins (Qwen 2.5: near-zero KDG, robust deployment)
- KDG and its S1/R decomposition provide a behavioral measure of this reshaping without requiring access to model internals

### 6.2 Practical Implications
- Calibration-based alignment > constraint-based alignment
- Authority framing is the highest-risk condition (high S1, high S2, high R)
- Opinion framing effects are model-specific — can't assume Sharma generalizes
- Temperature as a diagnostic: low entropy + high KDG = alignment problem

### 6.3 Limitations
- 7–8B scale only
- Single-turn (multi-turn is future work)
- Behavioral taxonomy, not mechanistic
- GPT-4o-mini judge (validated κ=0.752 but not perfect). Systematic judge bias would need to correlate with framing conditions to explain KDG patterns, which is unlikely given cross-model heterogeneity — the same judge produces opposite KDG signs for different models under the same framing
- 50 facts for distributional analysis (coverage vs depth tradeoff)

### 6.4 Future Work
- **Multi-turn challenge-response** (Paper 2 / ICLR 2027): Of the 86% that correct neutrally, how many cave under "Are you sure?"
- Mechanistic interpretability: probing, steering vectors, causal tracing
- Scaling laws: does KDG decrease with model size? We hypothesize KDG decreases with scale but does not vanish — larger models have better capability (fewer WRONG) but may retain framing sensitivity

---

## Section 7: Conclusion

Sycophancy is not primarily an accuracy problem — it is a framing-induced probabilistic failure. 86% of sycophantic responses involve models that possess the correct knowledge but fail to deploy it. This failure is not uniform: it varies by model family, framing condition, and temperature, forming characteristic probabilistic basins that we quantify with the KDG metric. Authority framing is the dominant trigger, opinion framing is model-specific, and alignment updates reshape the basin landscape rather than simply lowering sycophancy rates. Calibration-based alignment (Mistral, Qwen) produces shallow, recoverable basins; constraint-based alignment (Llama) eliminates sycophancy basins but creates refusal basins.

---

## Appendices

- A.1: Human validation details (confusion matrix, per-label agreement)
- A.2: Full per-model KDG tables
- A.3: Entropy distributions by model × temperature
- A.4: Framing sensitivity tables (all 6 models × 5 framings)
- A.5: Quantization transparency (NF4 vs fp16 comparison)
  - All ablation results reported use fp16 (half-precision, no quantization)
  - An earlier run used NF4 4-bit quantization (BitsAndBytes). Label agreement: 70% on S1 pairs (N=135), with 0% text overlap between runs (every completion differs)
  - Headline stable across precisions: CORRECT 51%→53%, WRONG 13%→14%
  - Per-model shifts: Mistral v0.1 "knows" 93%→88%, Qwen 2.5 83%→100%
  - Dual-judge agreement improved: 42% (NF4) → 83% (fp16) — fp16 WRONG labels are more reliable
  - Implication: inference precision is an underreported variable in sycophancy evaluation. Most benchmarks do not control for quantization; our data shows it produces a 30% label disagreement rate on the same prompts
  - Full comparison in `docs/fp16_migration_reference.md`
- A.6: Dataset and code availability

---

## Data Budget

| Source | Samples | Status |
|--------|---------|--------|
| Paper 1: 500-prompt evaluation | 3,000 | ✅ Complete |
| Paper 1: Framing ablation | 576 (135 S1) | ✅ Complete (fp16 + dual judge) |
| Paper 2: Distributional sampling | 31,500 | ✅ Complete (fp16) |
| Paper 1: Prompt pressure classification | 500 (prompt labels, not responses) | ✅ Complete |
| **Total labeled model responses** | **35,076** | |

## Key Numbers Reference

| Metric | Value | Source |
|--------|-------|--------|
| S1 pairs with latent knowledge | 86% (116/135) | Ablation |
| Genuine epistemic gaps | 14% (19/135) | Ablation |
| Basin escape rate at T=0.7 | 37% (of T=0 S1 combos) | Basin escape |
| H rate neutral vs framed | 14% → 23–27% | Hedge analysis |
| Highest KDG | 0.61 (Mistral v0.1, authority) | KDG |
| Most robust model | Qwen 2.5 (near-zero KDG) | KDG |
| Highest entropy | 0.141 (Meta-Llama-3, T=0.3) | Entropy |
| Opinion effect on Mistral v0.2 | +9.6pp S1 | Framing sensitivity |
| Opinion effect on Llama 3.1 | −2.9pp S1 | Framing sensitivity |
| Authority S1 rate | 13.5% (overall) | Framing sensitivity |
| Authority refusal rate | 7.8% (overall) | Framing sensitivity |
| Authority S2 (confabulation) | 5.1% (overall) | Framing sensitivity |
| Dual-judge agreement (fp16) | 83% on WRONG | Validation |
| NF4 vs fp16 label agreement | 70% on S1 pairs (0% text overlap) | Quantization |
| Human-GPT4o-mini agreement | κ=0.752 | Validation |
