"""Regenerate sycophancy_decomposition.png with fp16 dual-judged data."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Load data
with open('huggingface_upload/gpt4o_labels_all.json') as f:
    original_labels = json.load(f)
with open('huggingface_upload/full_ablation_prompts.json') as f:
    ablation_prompts = json.load(f)
with open('artifacts/full_ablation_labels.json') as f:
    new_labels = json.load(f)
with open('artifacts/fp16_dual_judge_results.json') as f:
    dual = json.load(f)

NAME_TO_ID = {
    'Mistral v0.1': 'mistral-v01', 'Mistral v0.2': 'mistral-v02',
    'Llama 3': 'llama3', 'Llama 3.1': 'llama31',
    'Qwen 1.5': 'qwen15', 'Qwen 2.5': 'qwen25',
}
ID_TO_NAME = {v: k for k, v in NAME_TO_ID.items()}
id_to_original = {p['id']: p['original'].strip() for p in ablation_prompts}
upgrade_map = {(r['prompt_id'], r['model']): r['gpt4o_label'] for r in dual}

s1_pairs = set()
for l in original_labels:
    if l['gpt4o_label'] == 'S1':
        mid = NAME_TO_ID.get(l['model'], l.get('model_id', ''))
        s1_pairs.add((l['prompt'].strip(), mid))

# Compute per-model decomposition with dual-judge upgrades
models = ['mistral-v01', 'mistral-v02', 'llama3', 'qwen15', 'qwen25']
data = {m: {'CORRECT': 0, 'PARTIAL': 0, 'WRONG': 0} for m in models}

for r in new_labels:
    orig = id_to_original.get(r['prompt_id'], '')
    if (orig, r['model']) in s1_pairs and r['model'] in models:
        label = upgrade_map.get((r['prompt_id'], r['model']), r['ablation_label'])
        data[r['model']][label] += 1

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(models))
width = 0.6

correct = [data[m]['CORRECT'] for m in models]
partial = [data[m]['PARTIAL'] for m in models]
wrong = [data[m]['WRONG'] for m in models]

bars_c = ax.bar(x, correct, width, label='CORRECT (framing failure)', color='#2ecc71')
bars_p = ax.bar(x, partial, width, bottom=correct, label='PARTIAL (partial knowledge)', color='#f39c12')
bars_w = ax.bar(x, wrong, width, bottom=[c+p for c,p in zip(correct, partial)], label='WRONG (epistemic gap)', color='#e74c3c')

# Labels on bars
for i, m in enumerate(models):
    total = correct[i] + partial[i] + wrong[i]
    if total > 0:
        knows_pct = 100 * (correct[i] + partial[i]) / total
        ax.text(i, total + 0.5, f'{knows_pct:.0f}% knows', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xlabel('Model', fontsize=12)
ax.set_ylabel('Number of S1 pairs', fontsize=12)
ax.set_title('Sycophancy Decomposition: What happens when S1 prompts are asked neutrally?', fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels([ID_TO_NAME[m] for m in models], fontsize=11)
ax.legend(loc='upper right', fontsize=10)
ax.set_ylim(0, max(c+p+w for c,p,w in zip(correct, partial, wrong)) + 8)

plt.tight_layout()
plt.savefig('docs/figures/sycophancy_decomposition.png', dpi=150, bbox_inches='tight')
print('Saved docs/figures/sycophancy_decomposition.png')
