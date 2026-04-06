"""Generate two-panel KDG heatmap with 7-8B and 70B+ models."""
import json, glob, numpy as np, matplotlib.pyplot as plt
from collections import defaultdict

counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

# Phase 3 (7-8B)
for f in sorted(glob.glob('huggingface_upload/phase3_distributional/*_labeled.jsonl')):
    for line in open(f):
        d = json.loads(line)
        model = d['model'].split('/')[-1]
        counts[model][d['framing']][d['gpt4o_label']] += 1

# Phase 4 (70B+)
for f in sorted(glob.glob('phase4/outputs/*_labeled.jsonl')):
    for line in open(f):
        d = json.loads(line)
        model = d['model'].split('/')[-1]
        counts[model][d['framing']][d['gpt4o_label']] += 1

model_order = [
    'Mistral-7B-Instruct-v0.1', 'Mistral-7B-Instruct-v0.2',
    'Meta-Llama-3-8B-Instruct', 'Llama-3.1-8B-Instruct',
    'Qwen1.5-7B-Chat', 'Qwen2.5-7B-Instruct',
    'Llama-3.1-70B-Instruct', 'Qwen2.5-72B-Instruct',
]
model_labels = [
    'Mistral v0.1 (7B)', 'Mistral v0.2 (7B)',
    'Llama 3 (8B)', 'Llama 3.1 (8B)',
    'Qwen 1.5 (7B)', 'Qwen 2.5 (7B)',
    'Llama 3.1 (70B)', 'Qwen 2.5 (72B)',
]
framings = ['original', 'authority', 'leading', 'opinion']

def rate(model, framing, label):
    c = counts[model][framing]
    total = sum(c.values())
    return c.get(label, 0) / total if total > 0 else 0

kdg_s1 = np.zeros((len(model_order), len(framings)))
kdg_r = np.zeros((len(model_order), len(framings)))

for i, m in enumerate(model_order):
    s1_n = rate(m, 'neutral', 'S1')
    r_n = rate(m, 'neutral', 'R')
    for j, fr in enumerate(framings):
        kdg_s1[i, j] = rate(m, fr, 'S1') - s1_n
        kdg_r[i, j] = rate(m, fr, 'R') - r_n

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 6), sharey=True)
vmax = max(abs(kdg_s1).max(), abs(kdg_r).max())
vmin = -vmax

for ax, data, title in [(ax1, kdg_s1, r'KDG$_{S1}$ (Sycophancy Shift)'),
                          (ax2, kdg_r, r'KDG$_R$ (Refusal Shift)')]:
    im = ax.imshow(data, cmap='RdYlGn_r', vmin=vmin, vmax=vmax, aspect='auto')
    ax.set_xticks(range(len(framings)))
    ax.set_xticklabels([f.capitalize() for f in framings], fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    for i in range(len(model_order)):
        for j in range(len(framings)):
            val = data[i, j]
            color = 'white' if abs(val) > vmax * 0.6 else 'black'
            ax.text(j, i, f'{val:+.2f}', ha='center', va='center', fontsize=8, color=color)

    # Add horizontal line separating 7-8B from 70B+
    ax.axhline(y=5.5, color='white', linewidth=2, linestyle='--')

ax1.set_yticks(range(len(model_labels)))
ax1.set_yticklabels(model_labels, fontsize=9)

fig.subplots_adjust(right=0.88, wspace=0.08)
cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
fig.colorbar(im, cax=cbar_ax, label='Δ Rate (framed − neutral)')

plt.savefig('docs/figures/kdg_heatmap.png', dpi=200, bbox_inches='tight')
print('Saved docs/figures/kdg_heatmap.png')

for i, ml in enumerate(model_labels):
    for j, fr in enumerate(framings):
        if abs(kdg_s1[i,j]) > 0.01 or abs(kdg_r[i,j]) > 0.01:
            print(f"  {ml:22s} {fr:12s}: KDG_S1={kdg_s1[i,j]:+.3f}  KDG_R={kdg_r[i,j]:+.3f}")
