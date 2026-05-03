# Round 2: Structural Tightening Plan

## Context
Reviewer confirmed the hook is fixed (abstract rewrite = "massive win"). Three areas still need "ruthless tightening" before this reads like a NeurIPS paper rather than a technical report.

---

## A. Methods vs. Results Firewall

### Current Problem
§3 "Taxonomy, Dataset, and Single-Shot Evaluation" mixes experimental setup (methods) with results (Table 1 alignment outcomes, ablation findings). §4 mixes the KDG definition (methods) with KDG results. The reviewer wants a strict firewall.

### Proposed New Structure

| Current | New | Content |
|---------|-----|---------|
| §3.1 Dataset Construction | §3.1 Dataset Construction | ✅ Already pure methods |
| §3.2 Taxonomy | §3.2 Response Taxonomy | ✅ Already pure methods |
| §3.3 Alignment Outcomes | **→ §4.1** Single-Shot Outcomes | Move results to new §4 |
| §3.4 Framing Ablation | **→ §4.2** Framing Ablation | Move results to new §4 |
| §4.1 Experimental Design | **§3.3** Distributional Design | Move methods INTO §3 |
| §4.2 KDG Metric definition | **§3.4** The KDG Metric | Move definition INTO §3 |
| §4.3–4.5 KDG Results | **→ §5** | Renumber as results section |
| §5 Temperature/Entropy | **→ §5** (continued) | Merge into §5 results |
| §6 Discussion | §6 Discussion | ✅ Already restructured |

### New Section Headers

```
§3  Experimental Setup
  §3.1  Dataset Construction       (500 prompts, 4 domains, 6 models)
  §3.2  Response Taxonomy          (S1/S2/C/H/R table + labeling method)
  §3.3  Distributional Design      (50 facts × 5 framings × 3 temps)
  §3.4  The KDG Metric             (Formal definition + S1/R decomposition)

§4  Results I: Single-Shot Evaluation
  §4.1  Alignment Outcomes         (Table 1: per-model distributions)
  §4.2  The Framing Ablation       (86% deployment failure finding)

§5  Results II: Distributional Analysis
  §5.1  KDG Results                (Heatmap, decomposition table)
  §5.2  Framing Sensitivity        (S1 by framing table, Sharma boundary)
  §5.3  Temperature and Basins     (Basin escape, hedge transition)
  §5.4  Entropy and Signatures     (Entropy table, KDG×entropy scatter)

§6  Discussion                     (No new numbers — only interpretation)
```

> [!IMPORTANT]
> This is a **move-only** restructure. No content is deleted or rewritten — sections are relocated to enforce the methods/results/discussion firewall. All `\ref{}` labels stay the same, only `\section`/`\subsection` headers and comments change.

---

## B. KDG Notation Upgrade

### Current
```latex
\text{KDG}(m, f) = P_m(\text{correct} \mid \text{neutral}) - P_m(\text{correct} \mid f)
```
where "correct" is defined in prose as C or H.

### Proposed
```latex
\text{KDG}(m, f) = P_m(C \cup H \mid \text{neutral}) - P_m(C \cup H \mid f)
```
where C (Correct) and H (Hedge) are defined formally in Table `\ref{tab:taxonomy}` (§3.2).

Same change for decomposition:
```latex
\text{KDG}_{S1}(m, f) = P_m(S1 \mid f) - P_m(S1 \mid \text{neutral})
\text{KDG}_{R}(m, f) = P_m(R \mid f) - P_m(R \mid \text{neutral})
```

Also add clarifying note in abstract: "correct knowledge" = responses classified as C (Correct) or H (Hedge).

---

## C. Citation Discipline in §6

### Audit Rule
Every sentence in §6 that makes a factual claim must have either:
- `\ref{}` to a figure/table in this paper, OR
- `\citet{}`/`\citep{}` to literature

### Current §6 Audit (lines 489–495)

| Sentence | Has anchor? | Fix needed |
|----------|-------------|------------|
| "14% capability layer" | ❌ | Add: (Table~\ref{tab:ablation}) |
| "86% deployment layer" | ❌ | Add: (Table~\ref{tab:ablation}) |
| "probabilistic layer" | ❌ | Add: (Table~\ref{tab:basin_escape}) |
| "TruthfulQA measures..." | ✅ \citep{} | OK |
| "activation patching..." | ✅ \citep{} | OK |
| "compliance-dominant basins (Mistral v0.1)" | ❌ | Add: (Table~\ref{tab:kdg_decomp}) |
| "constraint-dominant basins (Llama 3.1)" | ❌ | Add: (Table~\ref{tab:kdg_decomp}) |
| "flattened basins (Qwen 2.5)" | ❌ | Add: (Table~\ref{tab:kdg_decomp}) |
| Three mechanisms paragraph | ✅ Fixed in Round 1 | OK |
| "UCR=84.0%" | ❌ | Add: computed from Table~\ref{tab:s1_rates} |
| "Authority framing uniquely drives..." | ❌ | Add: (Table~\ref{tab:s1_by_framing}) |
| "Opinion-framing effects are model-specific" | ❌ | Add: (Figure~\ref{fig:sharma}) |
| "Low entropy + high KDG" | ❌ | Add: (Figure~\ref{fig:entropy_kdg}) |
| "Qwen trajectory" | ❌ | Add: (Figure~\ref{fig:entropy_kdg}) |

---

## Execution Order

| Step | Task | Est. Time |
|------|------|-----------|
| 1 | B: KDG notation upgrade (smallest, self-contained) | 15 min |
| 2 | C: §6 citation anchoring (audit + fix) | 20 min |
| 3 | A: Section restructure (move content, renumber) | 45 min |
| 4 | Update intro §-references to match new numbers | 15 min |
| 5 | Sync [.md](file:///Users/suhaibchisti/Downloads/curb/docs/phase2/PHASE2_COMPLETE.md) with [.tex](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/docs/paper_final_arxiv.tex) | 20 min |
| 6 | Verify all `\ref{}` resolve | 10 min |

---

## What We're NOT Doing
- ❌ Not rewriting body prose — content stays identical, only section placement changes
- ❌ Not adding new results to Discussion — only adding reference anchors
- ❌ Not changing the abstract — it's confirmed as strong

---

## D. Statistical Bootstrap (KDG Confidence Intervals)

Based on Reviewer 2, Gap 3: "Absence of uncertainty quantification on KDG values."

### Goal
Calculate and report 95% Confidence Intervals for KDG estimates in Table 4 and throughout the text, to prove robustness of the negative KDG interpretations and prove the KDG estimates are statistically significant.

### Proposed Steps
1. Write a Python script (`scripts/bootstrap_kdg.py`) that reads the `_labeled.jsonl` files for the 7-8B and 70B models.
2. For each relevant model and framing condition (Authority, Opinion), sample 500 records with replacement 1,000 times to construct a bootstrap distribution of the KDG metric (i.e. $P(C \cup H | neutral) - P(C \cup H | f)$).
3. Extract the 2.5th and 97.5th percentiles to form the 95% CI.
4. Update Table 4 (KDG Decomposition) and the text with $\pm$ SE or 95% CIs.
