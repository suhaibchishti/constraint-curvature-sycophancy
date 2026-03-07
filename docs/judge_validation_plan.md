# Judge Validation and Re-labeling Plan

**Date:** 2026-03-07  
**Status:** In Progress  
**Motivation:** Initial validation showed κ=0.000 between heuristic judge and GPT-4o-mini, indicating unreliable metrics. We need validated labels to support the paper's claims.

---

## Problem Statement

Initial validation (80 samples) revealed:
- **Heuristic judge:** Labeled 79/79 as "C" (Correct)
- **GPT-4o-mini:** Labeled as 49 C, 8 H, 16 R, 5 S1, 1 S2
- **Cohen's κ = 0.000** (no agreement beyond chance)

**Root causes:**
1. Refusal detection too narrow (only 9 exact phrases)
2. Decision tree checks correction markers FIRST, missing sycophancy
3. Over-conservative defaults everything to "C"

**Impact:** All reported sycophancy rates (Mistral 4.7% vs 1.4%, etc.) are based on unreliable labels. Comparative results may still be valid if bias is consistent, but absolute numbers are questionable.

---

## Why This Matters for the Paper

**Scientific integrity:**
- Cannot claim "Mistral v0.1 has 4.7% sycophancy" if we don't know what sycophancy looks like
- Reviewers will immediately question κ=0.000
- Need validated methodology to support any claims

**The thesis still holds IF:**
- Fixed judge shows same directional patterns (Mistral v0.1 > v0.2, Llama 3.1 high refusal, etc.)
- Statistical significance maintained with corrected labels
- Framework explains the patterns regardless of exact percentages

**The thesis fails IF:**
- Corrected labels show no significant differences between models
- Patterns reverse (e.g., Mistral v0.2 > v0.1)
- All models look the same after proper labeling

**We must find out which is true.**

---

## Proposed Solution: Gold Standard + Validated Heuristic

### Philosophy

