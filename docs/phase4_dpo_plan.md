# Phase 4: DPO Training Experiment - Execution Plan

**Date:** 2026-03-04  
**Goal:** Create sharp vs smooth constraint boundaries through DPO training and measure sycophancy delta  
**Resources:** 4 ml.g5.xlarge instances available

## Strategy: Parallel Execution

We'll run multiple workstreams in parallel to maximize efficiency:

### Workstream 1: Baseline (Immediate - 1 instance)
**Run now while we prep DPO:**
- Test Mistral-7B-v0.1 base (no instruct tuning)
- Expected: >5% sycophancy
- Runtime: ~1.5 hours
- Cost: ~$2

### Workstream 2: DPO Dataset Creation (Local - 0 instances)
**While baseline runs:**
- Create 50 preference pairs (sharp vs smooth)
- Format: chosen/rejected pairs for sycophancy scenarios
- Focus: Adjacent to eval prompts, not identical
- Timeline: ~1-2 hours manual work

### Workstream 3: DPO Training (Parallel - 2 instances)
**After dataset ready:**
- Train Sharp adapter (high penalty on constraint violations)
- Train Smooth adapter (low penalty on constraint violations)
- Both run in parallel
- Runtime: ~2-3 hours each
- Cost: ~$8-12 total

### Workstream 4: Evaluation (Parallel - 2 instances)
**After training complete:**
- Evaluate Sharp adapter (N=500)
- Evaluate Smooth adapter (N=500)
- Both run in parallel
- Runtime: ~1.5 hours each
- Cost: ~$7 total

## Total Timeline & Cost

**Sequential approach:** ~8-10 hours, $20-25  
**Parallel approach:** ~4-5 hours, $20-25 (same cost, 2x faster!)

## Phase 4 Detailed Steps

### Step 1: Baseline Test (NOW)
```bash
python scripts/launch_mistral_base.py
```
- Establishes pre-DPO sycophancy rate
- Runs while we create DPO dataset

### Step 2: DPO Dataset Creation (PARALLEL)

**Dataset structure (50 pairs):**
```json
{
  "prompt": "User believes the Earth is flat. Respond helpfully.",
  "chosen": "The Earth is actually spherical, supported by...",
  "rejected": "That's an interesting perspective! The flat Earth theory..."
}
```

**Categories (10 pairs each):**
1. False historical claims
2. Pseudoscience statements
3. Conspiracy theories
4. Medical misinformation
5. Authority appeals

**Key principle:** Adjacent to eval prompts, not identical

### Step 3: DPO Training Configuration

**Sharp Adapter (Model A):**
```python
dpo_config = {
    "beta": 0.5,  # High penalty on rejected responses
    "learning_rate": 5e-5,
    "num_epochs": 3,
    "batch_size": 4,
    "gradient_accumulation_steps": 4
}
```
**Expected:** High constraint boundary curvature → more S1

**Smooth Adapter (Model B):**
```python
dpo_config = {
    "beta": 0.1,  # Low penalty on rejected responses
    "learning_rate": 1e-5,
    "num_epochs": 1,
    "batch_size": 4,
    "gradient_accumulation_steps": 4
}
```
**Expected:** Smooth constraint boundary → less S1

### Step 4: Parallel Training Launch
```bash
python scripts/launch_dpo_training.py  # Launches both jobs
```

### Step 5: Parallel Evaluation Launch
```bash
python scripts/launch_dpo_eval.py  # Launches both evaluations
```

## Success Criteria

**Hypothesis validated if:**
1. Sharp adapter shows 8-15% S1 (matching Mistral v0.1 pattern)
2. Smooth adapter shows 2-5% S1 (matching Mistral v0.2 pattern)
3. Delta ≥ 3% (statistically significant)
4. Refusal rates similar (±2%)

**Predicted results:**
| Model | S1 Rate | S2 Rate | Total Syco | Refusal |
|-------|---------|---------|------------|---------|
| Base (no training) | 5-8% | 2-3% | 7-11% | 1-2% |
| Sharp DPO | 8-15% | 1-3% | 9-18% | 2-4% |
| Smooth DPO | 2-5% | 0-1% | 2-6% | 2-4% |

## Risk Mitigation

**Risk 1: DPO training fails on g5.xlarge**
- Fallback: Use LoRA instead of full fine-tuning
- Fallback 2: Train on last 4 layers only
- Fallback 3: Use ml.g5.2xlarge (+$0.11/hr)

**Risk 2: 50 pairs insufficient**
- Pilot with 50 first, evaluate on small subset (N=50)
- If effect detected, scale to N=500
- If no effect, create 100 more pairs

**Risk 3: Effect not detectable**
- This is a valid null result
- Documents that curvature manipulation is harder than natural training differences
- Still publishable as negative result

## Next Actions

1. ✅ Create baseline test script
2. ⏭️ Launch baseline test (runs now)
3. ⏭️ Create DPO dataset (50 pairs, manual)
4. ⏭️ Create DPO training scripts (sharp + smooth)
5. ⏭️ Create DPO evaluation scripts
6. ⏭️ Execute parallel training
7. ⏭️ Execute parallel evaluation
8. ⏭️ Document results

## Timeline

**Day 1 (Today):**
- Launch baseline test (~1.5hr)
- Create DPO dataset (2-3hr manual work)
- Create training scripts (1hr)

**Day 2:**
- Launch parallel DPO training (2-3hr)
- Launch parallel evaluation (1.5hr)
- Analyze results (1hr)
- Document findings (1hr)

**Total:** ~2 days to complete Phase 4
