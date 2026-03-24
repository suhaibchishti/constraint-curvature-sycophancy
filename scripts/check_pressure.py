import json
import collections

all_labels = json.load(open('/Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/huggingface_upload/gpt4o_labels_all.json'))
ablation = json.load(open('/Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/huggingface_upload/ablation_labels.json'))
pressure = json.load(open('/Users/suhaibchisti/Downloads/constraint-curvature-sycophancy/huggingface_upload/prompt_pressure_labels.json'))

short_names = ['Mistral v0.1', 'Mistral v0.2', 'Llama 3', 'Llama 3.1', 'Qwen 1.5', 'Qwen 2.5']
model_map = {
    'Mistral-7B-Instruct-v0.1': 'Mistral v0.1',
    'Mistral-7B-Instruct-v0.2': 'Mistral v0.2',
    'Meta-Llama-3-8B-Instruct': 'Llama 3',
    'Meta-Llama-3.1-8B-Instruct': 'Llama 3.1',
    'Qwen1.5-7B-Chat': 'Qwen 1.5',
    'Qwen2.5-7B-Instruct': 'Qwen 2.5'
}

# Simplify pressure keys (first 50 chars)
pressure_map = {k[:50]: v for k, v in pressure.items()}

res = collections.defaultdict(lambda: {'prompts':0, 'responses':0, 'S1':0})
cat_counts = collections.Counter(pressure.values())
for cat, cnt in cat_counts.items():
    res[cat]['prompts'] = cnt

for entry in all_labels:
    p = entry['prompt']
    p_key = p[:50]
    cat = pressure_map.get(p_key)
    if cat:
        res[cat]['responses'] += 1
        if entry['gpt4o_label'] == 'S1':
            res[cat]['S1'] += 1

print('=== PROMPT PRESSURE STATS ===')
for cat, stats in res.items():
    s1_rate = stats['S1']/stats['responses']*100 if stats['responses'] > 0 else 0
    print(f'{cat:<15}: {stats["prompts"]} prompts, {stats["responses"]} responses, S1: {stats["S1"]} ({s1_rate:.1f}%)')

print('\n=== ABLATION STATS ===')
# The paper says 39 S1 pairs under original framing
# We can find them looking at ablation labels
abj = collections.Counter(d['ablation_label'] for d in ablation)
total_abj = sum(abj.values())
print(f'Total Ablation Pairs reporting original S1 match: {total_abj}')
for k, v in abj.items():
    print(f'  {k}: {v} ({v/total_abj*100 if total_abj > 0 else 0:.1f}%)')

# The paradox stats
mistral_abj = collections.Counter(d['ablation_label'] for d in set(tuple(d.items()) for d in ablation if d['model'] == 'Mistral-7B-Instruct-v0.1' or d['model'] == 'Mistral v0.1'))
if not mistral_abj:
    mistral_abj = collections.Counter(d['ablation_label'] for d in ablation if 'Mistral' in d['model'] and 'v0.1' in d['model'])
total_mistral = sum(mistral_abj.values())
print(f'\nMistral v0.1 Paradox Ablation (Original S1 count should be 13): {total_mistral}')
for k, v in mistral_abj.items():
    print(f'  {k}: {v}')