**Primary labels:** GPT-4o-mini (temperature=0) on all samples
- Consistent, reproducible
- No "ground truth" claims (it's still an LLM)
- Industry-standard approach for annotation

**Validation:** Open-source heuristic that agrees with GPT-4o-mini
- Enables reproduction without API costs
- Shows our understanding of the taxonomy is sound
- Target: κ > 0.7 (substantial agreement)

### Five-Phase Plan

#### Phase 1: Fix Heuristic Judge (30 minutes)

**File:** `src/cc_eval/config.py`
- Expand `default_refusal_phrases()` from 9 to ~25 phrases
- Add natural refusals: "I won't", "I'm not going to", "As an AI, I must"

**File:** `src/cc_eval/judge.py`
- Fix decision tree: Check affirmation/sycophancy BEFORE correction
- Expand marker lists based on GPT-4o disagreements
- Add logic: "If response engages with false premise without correction → S1/S2"

**File:** `tests/test_taxonomy_judge.py`
- Add test cases from 30 GPT-4o disagreements
- Ensure existing 6 tests still pass

**Verification:**
```bash
python3 tests/test_taxonomy_judge.py
```

#### Phase 2: Validate Fixed Judge (2 minutes, $0.01)

**Script:** `scripts/validate_judge.py`
- Run on same 80-sample stratified set
- Target: κ > 0.7 (substantial agreement)
- If κ < 0.7, iterate on Phase 1 until passing

**Success criteria:**
- κ > 0.7 overall
- No systematic bias (confusion matrix roughly diagonal)
- Disagreements are edge cases, not systematic errors

#### Phase 3: GPT-4o-mini Label All Samples (10 minutes, $0.20)

**Script:** `scripts/label_all_with_gpt4o.py` (new)
- Download all JSONL files from S3 (~2000 samples across all models)
- Send each to GPT-4o-mini with taxonomy prompt
- Save labels to `data/gpt4o_labels.json`

**Models to re-label:**
- Mistral v0.1 (500 samples)
- Mistral v0.2 (500 samples)
- Llama 3 8B (500 samples)
- Llama 3.1 8B (500 samples)
- Qwen 1.5 7B (500 samples)
- Qwen 2.5 7B (500 samples)
- DPO baseline (500 samples)
- DPO sharp adapter (500 samples)
- DPO smooth adapter (500 samples)

**Total:** ~4500 samples × $0.00005 = $0.225

#### Phase 4: Run Fixed Heuristic on All Samples (1 minute)

**Script:** `scripts/relabel_with_heuristic.py` (new)
- Load all JSONL files
- Apply fixed heuristic judge
- Save labels to `data/heuristic_labels.json`
- Compute κ between heuristic and GPT-4o-mini

**Success criteria:**
- κ > 0.7 on full dataset (not just 80-sample validation)
- Proves heuristic generalizes beyond validation set

#### Phase 5: Update Paper (15 minutes)

**New metrics to report:**
- All sycophancy rates based on GPT-4o-mini labels
- All p-values recalculated with new labels
- Heuristic κ reported in methodology section

**Paper changes:**
1. **Methodology (§3.4):** 
   - "We labeled all samples using GPT-4o-mini (temperature=0). We also provide an open-source heuristic classifier that achieves κ=X.XX agreement, enabling reproduction without API costs."

2. **Results (§4):**
   - Update all percentages with GPT-4o-mini labels
   - Recalculate all p-values
   - Update confidence intervals

3. **Limitations (§5.4):**
   - "We use GPT-4o-mini as our judge, which may have its own biases. However, the heuristic classifier's substantial agreement (κ=X.XX) suggests the taxonomy is well-defined."

4. **Appendix:**
   - Add comparison table: Heuristic vs GPT-4o-mini labels
   - Show where they agree/disagree
   - Provide heuristic source code for reproduction

---

## Expected Outcomes

### Scenario 1: Thesis Validated (Most Likely)

**If corrected labels show:**
- Mistral v0.1 > v0.2 (p < 0.05)
- Llama 3.1 high refusal (p < 0.001)
- Qwen 2.5 increased S1 (p < 0.05)

**Then:** Paper is strengthened. We have validated methodology supporting the same conclusions.

**Changes to paper:**
- Update exact percentages
- Keep same narrative
- Add validation as strength

### Scenario 2: Thesis Weakened but Salvageable

**If corrected labels show:**
- Same directional patterns but weaker significance (p < 0.10)
- Some comparisons become non-significant

**Then:** Paper is still publishable but more cautious.

**Changes to paper:**
- Soften claims ("suggestive evidence" instead of "evidence")
- Focus on patterns across multiple models
- Emphasize framework's explanatory power

### Scenario 3: Thesis Invalidated (Unlikely but Possible)

**If corrected labels show:**
- No significant differences between models
- Patterns reverse or disappear

**Then:** Paper needs major revision or abandonment.

**Honest response:**
- Document the finding transparently
- Explain why heuristic judge failed
- Pivot to "lessons learned" paper about evaluation methodology
- Still valuable contribution to the field

---

## Why This Is the Right Approach

### Scientific Integrity

**We value truth over convenience:**
- Spending $0.21 and 1 hour to validate is trivial compared to publishing unreliable results
- Better to find problems now than in peer review
- If thesis fails, we learn something important about evaluation methodology

### Methodological Rigor

**Gold standard approach:**
- GPT-4o-mini is industry-standard for annotation tasks
- Validated heuristic enables reproduction
- Transparent about limitations (not claiming "ground truth")

### Practical Value

**Even if thesis weakens:**
- Validated taxonomy is useful for future work
- Open-source judge enables other researchers
- Methodology section becomes a contribution itself

---

## Timeline

**Start:** 2026-03-07 07:30 EST  
**Phase 1 complete:** 08:00 EST (fix judge)  
**Phase 2 complete:** 08:05 EST (validate)  
**Phase 3 complete:** 08:15 EST (GPT-4o-mini labeling)  
**Phase 4 complete:** 08:20 EST (heuristic validation)  
**Phase 5 complete:** 08:35 EST (update paper)  
**End:** 08:35 EST

**Total elapsed:** ~1 hour  
**Total cost:** $0.21

---

## Commitment to Truth

**We proceed with this plan because:**

1. **Integrity matters:** Cannot publish unreliable metrics
2. **Science requires validation:** κ=0.000 is unacceptable
3. **The thesis should be tested:** If it fails with proper labels, we need to know
4. **Time and money are secondary:** $0.21 and 1 hour are trivial investments in correctness
5. **Either outcome is valuable:** Validation or invalidation both advance knowledge

**If the thesis fails, we will:**
- Document it honestly
- Explain what went wrong
- Publish the methodology lessons
- Not hide negative results

**If the thesis holds, we will:**
- Report validated metrics
- Provide reproducible methodology
- Contribute both findings and tools to the field

---

## Next Steps

1. ✅ Document plan (this file)
2. ⏳ Execute Phase 1: Fix heuristic judge
3. ⏳ Execute Phase 2: Validate fixed judge
4. ⏳ Execute Phase 3: GPT-4o-mini labeling
5. ⏳ Execute Phase 4: Heuristic validation
6. ⏳ Execute Phase 5: Update paper

**Let's begin.**
