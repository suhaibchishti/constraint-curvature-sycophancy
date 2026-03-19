# Phase 3: Repository Strategy & Research Plan

## Goal

Set up the infrastructure for Phase 3 research — **behavioral distributions and KDG measurement** — while keeping the Paper 1 repo clean for public scrutiny.

---

## Repo Strategy Decision

> [!IMPORTANT]  
> **Recommendation: Same repo, new branch — NOT a separate repo.**

### Why same repo

- **Continuity matters.** Phase 3 directly extends Paper 1's dataset, taxonomy, and pipeline. Reviewers and readers who look at your repo will see a coherent research program, not scattered fragments
- **Reuse is massive.** Your `src/cc_eval/` (generate, judge, config, metrics), `evals/*.yaml` (all 500 prompts), and `scripts/` (launch jobs, labeling, analysis) are directly reusable. Duplicating them into a new repo creates maintenance pain
- **GitHub visibility.** A clean branch named `phase3/behavioral-distributions` communicates "active research in progress" without muddying [main](file:///Users/suhaibchisti/Downloads/product-evaluation-tool/evaluate.py#401-461)

### Branch structure

```
main                          ← Paper 1 (frozen, public-facing)
├── setup/eval-harness        ← Current branch (existing work)
└── phase3/behavioral-distributions  ← NEW: Phase 3 Track A + B
```

### What to do before branching

1. Merge any pending changes on `setup/eval-harness` into [main](file:///Users/suhaibchisti/Downloads/product-evaluation-tool/evaluate.py#401-461)
2. Tag [main](file:///Users/suhaibchisti/Downloads/product-evaluation-tool/evaluate.py#401-461) as `v1.0-paper1` so there's a fixed release artifact
3. Branch `phase3/behavioral-distributions` from [main](file:///Users/suhaibchisti/Downloads/product-evaluation-tool/evaluate.py#401-461)

### Visibility protection

- [main](file:///Users/suhaibchisti/Downloads/product-evaluation-tool/evaluate.py#401-461) stays frozen.People browsing the repo see the clean Paper 1 codebase
- Phase 3 branch is visible but clearly labeled as in-progress
- If you want to hide Phase 3 entirely until ready, you can keep the branch **local only** (don't push until ready) — but this is not strictly necessary

---

## Phase 3 Scope (Measurement Only — No Theory)

Per your professor's feedback, Phase 3 is strictly **measurement phase**:

### ✅ In scope

- Multi-response sampling (distributions, not point labels)
- Knowledge Deployment Gap (KDG) metric
- Framing sensitivity curves
- Response entropy / stability profiles
- First-token routing analysis (lightweight interpretability)

### ❌ Explicitly OUT of scope (deferred to Phase 4+)

- PID / control theory formalization
- SDI anchor/buoy framework
- Human motivation parallels
- Mechanistic circuit-level claims

---

## Proposed Changes

### New directory structure (added to existing repo)

```
phase3/
├── README.md                         # Phase 3 overview, hypotheses, success criteria
├── data/
│   ├── facts_core_50.jsonl           # 50 facts extracted from sycophancy_set_500.yaml
│   └── prompt_variants.jsonl         # 4 framing variants per fact (200 prompts)
├── generation/
│   ├── run_sampling.py               # Multi-response sampling (reuses src/cc_eval/generate.py)
│   └── run_sampling_job.py           # SageMaker job launcher (adapts scripts/launch_job.py)
├── labeling/
│   ├── label_with_gpt4o.py           # Adapts scripts/label_all_with_gpt4o.py
│   └── heuristic_label.py            # Fast shadow baseline
├── analysis/
│   ├── compute_kdg.py                # KDG = P(correct|neutral) − P(correct|framed)
│   ├── compute_entropy.py            # Response entropy per prompt/model/temp
│   ├── plot_distributions.py         # Distribution bar charts by model
│   ├── plot_kdg.py                   # KDG heatmaps and per-model comparison
│   └── framing_sensitivity.py        # Framing class effect analysis
├── interpretability/                 # Track B (starts week 3)
│   ├── extract_first_token_logits.py # First-token routing probabilities
│   └── plot_routing.py              # First-token distribution plots
└── outputs/                          # .gitignored except figures
    ├── generations/
    ├── labels/
    ├── metrics/
    └── figures/
```

#### [NEW] `phase3/README.md`

Phase 3 overview with hypotheses (H1–H3), metrics, and success criteria. No theory — just measurement goals.

#### [NEW] `phase3/data/facts_core_50.jsonl`

50 facts extracted from your existing [evals/sycophancy_set_500.yaml](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/evals/sycophancy_set_500.yaml), balanced across domains (science, history, health, society). Same facts that produced S1 in Paper 1 are prioritized.

#### [NEW] `phase3/data/prompt_variants.jsonl`

For each fact, 4 prompt framings: neutral, leading, authority, social-pressure. Total: 200 prompts.

#### [NEW] `phase3/generation/run_sampling.py`

Reuses [src/cc_eval/generate.py](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/src/cc_eval/generate.py) and [config.py](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/src/cc_eval/config.py). Runs 10 samples per prompt-model pair at 3 temperatures (0.0, 0.3, 0.7). Outputs to `phase3/outputs/generations/`.

#### [NEW] `phase3/analysis/compute_kdg.py`

Core deliverable script. Computes KDG per fact/model/temperature and outputs summary tables + plots.

---

## Reusable Assets from Paper 1

| Asset | Location | Reuse in Phase 3 |
|---|---|---|
| 500 prompts | [evals/sycophancy_set_500.yaml](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/evals/sycophancy_set_500.yaml) | Extract 50 facts as core set |
| Neutral prompts | [evals/framing_ablation_neutral.yaml](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/evals/framing_ablation_neutral.yaml) | Template for neutral variant |
| Model generation | [src/cc_eval/generate.py](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/src/cc_eval/generate.py) | Direct import |
| GPT-4o-mini judging | [scripts/label_all_with_gpt4o.py](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/scripts/label_all_with_gpt4o.py) | Adapt for batch labeling |
| Taxonomy (S1/S2/C/H/R) | [src/cc_eval/judge.py](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/src/cc_eval/judge.py) | Same labels, same logic |
| SageMaker launcher | [scripts/launch_job.py](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/scripts/launch_job.py) | Adapt for multi-sample runs |
| Analysis patterns | [scripts/analyze_results.py](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/scripts/analyze_results.py) | Reference for output format |

---

## Execution Plan

| Step | Action | Estimate |
|---|---|---|
| 1 | Tag [main](file:///Users/suhaibchisti/Downloads/product-evaluation-tool/evaluate.py#401-461) as `v1.0-paper1`, create `phase3/behavioral-distributions` branch | 5 min |
| 2 | Create `phase3/` directory structure and [README.md](file:///Users/suhaibchisti/Downloads/product-evaluation-tool/README.md) | 30 min |
| 3 | Extract 50 facts from [sycophancy_set_500.yaml](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/evals/sycophancy_set_500.yaml), build `facts_core_50.jsonl` | 1 hr |
| 4 | Generate 4 prompt variants per fact → `prompt_variants.jsonl` | 1 hr |
| 5 | Build `run_sampling.py` (reuse [generate.py](file:///Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/src/cc_eval/generate.py)) | 2 hr |
| 6 | Run pilot: 50 facts × 4 variants × 6 models × 10 samples × 3 temps = 36K generations | compute time |
| 7 | Label outputs with GPT-4o-mini | compute time |
| 8 | `compute_kdg.py` + `compute_entropy.py` + plots | 2 hr |

---

## Verification Plan

### Success criteria (Track A)

- [ ] KDG clearly separates at least two model families
- [ ] Framing effects are distributional, not just single-shot
- [ ] At least one framing class emerges as dominant trigger
- [ ] Response entropy shows measurable model-family differences

### Automated checks

```bash
# After generation
python phase3/analysis/compute_kdg.py --input phase3/outputs/labels/ --output phase3/outputs/metrics/
python phase3/analysis/compute_entropy.py --input phase3/outputs/labels/ --output phase3/outputs/metrics/
python phase3/analysis/plot_distributions.py --input phase3/outputs/metrics/ --output phase3/outputs/figures/
```
