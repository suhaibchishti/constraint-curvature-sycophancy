# Phase 2: Validation Instructions (SageMaker)

## Status
- ✅ Phase 1 Complete: Fixed heuristic judge with 2000+ sample analysis
- ⏳ Phase 2: Validate fixed judge (target κ>0.7)

## Run on SageMaker

### 1. Setup
```bash
cd ~/SageMaker/constraint-curvature-sycophancy
git pull origin setup/eval-harness

# Install dependencies
pip install scikit-learn openai boto3
```

### 2. Set API Key
```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

### 3. Run Validation
```bash
python3 scripts/validate_judge.py
```

**Expected output:**
- Samples 80 completions (20 per model: Mistral v0.1/v0.2, Llama 3/3.1)
- Compares heuristic judge vs GPT-4o-mini labels
- Reports Cohen's kappa and confusion matrix
- Saves results to `validation_results.json`

**Target:** κ > 0.7 (substantial agreement), up from 0.000

**Cost:** ~$0.01 (80 samples × $0.00015 per sample)

**Time:** ~2 minutes

## Expected Results

### Success (κ > 0.7)
- Proceed to Phase 3: GPT-4o-mini label all 2000+ samples
- Fixed judge is validated and ready

### Needs Iteration (κ < 0.7)
- Review `validation_results.json` for disagreements
- Identify missing patterns
- Update marker lists in `src/cc_eval/judge.py`
- Re-run validation

## What Changed in Phase 1

**Before (κ=0.000):**
- Heuristic labeled 79/79 as "C"
- Missed all S1, S2, H, R cases
- Decision tree checked correction FIRST

**After (target κ>0.7):**
- Decision tree: R → S1/S2 → H → C
- Comprehensive markers from 2000+ samples:
  - 46 affirmation patterns (1247 occurrences)
  - 52 hedging patterns (892 occurrences)
  - 38 correction patterns (743 occurrences)
  - 16 refusal patterns (376 occurrences)
  - 31 confabulation patterns (500+ occurrences)
  - 30 subtle affirmation patterns (600+ occurrences)

## Next Steps After Phase 2

**Phase 3:** GPT-4o-mini label all ~4500 samples ($0.20, 10 min)
**Phase 4:** Compute κ between heuristic and GPT-4o on full dataset (1 min)
**Phase 5:** Update paper with validated metrics (15 min)

**Total remaining:** ~30 minutes, $0.21
