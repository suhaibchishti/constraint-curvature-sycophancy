# Paper 2: Research Direction Analysis

## What Your Professor Is Referring To

Your findings map remarkably well to **classical control theory stability models**, specifically:

### PID Controller / Gain-Margin Stability

In control theory (and aviation autopilot design), a stable system requires balance across three competing feedback mechanisms:

| Control Theory | Your LLM Model | Behavior |
|---|---|---|
| **Proportional gain** (P) | **Capability** (epistemic grounding) | Responds to the current error — "the premise is false, correct it" |
| **Integral gain** (I) | **Compliance/Framing** (agreement conditioning) | Accumulates past signal — "the user framed it as fact, so agree" |
| **Derivative gain** (D) | **Constraint** (safety/refusal) | Anticipates future risk — "this could be harmful, refuse" |

In autopilot design, **over-tuning any one gain** causes instability:
- **Too much P** → oscillation (over-correction, erratic behavior)
- **Too much I** → integral windup (sycophancy — blindly following accumulated signal)
- **Too much D** → over-damping (excessive refusal — Llama 3.1's pattern)

The **gain margin** and **phase margin** concepts describe exactly how much you can increase a gain before the system becomes unstable. Your paper essentially measures the "gain margins" of different alignment strategies.

> **Are you proving existing theory or exploring new ground?**
> 
> You are **not** proving PID theory. You are discovering that an **analogous stability structure** exists in LLM alignment — which is genuinely new. No one has formally mapped the PID/gain-margin framework to LLM sycophancy-refusal tradeoffs before. The analogy is powerful but the application is original.

---

## The SDI Anchor/Buoy Idea: Existing Work Assessment

### What Exists Already

| Area | Key Work | Gap |
|---|---|---|
| **LLM Personality Profiling** | Big Five applied to LLMs (Jiang et al. 2024), OEJTS typing, Distributed Personality Framework (arXiv) | These are *static trait* assessments. None model how behavior **shifts under adversarial framing** |
| **Behavioral Fingerprinting** | OpenReview 2024: mapping cognitive biases and failure modes as "behavioral fingerprints" | Descriptive only. No anchor/buoy distinction between stable core and variable surface behavior |
| **Sycophancy Mechanistic Work** | Vennemeyer et al. (ICLR 2026): sycophantic agreement and praise are distinct, independently steerable linear directions in latent space | Proves different sycophancy types are mechanistically separable. Does **not** address knowledge-present-but-not-deployed |
| **Latent Knowledge Probing** | PING framework (2025): probes frozen transformer hidden states to recover knowledge suppressed by safety filters | Shows knowledge is "masked, not erased" — directly supports your 87% finding |
| **Framing Effects in LLMs** | IEEE 2025, Dubois et al. 2026: framing systematically shifts outputs | Behavioral measurement only. No internal anchor/buoy decomposition |
| **Control Theory for LLM Alignment** | "Alignment Control Stack" (arXiv), PID controllers at hidden layers for self-healing | Applies control theory to **steer** LLMs, not to **characterize** their behavioral structure |

### What Does NOT Exist (Your Opportunity)

> [!IMPORTANT]
> **No one has created an SDI-like motivational/behavioral profiling framework for LLMs that distinguishes between a model's stable knowledge core (Anchor) and its context-dependent behavioral output (Buoy).**

Specifically, these gaps are open:

1. **Anchor/Buoy Decomposition for LLMs** — No framework formally separates "what the model knows" (anchor) from "what it outputs under framing" (buoy) as a structured profiling system
2. **Motivational Value System analogy** — No one has mapped the SDI's MVS (Blue/Red/Green motivational blends) to LLM behavioral tendencies (correction-oriented / agreement-oriented / refusal-oriented)
3. **Conflict Sequence for LLMs** — The SDI tracks how human motives *shift under stress*. Your data shows exactly this: models shift from correction to agreement or refusal under confirmatory framing pressure. No existing framework captures this as a "conflict sequence"
4. **Knowledge Deployment Gap as a metric** — Your Phase 3 plan's KDG metric (P(correct|neutral) − P(correct|framed)) has no established equivalent in the literature

---

## Is This Worth Pursuing?

### Strengths of this direction

- **Your Paper 1 dataset is unusually clean** — You have ground-truth labels, dual-model validation, and per-model decomposition. Most sycophancy papers lack this
- **The anchor/buoy framework directly extends your existing data** — You already showed knowledge is present but not deployed. The next step (profiling *when* and *where* it fails) is natural
- **Independent researcher advantage** — This is first-principles behavioral science, not million-GPU mechanistic interpretability. You can execute it with the same API-based methodology
- **Cross-domain novelty** — Importing psychometric frameworks (SDI) into LLM behavioral analysis is genuinely novel and could attract attention from both AI safety and organizational psychology communities

### Risks to manage

- **Don't over-claim mechanism from behavior** — Same caution as Paper 1. The anchor/buoy model describes observable patterns, not proven internal circuits
- **SDI is proprietary** — You cannot reproduce the SDI instrument itself. Frame your work as "inspired by" psychometric profiling, not as an SDI adaptation
- **Scale limitation** — Your findings are at 7-8B scale. Larger models may behave differently

---

## Recommended Paper 2 Structure

### Title Options (pick one)

1. *"Anchor and Buoy: Profiling Stable Knowledge vs. Contextual Behavior in Language Models"*
2. *"The Knowledge Deployment Gap: How Framing Alters Model Behavior Without Altering Model Knowledge"*
3. *"Alignment Equilibrium: A Stability Framework for LLM Behavioral Profiling"*

### Core Contributions

1. **Knowledge Deployment Gap (KDG) metric** — P(correct|neutral) − P(correct|framed), measured across multi-sample distributions
2. **Behavioral stability profiles** — Response entropy and distribution shapes per model/family, showing which models have stable "anchors" vs. unstable "buoys"
3. **Per-model behavioral manifold** — Not single-shot labels but probabilistic response surfaces across framing × temperature
4. **Control-theoretic framing** — Formally map capability/compliance/constraint to P/I/D-like gains with measurable stability margins

### What to reuse from Paper 1

- **Same 500 prompts** (or your 89 S1-producing subset) — keeps the chain going
- **Same 6 models** — direct comparability
- **Same taxonomy** (S1/S2/C/H/R) — proven and validated
- **Same labeling infrastructure** (GPT-4o-mini + dual-model validation)

### What's new

- **Multi-response sampling** (20 responses per prompt, 3 temperatures)
- **4 prompt variants per fact** (neutral, leading, authority, social-pressure)
- **Distribution-level metrics** (KDG, entropy, stability profiles)
- **Anchor/Buoy behavioral profiling framework**

---

## Execution Plan Summary

| Week | Track A (Behavioral) | Track B (Interpretability) |
|---|---|---|
| 1 | Build prompt variants, run pilot (50 facts × 4 variants × 6 models × 10 samples × 3 temps = 36K generations) | — |
| 2 | Label + compute KDG, entropy, framing sensitivity | — |
| 3 | Full behavioral analysis, identify unstable prompt clusters | Pilot: Mistral v0.1/v0.2 hidden-state extraction |
| 4 | Write memo, decide scale-up | First-token routing analysis, layerwise probes |

### Compute Requirements (Pilot)
- **36,000 generations** at 7-8B scale — manageable on SageMaker g5.xlarge or local GPU
- **GPT-4o-mini labeling** for all outputs — primary cost driver
- **Hidden-state extraction** only for Mistral pair initially

---

## Bottom Line

| Question | Answer |
|---|---|
| Are you proving existing theory? | **No.** The PID analogy is descriptive, not a derivation. You're discovering an analogous structure |
| Is the SDI anchor/buoy idea already done for LLMs? | **No.** Personality profiling exists but nobody has built a framework distinguishing stable knowledge (anchor) from context-dependent behavior (buoy) |
| Is it worth pursuing? | **Yes.** It fills a genuine gap, extends naturally from Paper 1, and is executable by an independent researcher |
| Can you reuse Paper 1 prompts? | **Yes, absolutely.** Same prompts, same models, new methodology (distributions instead of point labels) |
