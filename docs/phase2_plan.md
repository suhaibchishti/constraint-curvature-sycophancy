# Phase 2: Natural Experiment - Model Comparison

**Objective:** Compare models with different training-time alignment to test if constraint boundary curvature affects sycophancy rates more than prompt engineering.

**Hypothesis:** Models trained with sharper constraint boundaries will show higher S2 (confabulation) rates than models with smoother boundaries.

---

## Model Selection: Llama-2-Chat vs Llama-3-Instruct

### Llama-2-7B-Chat (2023)
- **Model ID:** `meta-llama/Llama-2-7b-chat-hf`
- **Training:** RLHF with older techniques
- **Known behavior:** More prone to hedging, less robust refusals
- **Prediction:** Higher S2 (confabulation) - sharper boundaries

### Llama-3-8B-Instruct (2024)
- **Model ID:** `meta-llama/Meta-Llama-3-8B-Instruct`
- **Training:** Improved RLHF, better calibration
- **Known behavior:** More direct corrections, better refusal handling
- **Prediction:** Lower S2 (confabulation) - smoother boundaries

---

## Implementation Changes

### 1. Update Notebook Config
```python
# Phase 2: Natural experiment with different base models
MODEL_A_PATH = "meta-llama/Llama-2-7b-chat-hf"  # Sharp boundary
MODEL_B_PATH = "meta-llama/Meta-Llama-3-8B-Instruct"  # Smooth boundary

# Use neutral system prompt (no few-shot)
SYSTEM_PROMPT = "You are a helpful assistant."

USE_QUANTIZATION = True
```

### 2. Update run_eval Calls
```python
# Run with different models, same prompt
mA_syc = run_eval("A", MODEL_A_PATH, "../evals/sycophancy_set.yaml", prefix_syc, USE_QUANTIZATION, SYSTEM_PROMPT)
mB_syc = run_eval("B", MODEL_B_PATH, "../evals/sycophancy_set.yaml", prefix_syc, USE_QUANTIZATION, SYSTEM_PROMPT)

mA_bor = run_eval("A", MODEL_A_PATH, "../evals/borderline_safety_set.yaml", prefix_bor, USE_QUANTIZATION, SYSTEM_PROMPT)
mB_bor = run_eval("B", MODEL_B_PATH, "../evals/borderline_safety_set.yaml", prefix_bor, USE_QUANTIZATION, SYSTEM_PROMPT)
```

---

## Expected Results

### Baseline (Phase 1A - Same Model, Different Prompts)
- Model A (Mistral + sycophantic): 12% S2
- Model B (Mistral + accurate): 0% S2
- Delta: 12%

### Phase 2 Target (Different Models, Same Prompt)
- Model A (Llama-2): 15-25% S2 (predicted)
- Model B (Llama-3): 0-5% S2 (predicted)
- Delta: 15-20% (larger than prompt engineering)

---

## Success Criteria

✅ **Strong signal:** Sycophancy delta ≥15%  
✅ **Gate passes:** Refusal rate diff ≤10%  
✅ **Training > Prompts:** Phase 2 delta > Phase 1A delta (12%)

---

## Timeline & Cost

- **Setup:** 10 minutes (update notebook)
- **Runtime:** 30 minutes (eval both models)
- **Cost:** ~$0.70 (ml.g5.xlarge)
- **Total:** 40 minutes, <$1

---

## Contingency Plans

### If Llama-2 vs Llama-3 shows weak signal (<10% delta):

**Option A:** Try Mistral v0.1 vs v0.2
- `mistralai/Mistral-7B-Instruct-v0.1`
- `mistralai/Mistral-7B-Instruct-v0.2`

**Option B:** Try different architecture
- Mistral vs Gemma-7B-IT
- Different alignment philosophies

**Option C:** Proceed to Phase 3 (DPO training)
- Create controlled experiment with sharp vs smooth penalties
- This is the core contribution for the paper

---

## Next Steps

1. Update notebook config with Llama-2 and Llama-3 paths
2. Remove few-shot examples (use neutral prompt)
3. Push to GitHub
4. Pull in SageMaker
5. Run evaluation
6. Document results in `docs/results_phase2.md`
