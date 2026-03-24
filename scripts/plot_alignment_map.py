#!/usr/bin/env python3
"""
Generate the Alignment Map scatter plot (Figure 1) for the paper.

Plots S1 sycophancy rate vs refusal rate for all 6 models,
with arrows showing the trajectory from older → newer versions.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Model data: (name, S1%, Refusal%, family, version)
models = [
    ("Mistral v0.1", 13.6, 8.0,  "Mistral", "old"),
    ("Mistral v0.2", 5.4,  10.6, "Mistral", "new"),
    ("Llama 3",      2.6,  25.6, "Llama",   "old"),
    ("Llama 3.1",    0.0,  36.4, "Llama",   "new"),
    ("Qwen 1.5",     4.2,  21.0, "Qwen",    "old"),
    ("Qwen 2.5",     1.2,  10.4, "Qwen",    "new"),
]

# Colors per family
colors = {"Mistral": "#4ECDC4", "Llama": "#FF6B6B", "Qwen": "#45B7D1"}
markers_old = {"Mistral": "o", "Llama": "o", "Qwen": "o"}

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

# Plot points
for name, s1, ref, family, ver in models:
    marker = 's' if ver == 'new' else 'o'
    edge = 'white' if ver == 'new' else 'none'
    size = 120 if ver == 'new' else 80
    ax.scatter(ref, s1, c=colors[family], marker=marker, s=size,
               edgecolors=edge, linewidths=1.5, zorder=5)

    # Label positioning
    offsets = {
        "Mistral v0.1": (1.5, 0.5),
        "Mistral v0.2": (1.5, 0.3),
        "Llama 3":      (-1.5, 0.8),
        "Llama 3.1":    (1.5, 0.3),
        "Qwen 1.5":     (1.5, 0.5),
        "Qwen 2.5":     (-1.5, -1.0),
    }
    ha_map = {
        "Mistral v0.1": "left",
        "Mistral v0.2": "left",
        "Llama 3":      "right",
        "Llama 3.1":    "left",
        "Qwen 1.5":     "left",
        "Qwen 2.5":     "right",
    }
    dx, dy = offsets[name]
    ax.annotate(name, (ref, s1), xytext=(ref + dx, s1 + dy),
                fontsize=9, color='white', fontweight='bold',
                ha=ha_map[name], va='bottom')

# Draw arrows (old → new)
pairs = [("Mistral", 0, 1), ("Llama", 2, 3), ("Qwen", 4, 5)]
for family, i_old, i_new in pairs:
    x0, y0 = models[i_old][2], models[i_old][1]
    x1, y1 = models[i_new][2], models[i_new][1]
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="->", color=colors[family],
                                lw=2, alpha=0.7))

# Quadrant shading
ax.axhline(y=3.0, color='white', linestyle='--', alpha=0.2)
ax.axvline(x=20.0, color='white', linestyle='--', alpha=0.2)

# Quadrant labels
ax.text(5, 14.5, "High Sycophancy\nLow Refusal", fontsize=8, color='#888',
        ha='center', va='center', style='italic')
ax.text(35, 14.5, "High Sycophancy\nHigh Refusal", fontsize=8, color='#888',
        ha='center', va='center', style='italic')
ax.text(5, -0.8, "✓ IDEAL\nLow Syc + Low Refusal", fontsize=8,
        color='#4ECDC4', ha='center', va='center', fontweight='bold')
ax.text(35, -0.8, "Over-Constraint\nLow Syc + High Refusal", fontsize=8,
        color='#FF6B6B', ha='center', va='center', fontweight='bold')

# Styling
ax.set_xlabel("Refusal Rate (%)", fontsize=12, color='white', labelpad=10)
ax.set_ylabel("S1 Sycophancy Rate (%)", fontsize=12, color='white', labelpad=10)
ax.set_title("Figure 1: Alignment Map — Sycophancy vs Refusal",
             fontsize=13, color='white', fontweight='bold', pad=15)

ax.set_xlim(-2, 42)
ax.set_ylim(-2, 16)
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.1, color='white')

# Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors["Mistral"],
           markersize=8, label='Mistral', linestyle='None'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors["Llama"],
           markersize=8, label='Llama', linestyle='None'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors["Qwen"],
           markersize=8, label='Qwen', linestyle='None'),
    Line2D([0], [0], marker='o', color='gray', label='Older version',
           markersize=7, linestyle='None'),
    Line2D([0], [0], marker='s', color='gray', markeredgecolor='white',
           label='Newer version', markersize=7, linestyle='None'),
]
legend = ax.legend(handles=legend_elements, loc='upper left', fontsize=9,
                   facecolor='#16213e', edgecolor='#444', labelcolor='white')

plt.tight_layout()
outpath = 'docs/figures/alignment_map.png'
import os
os.makedirs('docs/figures', exist_ok=True)
plt.savefig(outpath, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"✓ Saved to {outpath}")
