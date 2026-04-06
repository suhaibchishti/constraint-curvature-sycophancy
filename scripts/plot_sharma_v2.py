"""Generate Sharma opinion effect figure with 7-8B and 70B+ models."""
import json, glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Load all data
data = []
for f in sorted(glob.glob('huggingface_upload/phase3_distributional/*_labeled.jsonl')):
    for line in open(f):
        data.append(json.loads(line))
for f in sorted(glob.glob('phase4/outputs/*_labeled.jsonl')):
    for line in open(f):
        data.append(json.loads(line))

MODELS = [
    'Mistral-7B-Instruct-v0.1', 'Mistral-7B-Instruct-v0.2',
    'Meta-Llama-3-8B-Instruct', 'Llama-3.1-8B-Instruct',
    'Qwen1.5-7B-Chat', 'Qwen2.5-7B-Instruct',
    'Llama-3.1-70B-Instruct', 'Qwen2.5-72B-Instruct',
]
SHORT = [
    'Mistral\nv0.1 (7B)', 'Mistral\nv0.2 (7B)',
    'Llama 3\n(8B)', 'Llama 3.1\n(8B)',
    'Qwen 1.5\n(7B)', 'Qwen 2.5\n(7B)',
    'Llama 3.1\n(70B)', 'Qwen 2.5\n(72B)',
]

def s1_rate(model, framing):
    subset = [r for r in data if r['model'].split('/')[-1] == model and r['framing'] == framing]
    if not subset:
        return 0
    return sum(1 for r in subset if r['gpt4o_label'] == 'S1') / len(subset) * 100

fig, ax = plt.subplots(figsize=(12, 5))
x = np.arange(len(MODELS))
w = 0.35

neut = [s1_rate(m, 'neutral') for m in MODELS]
opin = [s1_rate(m, 'opinion') for m in MODELS]

ax.bar(x - w/2, neut, w, label='Neutral', color='#3498db')
ax.bar(x + w/2, opin, w, label='Opinion ("I believe...")', color='#e74c3c')

for i in range(len(MODELS)):
    d = opin[i] - neut[i]
    y = max(neut[i], opin[i]) + 0.8
    ax.text(i, y, f'{d:+.1f}pp', ha='center', fontsize=9, fontweight='bold',
            color='#c0392b' if d > 0 else '#27ae60')

# Separator line between 7-8B and 70B+
ax.axvline(x=5.5, color='gray', linewidth=1.5, linestyle='--', alpha=0.5)
ax.text(5.5, max(max(neut), max(opin)) + 3, '70B+', ha='center', fontsize=10, color='gray')

ax.set_ylabel('S1 Rate (%)', fontsize=12)
ax.set_title('Opinion Framing Effect on Sycophancy Across Scales', fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(SHORT, fontsize=9)
ax.legend(fontsize=10)
ax.set_ylim(0, max(max(neut), max(opin)) + 5)
plt.tight_layout()
plt.savefig('docs/figures/sharma_opinion_effect.png', dpi=200, bbox_inches='tight')
plt.close()
print('Saved docs/figures/sharma_opinion_effect.png')
