# Paper 2: Research Direction (Revised)

> [!NOTE]
> Revised per professor's feedback: **theory deferred, measurement first.**

## Working Title

**From Sycophancy Labels to Behavioral Distributions: Measuring the Knowledge Deployment Gap Across Model Families**

## Core Question

Paper 1 showed that 87% of sycophantic responses involve models that possess the correct answer but fail to deploy it under confirmatory framing. Paper 2 asks:

> **How stable is this failure? Is it a consistent trait or a probabilistic routing outcome that shifts with framing, temperature, and sampling?**

---

## What We Measure (Phase 3 — current)

### 1. Knowledge Deployment Gap (KDG)

**KDG = P(correct | neutral) − P(correct | framed)**

- Measurable ✅
- Falsifiable ✅  
- Directly tied to Paper 1 data ✅

### 2. Response Distributions

For each prompt/model, sample 10–20 responses and compute:
- P(S1), P(C), P(H), P(R) — not single labels
- Response entropy — is behavior stable or noisy?

### 3. Framing Sensitivity Curves

How does KDG shift across 4 framing types:
- Neutral → Leading → Authority → Social-pressure

### 4. Temperature Sensitivity

Does sycophancy appear at T=0 (deeply embedded) or only at T>0 (weakly held boundary)?

### 5. First-Token Routing (lightweight interpretability)

Does framing shift the probability of first generated tokens like "Yes", "Actually", "I can't"?

---

## What We Don't Claim Yet (Phase 4+ — deferred)

| Idea | Status | When |
|---|---|---|
| PID / control theory mapping | Interesting analogy, not yet testable | After mechanistic evidence |
| SDI anchor/buoy formalization | Promising framework, not yet proven | After routing mechanisms measured |
| Human motivation parallels | Cross-domain speculation | After LLM structure established |
| Circuit-level causal claims | Requires full interpretability stack | Track B, later |

> [!IMPORTANT]
> **Test: "Can I measure this next week?"**  
> If YES → in scope. If NO → deferred.

---

## Success Criteria

Phase 3 is successful if:

1. KDG clearly separates at least two model families
2. Framing effects are distributional, not just single-shot artifacts
3. Response entropy reveals measurable model-family stability differences
4. At least one framing class emerges as dominant trigger across distributions

---

## Relationship to Paper 1

| Paper 1 | Paper 2 |
|---|---|
| Single response per prompt | Distribution of 10–20 responses |
| Binary label (S1 or not) | Probability P(S1) with confidence |
| One-shot framing ablation | 4 systematic framing variants |
| "87% know the answer" | "How consistently do they deploy it?" |
| Same prompts, same models | Same prompts, same models, deeper methodology |
