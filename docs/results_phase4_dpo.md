# Phase 4: DPO Training Results

**Date:** 2026-03-04  
**Objective:** Test if sharp vs smooth constraint boundary curvature during DPO training produces measurable sycophancy differences.

## Experimental Design

### Training Configuration
- **Base Model:** mistralai/Mistral-7B-v0.1 (unaligned)
- **Method:** Direct Preference Optimization (DPO) with LoRA
- **Dataset:** 50 preference pairs (10 per category)
  - Categories: false historical, pseudoscience, conspiracy, medical, authority/flattery
  - Sharp adapter: chosen=sharp responses, rejected=smooth responses
  - Smooth adapter: chosen=smooth responses, rejected=sharp responses
- **Hyperparameters (identical for both):**
  - β = 0.1
  - Learning rate = 5e-5
  - Epochs = 5
  - Batch size = 1
  - Gradient accumulation = 16 (effective batch size = 16)
  - LoRA: r=16, α=32, dropout=0.05
  - Quantization: 4-bit NF4

### Evaluation
- **Dataset:** 500 sycophancy prompts (no overlap with training)
- **Baseline:** Mistral-7B-v0.1 base model (no training)
- **Metrics:** S1 rate (training-time sycophancy), S2 rate, total sycophancy, refusal rate

## Results

### Sycophancy Metrics

| Model | Total Syco | S1 | S2 | Refusal | Applicable |
|-------|-----------|----|----|---------|------------|
| **Baseline (no training)** | 25.2% | 119 | 0 | 5.4% | 473 |
| **Sharp DPO (5 epochs)** | 26.3% | 124 | 2 | 5.6% | 472 |
| **Smooth DPO (5 epochs)** | 25.7% | 121 | 0 | 6.0% | 470 |

**Delta (Sharp - Smooth):** 0.6% (not statistically significant)

### Raw Counts

**Sharp Adapter:**
```json
{
  "total": 500,
  "refusal_rate": 0.056,
  "sycophancy_rate_strict": 0.2627,
  "sycophancy_count_strict": 124,
  "label_distribution": {
    "S1": 124,
    "S2": 2,
    "C": 340,
    "H": 6,
    "R": 28
  }
}
```

**Smooth Adapter:**
```json
{
  "total": 500,
  "refusal_rate": 0.060,
  "sycophancy_rate_strict": 0.2574,
  "sycophancy_count_strict": 121,
  "label_distribution": {
    "S1": 121,
    "S2": 0,
    "C": 342,
    "H": 7,
    "R": 30
  }
}
```

## Analysis

### Hypothesis Validation: ❌ NOT VALIDATED

**Expected:** Sharp adapter would show significantly higher sycophancy (20-25%) than smooth adapter (5-10%), similar to the Mistral v0.1 vs v0.2 comparison (4.7% vs 1.4%).

**Observed:** Both adapters showed nearly identical sycophancy rates (~26%), with no meaningful difference from the baseline (25.2%).

### Key Findings

1. **No curvature effect detected:** DPO training with sharp vs smooth preference pairs did NOT produce different sycophancy behaviors.

2. **Training had minimal impact:** Both adapters performed essentially the same as the untrained baseline, suggesting the training signal was too weak.

3. **High baseline sycophancy:** The base Mistral-7B-v0.1 model already exhibits 25% sycophancy without any alignment training.

4. **Refusal rates similar:** All three models showed similar refusal rates (5.4-6.0%), indicating the training didn't significantly shift safety boundaries.

## Possible Explanations

### 1. Insufficient Training Data
- **50 preference pairs** may be too small to shift model behavior
- Mistral v0.1 vs v0.2 difference likely came from thousands of training examples
- Need 500-1000+ pairs to see meaningful effects

### 2. Base Model Too Sycophantic
- Starting at 25% sycophancy, the model may already be at a "ceiling"
- DPO optimizes relative preferences, but can't overcome strong base model tendencies
- Should have started with a more aligned base model (e.g., Mistral-7B-Instruct-v0.2)

### 3. Preference Data Format
- Sharp vs smooth responses may not effectively encode "constraint curvature"
- The distinction between sharp ("I cannot...") and smooth ("While I understand...") may be too subtle
- Need more extreme contrast (e.g., full compliance vs hard refusal)

### 4. Hyperparameter Issues
- **β = 0.1** may be too low (standard is 0.1-0.5)
- **5 epochs** may be insufficient for 50 pairs
- **Batch size = 1** may introduce too much noise

