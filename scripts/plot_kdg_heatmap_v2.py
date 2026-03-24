"""Generate two-panel KDG heatmap: KDG_S1 (sycophancy) vs KDG_R (refusal)."""
import json, glob, numpy as np, matplotlib.pyplot as plt
from collections import defaultdict

# Compute rates per model/framing at T=0.0
counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for f in sorted(glob.glob('huggingface_upload/phase3_distributional/*_labeled.jsonl')):
    for line in open(f):
        d = json.loads(line)
        if d['temperature'] == 0.0:
            model = d['model'].split('/')[-1]
            counts[model][d['framing']][d['gpt4o_label']] += 1

model_order = [
    'Mistral-7B-Instruct-v0.1', 'Mistral-7B-Instruct-v0.2',
    'Meta-Llama-3-8B-Instruct', 'Llama-3.1-8B-Instruct',
    'Qwen1.5-7B-Chat', 'Qwen2.5-7B-Instruct'
]
model_labels = ['Mistral v0.1', 'Mistral v0.2', 'Llama 3', 'Llama 3.1', 'Qwen 1.5', 'Qwen 2.5']
framings = ['original', 'authority', 'leading', 'opinion']

def rate(model, framing, label):
    c = counts[model][framing]
    total = sum(c.values())
    return c.get(label, 0) / total if total > 0 else 0

def neutral_rate(model, label):
    return rate(model, 'neutral', label)

# Build KDG_S1 and KDG_R matrices
kdg_s1 = np.zeros((len(model_order), len(framings)))
kdg_r = np.zeros((len(model_order), len(framings)))

for i, m in enumerate(model_order):
    s1_n = neutral_rate(m, 'S1')
    r_n = neutral_rate(m, 'R')
    for j, fr in enumerate(framings):
        s1_f = rate(m, fr, 'S1')
        r_f = rate(m, fr, 'R')
        kdg_s1[i, j] = s1_f - s1_n  # positive = more sycophancy under framing
        kdg_r[i, j] = r_f - r_n      # positive = more refusal under framing

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)

vmax = max(abs(kdg_s1).max(), abs(kdg_r).max())
vmin = -vmax

for ax, data, title in [(ax1, kdg_s1, r'KDG$_{S1}$ (Sycophancy Shift)'),
                          (ax2, kdg_r, r'KDG$_R$ (Refusal Shift)')]:
    im = ax.imshow(data, cmap='RdYlGn_r', vmin=vmin, vmax=vmax, aspect='auto')
    ax.set_xticks(range(len(framings)))
    ax.set_xticklabels([f.capitalize() for f in framings], fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    # Annotate cells
    for i in range(len(model_order)):
        for j in range(len(framings)):
            val = data[i, j]
            color = 'white' if abs(val) > vmax * 0.6 else 'black'
            ax.text(j, i, f'{val:+.2f}', ha='center', va='center', fontsize=9, color=color)

ax1.set_yticks(range(len(model_labels)))
ax1.set_yticklabels(model_labels, fontsize=10)

fig.subplots_adjust(right=0.88, wspace=0.08)
cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
fig.colorbar(im, cax=cbar_ax, label='Δ Rate (framed − neutral)')

plt.savefig('docs/figures/kdg_heatmap.png', dpi=200, bbox_inches='tight')
print('Saved docs/figures/kdg_heatmap.png')
