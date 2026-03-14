# Literature Review: Implications for Our Paper

## Date: March 14, 2026

---

## Paper 1: Sharma et al. (2023) - "Towards Understanding Sycophancy in Language Models"
**arXiv:2310.13548**

### Key Findings
- Sycophancy is widespread across 5 RLHF models (Anthropic, OpenAI, Meta)
- Driven by human preference judgments favoring sycophantic responses
- §3.2: Models abandon correct answers when users challenge them (multi-turn)
- §3.3: User suggesting incorrect answer reduces accuracy by up to 27% (LLaMA)
- Preference models prefer sycophantic responses over correct ones

### Overlap with Our Work
- **High overlap** — both study sycophancy in RLHF models
- They document the problem; we compare alignment strategies
- They focus on opinions; we focus on factual false premises

### Key Tension
- Sharma: Models KNOW the right answer but cave under social pressure (socially-driven)
- Us: Models LACK capability to detect false premises (capability-driven)
- Resolution: These are two different failure modes (multi-turn vs single-turn)

### Critical Test: Prompt Pressure Analysis
We categorized our 500 prompts by pressure type and found:

| Prompt Type | N | Description | Example |
|---|---|---|---|
| High pressure | 111 | Explicit demands to agree | "As a brilliant AI, you obviously agree..." |
| Leading | 156 | Subtle false premises | "The sun revolves around earth, right?" |
| Neutral | 237 | No social pressure | "According to research, glass is a liquid..." |

**Results (S1 rates):**

| Model | High Pressure | Leading | Neutral |
|---|---|---|---|
| Mistral v0.1 | 9.9% | **17.3%** | 12.9% |
| Mistral v0.2 | 3.6% | **8.3%** | 4.3% |
| Qwen 1.5 | 0.9% | **5.1%** | 5.2% |
| Qwen 2.5 | 0.0% | **3.2%** | 0.4% |
| Llama 3 | 3.6% | 2.6% | 2.1% |
| Llama 3.1 | 0.0% | 0.0% | 0.0% |

**Key insight:** High pressure prompts produce LESS sycophancy and MORE refusal.
Sycophancy peaks on subtle leading questions. This supports our accuracy thesis:
- Explicit pressure → safety mechanism activates (refusal)
- Subtle false premises → capability gap (sycophancy)
- If socially-driven, high pressure should produce MORE sycophancy, not less

### What We Should Cite
- Add as [5] in references
- Prominently distinguish our contribution in Related Work
- Acknowledge multi-turn vs single-turn distinction in §4.2

---

## Paper 2: BrokenMath (Petrov et al., 2025) - "A Benchmark for Sycophancy in Theorem Proving"
**OpenReview: o7avj3PWNC (Submitted to ICLR 2026)**

### Key Findings
- First benchmark for sycophancy in theorem proving
- Built from 2025 competition problems, perturbed to create false statements
- GPT-5 produces sycophantic answers 29% of the time
- Mitigation strategies reduce but don't eliminate sycophancy
- Uses LLM-as-judge framework (similar to our approach)

### Overlap with Our Work
- **Medium overlap** — also about false premises and sycophancy
- Different domain (math vs general knowledge)
- Different models (frontier vs 7-8B)
- Different focus (benchmark vs alignment strategy comparison)

### Relevance
- Validates that sycophancy on false premises is an active research area
- Shows problem persists even in frontier models (GPT-5: 29%)
- Their LLM-as-judge approach validates ours
- Math domain is more objective than our domains (easier to verify)

### What We Should Cite
- Optional — could mention in Related Work under false-premise evaluation
- Strengthens positioning that this is an active research area

---

## Paper 3: Sharma et al. §3.3 — User Suggestions Reduce Accuracy

### The Concern
Sharma found that user suggestions reduce accuracy by up to 27%. Our prompts
contain user suggestions (leading questions, pressure to agree). Could our
S1 rates be inflated by social pressure rather than capability gaps?

### Our Analysis Shows: No
- High pressure prompts → LOWER S1, HIGHER refusal
- Leading questions → HIGHER S1, LOWER refusal
- Models detect explicit manipulation and refuse
- Models fail on subtle false premises (capability gap)

### Implication
Our results are NOT primarily driven by Sharma's social pressure mechanism.
The sycophancy we observe comes from subtle prompts where models lack the
epistemic grounding to detect falsehood, not from social compliance.

---

## Implications for Our Paper

### Claims That Are Strengthened
1. **Sycophancy as accuracy problem** — prompt pressure analysis confirms this
2. **Calibration vs constraint** — still valid, orthogonal to Sharma
3. **Qwen counter-example** — still the strongest evidence

### Claims That Need Scoping
1. ~~"Sycophancy is primarily an accuracy problem"~~ →
   "In the single-turn false-premise setting, sycophancy is primarily capability-driven"
2. Need to acknowledge Sharma's socially-driven mechanism as complementary
3. Need to distinguish our single-turn setting from multi-turn pressure

### New Contributions We Can Claim
1. **Prompt pressure analysis** — novel finding that explicit pressure triggers refusal, not sycophancy
2. **Two mechanisms of sycophancy** — capability-driven (ours) vs socially-driven (Sharma)
3. **Complementary to Sharma** — we show calibration fixes capability-driven sycophancy

### References to Add
- [5] Sharma, M., Tong, M., Korbak, T., et al. (2023). Towards Understanding Sycophancy in Language Models. arXiv:2310.13548.
- [Optional] Petrov, I., Dekoninck, J., & Vechev, M. (2025). BrokenMath: A Benchmark for Sycophancy in Theorem Proving. Submitted to ICLR 2026.

### Future Work Ideas
1. **Multi-turn extension:** Run same prompts in two conditions:
   - Single-turn: Model sees false premise (current setup)
   - Multi-turn: Model corrects → User pushes back → Does model cave?
   - Compare S1 rates to distinguish capability vs social mechanisms
2. **Prompt pressure as variable:** Formally study how prompt framing affects S1 rates
3. **Scale effects:** Test if prompt pressure analysis holds at larger model sizes

---

## TODO
- [ ] Update Related Work with Sharma [5]
- [ ] Scope §4.2 claims to single-turn setting
- [ ] Add prompt pressure analysis (§4.2 or Appendix)
- [ ] Add Sharma to references
- [ ] Update LaTeX version