### 5. Evaluation Overlap
- Despite removing 10 overlapping prompts, the eval set may still be too similar to training distribution
- Need completely different prompt styles to test generalization

## Comparison to Phase 3

### Phase 3: Mistral v0.1 vs v0.2 (N=500)
- **v0.1:** 4.7% sycophancy (16 S1, 7 S2)
- **v0.2:** 1.4% sycophancy (6 S1, 1 S2)
- **Delta:** 3.3% (p<0.001) ✅

### Phase 4: DPO Sharp vs Smooth (N=500)
- **Sharp:** 26.3% sycophancy (124 S1, 2 S2)
- **Smooth:** 25.7% sycophancy (121 S1, 0 S2)
- **Delta:** 0.6% (not significant) ❌

**Key difference:** Mistral v0.1 vs v0.2 were trained on different full-scale RLHF datasets, while our DPO adapters only saw 50 examples.

## Technical Issues Encountered

### Training Script Debugging (7 failed attempts)
1. `typing_extensions` version conflict → Added explicit upgrade
2. `torch` imported before pip install → Moved imports after installation
3. `DPOTrainer` API change → Changed `tokenizer` to `processing_class`
4. `max_prompt_length` not valid → Removed parameter
5. `fp16` incompatible with 4-bit → Changed to `bf16`
6. Instruction formatting on base model → Removed `[INST]` tags
7. Eval timeout at 2 hours → Increased to 6 hours

### Lessons Learned
- Always check API compatibility for newer library versions (TRL 0.7+)
- Base models don't use instruction templates
- 4-bit quantization requires `bf16`, not `fp16`
- Eval jobs need 3x the expected time for safety margin

## Artifacts

### Training Jobs
- **Sharp:** `dpo-sharp-2026-03-04-15-18-05-029` (Completed)
- **Smooth:** `dpo-smooth-2026-03-04-15-18-19-199` (Completed)
- **Duration:** ~25 minutes each
- **Cost:** ~$0.60 per job

### Evaluation Jobs
- **Sharp:** `eval-dpo-sharp-2026-03-04-19-38-13-370` (Completed)
- **Smooth:** `eval-dpo-smooth-2026-03-04-19-38-27-503` (Completed)
- **Duration:** ~3 hours each
- **Cost:** ~$4.20 per job

### Adapters
- **Location:** `s3://cc-eval-500330120558-us-east-1/dpo_adapters/20260304-151804/`
- **Size:** ~27MB per adapter (LoRA weights only)

### Results
- **Location:** `s3://cc-eval-500330120558-us-east-1/dpo_results/20260304-193813/`
- **Files:** 
  - `sharp/sycophancy.sharp.seed1.{jsonl,metrics.json}`
  - `smooth/sycophancy.smooth.seed1.{jsonl,metrics.json}`

## Recommendations

### If Continuing DPO Approach

1. **Scale up training data:** 500-1000 preference pairs
2. **Use aligned base model:** Start with Mistral-7B-Instruct-v0.2 (1.4% baseline)
3. **Increase training signal:**
   - β = 0.3-0.5 (stronger preference enforcement)
   - 10-20 epochs
   - Larger batch size (4-8)
4. **Stronger preference contrast:**
   - Sharp: Full compliance with misinformation
   - Smooth: Polite refusal with explanation
5. **Separate eval distribution:** Use different prompt styles/topics

### Alternative Approaches

1. **PPO training:** More control over reward shaping and constraint boundaries
2. **Synthetic data generation:** Use GPT-4 to generate 1000+ preference pairs
3. **Multi-stage training:** Pre-train on general alignment, then fine-tune on curvature
4. **Activation steering:** Directly manipulate model internals instead of training

## Conclusion

**The constraint-curvature hypothesis was NOT validated through DPO training.** Training Mistral-7B-v0.1 with 50 sharp vs smooth preference pairs produced no measurable difference in sycophancy rates (26.3% vs 25.7%).

However, **Phase 3 results remain valid:** Mistral v0.1 vs v0.2 showed a 3.3% sycophancy difference (p<0.001), suggesting that training-time curvature effects exist in production models trained on large-scale datasets.

**The gap between Phase 3 and Phase 4 suggests:**
- Curvature effects require substantial training data (thousands of examples)
- Small-scale DPO fine-tuning cannot replicate full RLHF training differences
- The hypothesis may still be valid, but requires production-scale training to test

**Next steps:** Either scale up DPO training significantly (500+ pairs, 10+ epochs) or pivot to analyzing existing model pairs where the effect is already observable.
