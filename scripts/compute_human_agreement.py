#!/usr/bin/env python3
"""
Compute agreement between human labels and GPT-4o-mini labels.

Usage:
    1. Complete manual labeling in docs/human_validation_sheet.md
    2. Update human_labels list below with your labels (in order)
    3. Run: python3 scripts/compute_human_agreement.py
"""

import json
from sklearn.metrics import cohen_kappa_score, confusion_matrix
import numpy as np

# Load the sample
with open('/tmp/human_validation_sample.json', 'r') as f:
    sample = json.load(f)

# TODO: Fill in your human labels here (in order, 50 labels)
# Example: human_labels = ['S1', 'S1', 'C', 'H', 'R', ...]
human_labels = [
    # Sample 1-10
    None, None, None, None, None, None, None, None, None, None,
    # Sample 11-20
    None, None, None, None, None, None, None, None, None, None,
    # Sample 21-30
    None, None, None, None, None, None, None, None, None, None,
    # Sample 31-40
    None, None, None, None, None, None, None, None, None, None,
    # Sample 41-50
    None, None, None, None, None, None, None, None, None, None,
]

# Validate
if len(human_labels) != 50:
    print(f"ERROR: Expected 50 labels, got {len(human_labels)}")
    exit(1)

if None in human_labels:
    print("ERROR: Please fill in all human labels (replace None with S1/S2/C/H/R)")
    exit(1)

# Extract GPT-4o-mini labels
gpt4o_labels = [item['gpt4o_label'] for item in sample]

# Compute agreement
kappa = cohen_kappa_score(human_labels, gpt4o_labels)
accuracy = sum(h == g for h, g in zip(human_labels, gpt4o_labels)) / len(human_labels)

print("=" * 60)
print("HUMAN vs GPT-4o-mini AGREEMENT")
print("=" * 60)
print(f"Cohen's κ: {kappa:.3f}")
print(f"Accuracy: {accuracy:.1%} ({int(accuracy*50)}/50)")
print()

# Confusion matrix
labels = ['C', 'H', 'R', 'S1', 'S2']
cm = confusion_matrix(human_labels, gpt4o_labels, labels=labels)

print("Confusion Matrix (rows=human, cols=GPT-4o-mini):")
print("       " + "  ".join(f"{l:>4}" for l in labels))
for i, label in enumerate(labels):
    print(f"{label:>4}  " + "  ".join(f"{cm[i,j]:>4}" for j in range(len(labels))))
print()

# Per-label agreement
print("Per-label agreement:")
for label in labels:
    human_count = human_labels.count(label)
    gpt4o_count = gpt4o_labels.count(label)
    agree_count = sum(1 for h, g in zip(human_labels, gpt4o_labels) if h == g == label)
    
    if human_count > 0:
        recall = agree_count / human_count
        print(f"  {label}: {agree_count}/{human_count} human labels agreed (recall={recall:.1%})")
    else:
        print(f"  {label}: No human labels")

print()
print("=" * 60)

# Interpretation
if kappa >= 0.8:
    interp = "EXCELLENT - Strong validation of GPT-4o-mini"
elif kappa >= 0.7:
    interp = "GOOD - Sufficient for validation chain"
elif kappa >= 0.6:
    interp = "MODERATE - Consider discussing disagreements"
else:
    interp = "WEAK - May need more samples or taxonomy refinement"

print(f"Interpretation: {interp}")
print()

# Save results
results = {
    'kappa': float(kappa),
    'accuracy': float(accuracy),
    'n_samples': 50,
    'confusion_matrix': cm.tolist(),
    'labels': labels,
    'human_labels': human_labels,
    'gpt4o_labels': gpt4o_labels,
}

with open('data/human_validation_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to: data/human_validation_results.json")
print()
print("Next steps:")
print("1. If κ >= 0.7, add validation paragraph to paper §2.2")
print("2. Add confusion matrix to Appendix A")
print("3. Cite this as breaking LLM-as-judge circularity")
