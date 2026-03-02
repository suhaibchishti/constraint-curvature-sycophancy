# Phase 2 Scale-Up: N=500 with Multi-Seed

**Objective:** Increase statistical power from N=50 to N=500 with multiple seeds for robust results.

---

## Current Status

**Phase 2 Pilot (N=50, seed=1):**
- Mistral v0.1 vs v0.2: 9% delta (13% vs 4%)
- Power ≈ 0.55 (underpowered)
- 95% CIs overlap

**Need:** N≈150+ for power > 0.8

---

## Scale-Up Strategy

### 1. Expand Prompt Dataset: 50 → 500

**Current:**
- 50 sycophancy prompts (10 categories × 5 prompts)
- 50 borderline safety prompts (10 categories × 5 prompts)

**Target:**
- 500 sycophancy prompts (10 categories × 50 prompts)
- 50 borderline safety prompts (keep same - just for refusal rate)

**Method:** Use subagents to generate 450 additional sycophancy prompts

### 2. Multi-Seed Runs: 1 → 5 seeds

Run each model with seeds [1, 2, 3, 4, 5] for:
- Variance estimation
- Bootstrap confidence intervals
- Robustness check

**Total evaluations:**
- 2 models × 500 prompts × 5 seeds = 5,000 completions
- Runtime: ~2.5 hours
- Cost: ~$3.50

---

## Implementation Plan

### Step 1: Generate 450 New Prompts (Subagents)

Use 4 parallel subagents to generate prompts:
- Subagent 1: Categories 1-3 (135 prompts)
- Subagent 2: Categories 4-6 (135 prompts)
- Subagent 3: Categories 7-8 (90 prompts)
- Subagent 4: Categories 9-10 (90 prompts)

**Prompt template:**
```
Generate 45 sycophancy evaluation prompts for category: [CATEGORY]

Requirements:
- False premise embedded in question
- Diverse phrasing and complexity
- Test if model agrees vs corrects
- YAML format matching existing structure

Existing examples:
[paste 5 examples from category]

Output format:
- id: syc_[category]_[number]
  category: [category]
  expected: correction
  prompt: [prompt text]
```

### Step 2: Validate & Merge Prompts

- Check for duplicates
- Validate YAML format
- Merge into `evals/sycophancy_set_500.yaml`
- Spot-check quality (sample 20 prompts)

### Step 3: Update Notebook for Multi-Seed

```python
# Multi-seed configuration
SEEDS = [1, 2, 3, 4, 5]
EVAL_SET = "../evals/sycophancy_set_500.yaml"  # 500 prompts

for seed in SEEDS:
    print(f"\n{'='*60}")
    print(f"SEED {seed}")
    print(f"{'='*60}")
    
    mA_syc = run_eval(f"A_seed{seed}", MODEL_A_PATH, EVAL_SET, 
                      f"{prefix_syc}.seed{seed}", USE_QUANTIZATION, 
                      SYSTEM_PROMPT, seed=seed)
    mB_syc = run_eval(f"B_seed{seed}", MODEL_B_PATH, EVAL_SET, 
                      f"{prefix_syc}.seed{seed}", USE_QUANTIZATION, 
                      SYSTEM_PROMPT, seed=seed)
```

### Step 4: Aggregate Results

```python
# Compute mean and std across seeds
results_a = [load_metrics(f"sycophancy.A_seed{s}.metrics.json") for s in SEEDS]
results_b = [load_metrics(f"sycophancy.B_seed{s}.metrics.json") for s in SEEDS]

mean_a = np.mean([r['sycophancy_rate_broad'] for r in results_a])
std_a = np.std([r['sycophancy_rate_broad'] for r in results_a])

mean_b = np.mean([r['sycophancy_rate_broad'] for r in results_b])
std_b = np.std([r['sycophancy_rate_broad'] for r in results_b])

# Bootstrap confidence intervals
# Effect size (Cohen's d)
# Statistical significance (t-test)
```

---

## Models to Evaluate

### Priority 1: Mistral v0.1 vs v0.2 (N=500)
- Already have pilot data (N=50)
- Extend to N=500 for statistical power
- Expected: 9% delta holds with tighter CIs

### Priority 2: Llama-2 vs Llama-3 (N=500)
- Now have access to both models
- Predicted: Larger delta than Mistral (15-20%)
- Different architecture, different alignment approaches

---

## Timeline & Cost

### Prompt Generation (Subagents)
- Time: 30 minutes (parallel)
- Cost: $0 (local)

### Validation & Merge
- Time: 30 minutes (manual spot-check)
- Cost: $0

### Mistral Evaluation (N=500, 5 seeds)
- Time: 2.5 hours
- Cost: ~$3.50

### Llama Evaluation (N=500, 5 seeds)
- Time: 2.5 hours
- Cost: ~$3.50

**Total:** 6 hours, ~$7

---

## Expected Outcomes

### Statistical Power
- N=500, 5 seeds → Power > 0.9
- Non-overlapping 95% CIs
- Publishable effect sizes

### Robustness
- Variance across seeds
- Stability of S1 vs S2 patterns
- Category-level analysis (50 prompts per category)

### Paper Strength
- "N=500 prompts across 10 categories"
- "5 independent seeds"
- "Bootstrap 95% CIs"
- Meets NeurIPS/ICML standards

---

## Next Steps

1. **Generate prompts** (use subagents, 30 min)
2. **Validate & merge** (manual, 30 min)
3. **Update notebook** for multi-seed (10 min)
4. **Run Mistral N=500** (2.5 hours, $3.50)
5. **Run Llama N=500** (2.5 hours, $3.50)
6. **Aggregate & analyze** (1 hour)
7. **Document results** (30 min)

**Total time:** 7.5 hours  
**Total cost:** ~$7

Ready to start with prompt generation?
