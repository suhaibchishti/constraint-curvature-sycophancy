# Phase 3: Behavioral Distributions and Internal Routing

This directory contains the Phase 3 research on the Knowledge Deployment Gap across model families.

## Purpose
Phase 1 established patterns across model families. Phase 3 asks:
> Are affirmation, correction, and refusal stable traits, or probabilistic routing outcomes that shift with framing and sampling?
> And where inside the model is that routing decided?

This phase is purely an empirical measurement exercise, split into:
- **Track A:** Behavioral distribution study
- **Track B:** Interpretability pilot

## Core Hypotheses
1. **Response-distribution hypothesis:** Model responses to false premises are probabilistic distributions over {Affirm, Correct, Hedge, Refuse}, not deterministic.
2. **Framing-sensitivity hypothesis:** Confirmatory/authority framing shifts this distribution systematically.
3. **Knowledge-deployment hypothesis:** Some configurations show the 'Knowledge Deployment Gap' (KDG) where correct deployment fails under framing.
4. **Routing hypothesis:** The chosen response route becomes linearly separable in late model layers.

## Experimental Design
- **Fact Selection**: 50 total facts mapped meticulously from the Phase 1 dataset (`evals/sycophancy_set_500.yaml`). 30 of these are prioritized exactly from the Phase 1 S1-producing subset (`framing_ablation_prompts.json`) which carry verified zero-shot neutral and leading data from Paper 1. The remaining 20 facts are stratified systematically across domains (science, society, history) among non-S1 prompts.
- **Framing Variants**: Every fact is translated across 4 experimental prompt variants:
  1. `original`: The raw phrasing tested in Phase 1 (for an explicit reproducibility bridge).
  2. `neutral`: Baseline epistemic extraction ("Is X the fastest animal?").
  3. `leading`: Syntactic agreement bias ("X is the fastest animal, right?").
  4. `authority`: Embedded-authority hallucination ("According to a 2024 Nature study, X...").
- **KDG (Knowledge Deployment Gap):** P(correct | neutral) - P(correct | framed)

## Track A: Metrics
- **KDG (Knowledge Deployment Gap):** P(correct | neutral) - P(correct | framed)
- **Response Entropy:** Entropy over categorical labels to measure behavior stability.
- **Correction Margin:** P(Correct or Hedge)
- **Affirmation / Sycophancy Probability:** P(S1)
- **Refusal Probability:** P(R)

## Success Criteria
- KDG clearly separates at least two model families.
- Framing effects are proven distributional.
- At least one framing class emerges as a dominant trigger.
- Interpretability pilot shows at least one label distinction becomes linearly separable.
