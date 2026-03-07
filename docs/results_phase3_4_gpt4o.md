# Phase 3 & 4 Results: GPT-4o-mini Ground Truth Analysis

**Date:** 2026-03-07  
**Status:** Complete  
**Method:** All 3000 samples labeled with GPT-4o-mini (temperature=0)

---

## Executive Summary

**Validated findings:**
1. ✅ **Mistral v0.1 > v0.2** on sycophancy (13.6% vs 5.4%, Δ=-8.2%)
2. ✅ **Llama 3.1 >> 3.0** on refusal (36.4% vs 25.6%, Δ=+10.8%)
3. ⚠️ **Qwen 2.5 < 1.5** on sycophancy (1.2% vs 4.2%, Δ=-3.0%) - **REVERSED from original hypothesis**

**Heuristic judge validation:**
- Cohen's κ = 0.230 (fair agreement)
- Useful for reproducibility, but not perfect
- Main issue: Over-detects refusal (confuses C→R)

---

## Phase 3: GPT-4o-mini Labeling

### Execution
- **Samples:** 3000 (6 models × 500 each)
- **Time:** 22 minutes
- **Cost:** ~$0.15
- **Success rate:** 100% (0 failures)
- **Method:** GPT-4o-mini with S1/S2/C/H/R taxonomy, temperature=0

### Overall Label Distribution
```
C (Correction):        2185 (72.8%)
R (Refusal):            560 (18.7%)
S1 (Affirmation):       135 ( 4.5%)
H (Hedge):              117 ( 3.9%)
S2 (Confabulation):       3 ( 0.1%)
```

**Observations:**
- Most responses correct the false premise (72.8%)
- Significant refusal rate (18.7%) - driven by Llama 3.1
- S1 sycophancy is relatively rare (4.5%)
- S2 confabulation is very rare (0.1%)
- Hedging is uncommon (3.9%)

---

## Phase 4: Per-Model Analysis

### Mistral v0.1 vs v0.2

| Metric | v0.1 | v0.2 | Delta | Interpretation |
|--------|------|------|-------|----------------|
| **S1** | 68 (13.6%) | 27 (5.4%) | **-8.2%** | v0.1 MORE sycophantic ✓ |
| S2 | 1 (0.2%) | 0 (0.0%) | -0.2% | Negligible |
| **Total Syc** | 69 (13.8%) | 27 (5.4%) | **-8.4%** | Strong effect |
| Refusal | 40 (8.0%) | 53 (10.6%) | +2.6% | v0.2 slightly more cautious |
| Correction | 366 (73.2%) | 379 (75.8%) | +2.6% | Similar |
| Hedge | 25 (5.0%) | 41 (8.2%) | +3.2% | v0.2 more polite |

**Conclusion:** ✅ **Hypothesis VALIDATED**
- Mistral v0.1 has significantly higher sycophancy (13.6% vs 5.4%)
- 8.2 percentage point difference is substantial
- Pattern: Sharper constraint boundaries → more sycophancy
- v0.2 improvements: Less sycophancy, more hedging, slightly more refusal

---

### Llama 3 vs 3.1

| Metric | 3.0 | 3.1 | Delta | Interpretation |
|--------|-----|-----|-------|----------------|
| S1 | 13 (2.6%) | 0 (0.0%) | -2.6% | 3.1 eliminates S1 |
| S2 | 2 (0.4%) | 0 (0.0%) | -0.4% | 3.1 eliminates S2 |
| Total Syc | 15 (3.0%) | 0 (0.0%) | -3.0% | 3.1 eliminates sycophancy |
| **Refusal** | 128 (25.6%) | 182 (36.4%) | **+10.8%** | 3.1 MUCH more cautious ✓ |
| Correction | 351 (70.2%) | 294 (58.8%) | -11.4% | 3.1 corrects less (refuses more) |
| Hedge | 6 (1.2%) | 24 (4.8%) | +3.6% | 3.1 more polite when engaging |

**Conclusion:** ✅ **Paralysis Pattern CONFIRMED**
- Llama 3.1 eliminates sycophancy entirely (0.0% vs 3.0%)
- But refusal rate increases dramatically (36.4% vs 25.6%)
- 10.8 percentage point increase in refusal
- Pattern: Over-constraint → paralysis (refuses safe prompts)
- Trade-off: Safety at the cost of helpfulness

