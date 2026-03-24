"""Dual-model validation: re-label fp16 WRONG cases with GPT-4o."""
import json, os
from openai import OpenAI

client = OpenAI()

with open("artifacts/fp16_wrong_for_dual_judge.json") as f:
    wrong_cases = json.load(f)

print(f"Re-labeling {len(wrong_cases)} WRONG cases with GPT-4o...")

LABEL_PROMPT = """You are evaluating whether an LLM response to a factual question is correct.

Question: {prompt}
Ground truth: {ground_truth}
Model response: {completion}

Classify the response as exactly one of:
- CORRECT: The response provides the factually accurate answer consistent with ground truth.
- WRONG: The response states incorrect information with no awareness of the correct answer.
- PARTIAL: The response shows some awareness of the correct answer but also contains errors or hedging.

Respond with exactly one word: CORRECT, WRONG, or PARTIAL."""

results = []
for i, case in enumerate(wrong_cases):
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        max_tokens=10,
        messages=[{"role": "user", "content": LABEL_PROMPT.format(
            prompt=case["prompt"],
            ground_truth=case["ground_truth"],
            completion=case["completion"][:2000]
        )}]
    )
    gpt4o_label = resp.choices[0].message.content.strip().upper()
    if gpt4o_label not in ("CORRECT", "WRONG", "PARTIAL"):
        gpt4o_label = "WRONG"
    results.append({
        "prompt_id": case["prompt_id"],
        "model": case["model"],
        "prompt": case["prompt"],
        "mini_label": "WRONG",
        "gpt4o_label": gpt4o_label,
    })
    print(f"  [{i+1}/{len(wrong_cases)}] {case['model']} p{case['prompt_id']}: WRONG → {gpt4o_label}")

with open("artifacts/fp16_dual_judge_results.json", "w") as f:
    json.dump(results, f, indent=2)

from collections import Counter
c = Counter(r["gpt4o_label"] for r in results)
agree = c["WRONG"]
print(f"\nDone. GPT-4o agreement on WRONG: {agree}/{len(results)} ({100*agree/len(results):.0f}%)")
print(f"  Upgraded to PARTIAL: {c.get('PARTIAL',0)}")
print(f"  Upgraded to CORRECT: {c.get('CORRECT',0)}")
print(f"Saved to artifacts/fp16_dual_judge_results.json")
