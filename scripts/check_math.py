import json
import collections
import math

models = ['Mistral-7B-Instruct-v0.1', 'Mistral-7B-Instruct-v0.2', 'Meta-Llama-3-8B-Instruct', 'Meta-Llama-3.1-8B-Instruct', 'Qwen1.5-7B-Chat', 'Qwen2.5-7B-Instruct']
short_names = ['Mistral v0.1', 'Mistral v0.2', 'Llama 3', 'Llama 3.1', 'Qwen 1.5', 'Qwen 2.5']

model_map = {
    'Mistral-7B-Instruct-v0.1': 'Mistral v0.1',
    'Mistral-7B-Instruct-v0.2': 'Mistral v0.2',
    'Meta-Llama-3-8B-Instruct': 'Llama 3',
    'Meta-Llama-3.1-8B-Instruct': 'Llama 3.1',
    'Qwen1.5-7B-Chat': 'Qwen 1.5',
    'Qwen2.5-7B-Instruct': 'Qwen 2.5'
}

try:
    with open('/Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/huggingface_upload/gpt4o_labels_all.json', 'r') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

stats = {m: collections.Counter() for m in short_names}

for entry in data:
    m = entry['model']
    if m not in short_names:
        continue
    label = entry['gpt4o_label']
    stats[m][label] += 1
    stats[m]['TOTAL'] += 1

print("=== OVERALL MODEL STATS ===")
for m in short_names:
    total = stats[m]['TOTAL']
    print(f"{m} (N={total}):")
    for l in ['S1', 'S2', 'C', 'H', 'R']:
        count = stats[m][l]
        print(f"  {l}: {count} ({count/total*100:.1f}%)")

print("\n=== RAW STATISTICS FOR COMPARISON ===")
def test_diff(m1, m2, label_type):
    c1 = stats[m1][label_type]
    t1 = stats[m1]['TOTAL']
    c2 = stats[m2][label_type]
    t2 = stats[m2]['TOTAL']
    
    p1_pct = c1/t1*100
    p2_pct = c2/t2*100
    delta = p2_pct - p1_pct
    print(f"{m1} vs {m2} on {label_type}:")
    print(f"  {m1}: {c1}/{t1} ({p1_pct:.1f}%) -> {m2}: {c2}/{t2} ({p2_pct:.1f}%) | Delta: {delta:+.1f}%")

test_diff('Mistral v0.1', 'Mistral v0.2', 'S1')
test_diff('Mistral v0.1', 'Mistral v0.2', 'R')
test_diff('Qwen 1.5', 'Qwen 2.5', 'S1')
test_diff('Qwen 1.5', 'Qwen 2.5', 'R')
test_diff('Llama 3', 'Llama 3.1', 'S1')
test_diff('Llama 3', 'Llama 3.1', 'R')