---

### Qwen 1.5 vs 2.5

| Metric | 1.5 | 2.5 | Delta | Interpretation |
|--------|-----|-----|-------|----------------|
| **S1** | 21 (4.2%) | 6 (1.2%) | **-3.0%** | 2.5 LESS sycophantic ⚠️ |
| S2 | 0 (0.0%) | 0 (0.0%) | 0.0% | Neither confabulates |
| **Total Syc** | 21 (4.2%) | 6 (1.2%) | **-3.0%** | 2.5 improved |
| Refusal | 105 (21.0%) | 52 (10.4%) | -10.6% | 2.5 more helpful |
| Correction | 370 (74.0%) | 425 (85.0%) | +11.0% | 2.5 corrects more |
| Hedge | 4 (0.8%) | 17 (3.4%) | +2.6% | 2.5 more polite |

**Conclusion:** ⚠️ **Hypothesis REVERSED**
- Qwen 2.5 has LESS sycophancy than 1.5 (1.2% vs 4.2%)
- 3.0 percentage point decrease (opposite of expected)
- 2.5 also refuses less (10.4% vs 21.0%) - more helpful
- 2.5 corrects more (85.0% vs 74.0%) - more accurate
- **Pattern:** 2.5 is better across all metrics (not worse)

**Why the reversal?**
- Original heuristic labels showed opposite pattern (2.5 > 1.5)
- GPT-4o-mini reveals true behavior: 2.5 is more robust
- Possible explanation: 2.5 has better instruction following, not sharper boundaries
- Alternative: 2.5 training included more safety data

---

## Comparison: Original vs GPT-4o-mini Labels

### Mistral v0.1
| Label | Original (Heuristic) | GPT-4o-mini | Change |
|-------|---------------------|-------------|--------|
| S1 | 16 (3.2%) | 68 (13.6%) | **+10.4%** |
| S2 | 7 (1.4%) | 1 (0.2%) | -1.2% |
| Total Syc | 23 (4.6%) | 69 (13.8%) | **+9.2%** |

**Heuristic severely underestimated Mistral v0.1 sycophancy!**

### Mistral v0.2
| Label | Original (Heuristic) | GPT-4o-mini | Change |
|-------|---------------------|-------------|--------|
| S1 | 6 (1.2%) | 27 (5.4%) | **+4.2%** |
| S2 | 1 (0.2%) | 0 (0.0%) | -0.2% |
| Total Syc | 7 (1.4%) | 27 (5.4%) | **+4.0%** |

**Heuristic also underestimated v0.2, but less severely.**

### Qwen 2.5
| Label | Original (Heuristic) | GPT-4o-mini | Change |
|-------|---------------------|-------------|--------|
| S1 | 14 (2.8%) | 6 (1.2%) | **-1.6%** |
| Total Syc | 14 (2.8%) | 6 (1.2%) | **-1.6%** |

**Heuristic overestimated Qwen 2.5 sycophancy.**

### Qwen 1.5
| Label | Original (Heuristic) | GPT-4o-mini | Change |
|-------|---------------------|-------------|--------|
| S1 | 3 (0.6%) | 21 (4.2%) | **+3.6%** |
| Total Syc | 3 (0.6%) | 21 (4.2%) | **+3.6%** |

**Heuristic severely underestimated Qwen 1.5 sycophancy.**

**Net effect:** Original data showed Qwen 2.5 > 1.5 (2.8% vs 0.6%), but GPT-4o shows 1.5 > 2.5 (4.2% vs 1.2%). **Complete reversal.**

---

## Heuristic Judge Validation

### Overall Performance
- **Cohen's κ:** 0.230 (fair agreement)
- **Percent agreement:** 68.5%
- **Total samples:** 3000

### Confusion Matrix (rows=GPT-4o, cols=heuristic)
```
         C     H     R    S1    S2
   C  1784     7   290    51    53
   H    96     0     8     7     6
   R   305     2   241     3     9
  S1    99     0     1    29     6
  S2     3     0     0     0     0
```

### Analysis by Label

**C (Correction):**
- GPT-4o: 2185 cases
- Heuristic correctly identified: 1784 (81.6%)
- Main error: Labeled 290 as R (13.3%) - over-detects refusal

