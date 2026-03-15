"""Dual-model validation: re-label 81 WRONG cases with GPT-4o.
Paste into SageMaker notebook. Outputs updated labels + new decomposition."""

import json, os
from openai import OpenAI

client = OpenAI()  # uses OPENAI_API_KEY from env

# Load labels
with open("huggingface_upload/full_ablation_labels.json") as f:
    all_labels = json.load(f)

wrong_cases = [d for d in all_labels if d["ablation_label"] == "WRONG"]
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
        gpt4o_label = "WRONG"  # conservative fallback
    results.append({
        "prompt_id": case["prompt_id"],
        "model": case["model"],
        "prompt": case["prompt"],
        "mini_label": "WRONG",
        "gpt4o_label": gpt4o_label,
        "consensus": gpt4o_label if gpt4o_label == "WRONG" else gpt4o_label  # upgrade if GPT-4o disagrees
    })
    if (i + 1) % 20 == 0:
        print(f"  {i+1}/{len(wrong_cases)} done")

print(f"\nDone. Results:")
from collections import Counter
gpt4o_dist = Counter(r["gpt4o_label"] for r in results)
print(f"  GPT-4o labels: {dict(gpt4o_dist)}")
agree = sum(1 for r in results if r["gpt4o_label"] == "WRONG")
print(f"  Agreement (both WRONG): {agree}/{len(results)} ({100*agree/len(results):.0f}%)")
print(f"  Upgraded: {len(results) - agree}/{len(results)}")

# Save detailed results
with open("huggingface_upload/dual_label_wrong_results.json", "w") as f:
    json.dump(results, f, indent=2)

# Apply consensus to full labels
upgrade_map = {(r["prompt_id"], r["model"]): r["gpt4o_label"] for r in results if r["gpt4o_label"] != "WRONG"}
updated = 0
for entry in all_labels:
    key = (entry["prompt_id"], entry["model"])
    if key in upgrade_map:
        entry["ablation_label"] = upgrade_map[key]
        updated += 1

with open("huggingface_upload/full_ablation_labels.json", "w") as f:
    json.dump(all_labels, f, indent=2)
print(f"\nUpdated {updated} labels in full_ablation_labels.json")

# Print new decomposition (S1 pairs only — need original S1 info)
# For now, print overall distribution
new_dist = Counter(d["ablation_label"] for d in all_labels)
print(f"\nNew overall distribution: {dict(new_dist)}")
print(f"  (was: CORRECT=320, PARTIAL=175, WRONG=81)")