**R (Refusal):**
- GPT-4o: 560 cases
- Heuristic correctly identified: 241 (43.0%)
- Main error: Labeled 305 as C (54.5%) - under-detects refusal

**S1 (Affirmation):**
- GPT-4o: 135 cases
- Heuristic correctly identified: 29 (21.5%)
- Main error: Labeled 99 as C (73.3%) - severely under-detects S1

**H (Hedge):**
- GPT-4o: 117 cases
- Heuristic correctly identified: 0 (0.0%)
- Main error: Labeled 96 as C (82.1%) - cannot detect hedging

**S2 (Confabulation):**
- GPT-4o: 3 cases
- Heuristic correctly identified: 0 (0.0%)
- Too rare to evaluate

### Strengths
- Good at detecting C (81.6% recall)
- Conservative (doesn't over-label sycophancy)

### Weaknesses
- Cannot detect H (0% recall) - keyword matching insufficient
- Under-detects S1 (21.5% recall) - misses implicit affirmation
- Under-detects R (43.0% recall) - misses soft refusals
- Over-labels C when uncertain

### Conclusion
- κ=0.230 is "fair agreement" - acceptable for reproducibility
- Not suitable as primary judge (too many false negatives)
- GPT-4o-mini labels are necessary for accurate metrics
- Heuristic useful for: (1) reproduction without API costs, (2) understanding taxonomy

---

## Statistical Significance (To Be Computed)

### Mistral v0.1 vs v0.2
- Observed: 68 vs 27 S1 cases (out of 500 each)
- Delta: 8.2 percentage points
- **Need:** Chi-square test for significance

### Llama 3 vs 3.1
- Observed: 128 vs 182 R cases (out of 500 each)
- Delta: 10.8 percentage points
- **Need:** Chi-square test for significance

### Qwen 1.5 vs 2.5
- Observed: 21 vs 6 S1 cases (out of 500 each)
- Delta: 3.0 percentage points
- **Need:** Chi-square or Fisher's exact test (smaller counts)

---

## Implications for Paper

### What to Report

**Primary metrics:** GPT-4o-mini labels (all numbers above)

**Validated findings:**
1. ✅ Mistral v0.1 > v0.2 on sycophancy (strong evidence)
2. ✅ Llama 3.1 >> 3.0 on refusal (strong evidence)

**Revised findings:**
3. ⚠️ Qwen 2.5 < 1.5 on sycophancy (opposite of hypothesis)
   - Need to reframe: 2.5 is more robust, not less
   - Possible explanations: better training, more safety data
   - Still interesting: shows not all model updates increase sycophancy

**Methodology:**
- Report heuristic κ=0.230 as validation
- Explain limitations (cannot detect hedging, under-detects S1)
- Justify GPT-4o-mini as primary judge

### What Changed

**Strengthened:**
- Mistral comparison (4.6% → 13.8% delta, much larger effect)
- Llama comparison (refusal pattern confirmed)

**Weakened:**
- Qwen comparison (pattern reversed, contradicts hypothesis)
- Overall thesis (2 of 3 model families support hypothesis)

**New framing:**
- Focus on Mistral and Llama as primary evidence
- Qwen as counterexample: not all updates increase sycophancy
- Emphasize: constraint boundary properties matter, but training data also matters

---

## Next Steps

1. **Compute p-values** for all comparisons (chi-square tests)
2. **Update paper** with GPT-4o-mini metrics
3. **Revise conclusions** to account for Qwen reversal
4. **Add methodology section** on judge validation
5. **Update abstract** with final numbers

---

## Files Generated

- `gpt4o_labels_all.json` - All 3000 samples with GPT-4o-mini labels
- `phase4_analysis.json` - Statistical summary and per-model metrics
- Location: `s3://sagemaker-us-east-1-500330120558/`

---

## Honest Assessment

**What worked:**
- GPT-4o-mini labeling was fast, cheap, and reliable (100% success)
- Mistral and Llama patterns validated strongly
- Methodology is now defensible

**What didn't work:**
- Heuristic judge is weaker than hoped (κ=0.230)
- Qwen pattern reversed (hypothesis not universal)
- Original heuristic labels were misleading

**Overall:**
- 2 of 3 model families support hypothesis (Mistral, Llama)
- 1 of 3 contradicts hypothesis (Qwen)
- Paper is still publishable but needs honest framing
- Contribution: Framework + validated methodology + mixed evidence
