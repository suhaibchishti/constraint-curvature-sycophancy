"""Generate all Phase 3 paper figures. Run from repo root.

Usage: python scripts/plot_paper_figures.py

Outputs to docs/figures/:
  - kdg_heatmap.png
  - sharma_opinion_effect.png
  - basin_escape.png
  - entropy_kdg_scatter.png
"""
import json, glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, defaultdict

LABELS_GLOB = 'phase3/outputs/labels/*_labeled.jsonl'
ENTROPY_FILE = 'phase3/outputs/metrics/entropy_results.json'
OUT_DIR = 'docs/figures'

MODELS = [
    'Mistral-7B-Instruct-v0.1', 'Mistral-7B-Instruct-v0.2',
    'Meta-Llama-3-8B-Instruct', 'Llama-3.1-8B-Instruct',
    'Qwen1.5-7B-Chat', 'Qwen2.5-7B-Instruct'
]
SHORT = ['Mistral\nv0.1','Mistral\nv0.2','Llama 3','Llama 3.1','Qwen 1.5','Qwen 2.5']
SHORT_INLINE = ['Mistral v0.1','Mistral v0.2','Llama 3','Llama 3.1','Qwen 1.5','Qwen 2.5']
COLORS = ['#e74c3c','#e67e22','#3498db','#2980b9','#9b59b6','#27ae60']
FRAMINGS = ['opinion','leading','authority','original']


def load_data():
    data = []
    for f in sorted(glob.glob(LABELS_GLOB)):
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    data.append(json.loads(line))
    return data


def get_subsets(data, model, framing):
    return [r for r in data if model in r['model'] and r['framing'] == framing]


def correct_rate(subset):
    return sum(1 for r in subset if r['gpt4o_label'] in ['C','H']) / len(subset) if subset else 0


def s1_rate(subset):
    return sum(1 for r in subset if r['gpt4o_label'] == 'S1') / len(subset) if subset else 0


def plot_kdg_heatmap(data):
    mat = np.zeros((len(MODELS), len(FRAMINGS)))
    for i, m in enumerate(MODELS):
        neut = get_subsets(data, m, 'neutral')
        for j, fr in enumerate(FRAMINGS):
            framed = get_subsets(data, m, fr)
            mat[i, j] = correct_rate(neut) - correct_rate(framed)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(mat, cmap='RdYlGn_r', aspect='auto', vmin=-0.15, vmax=0.65)
    ax.set_xticks(range(len(FRAMINGS)))
    ax.set_xticklabels([f.capitalize() for f in FRAMINGS], fontsize=11)
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels(SHORT, fontsize=10)
    for i in range(len(MODELS)):
        for j in range(len(FRAMINGS)):
            v = mat[i, j]
            color = 'white' if abs(v) > 0.3 else 'black'
            ax.text(j, i, f'{v:+.2f}', ha='center', va='center', fontsize=11, fontweight='bold', color=color)
    ax.set_title('Knowledge Deployment Gap (KDG) by Model × Framing', fontsize=13, pad=12)
    ax.set_xlabel('Framing Condition', fontsize=12)
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('KDG (higher = more knowledge suppression)', fontsize=10)
    plt.tight_layout()
    plt.savefig(f'{OUT_DIR}/kdg_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved {OUT_DIR}/kdg_heatmap.png')


def plot_sharma(data):
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(MODELS))
    w = 0.35
    neut = [100 * s1_rate(get_subsets(data, m, 'neutral')) for m in MODELS]
    opin = [100 * s1_rate(get_subsets(data, m, 'opinion')) for m in MODELS]
    ax.bar(x - w/2, neut, w, label='Neutral', color='#3498db')
    ax.bar(x + w/2, opin, w, label='Opinion ("I believe...")', color='#e74c3c')
    for i in range(len(MODELS)):
        d = opin[i] - neut[i]
        y = max(neut[i], opin[i]) + 0.8
        ax.text(i, y, f'{d:+.1f}pp', ha='center', fontsize=10, fontweight='bold',
                color='#c0392b' if d > 0 else '#27ae60')
    ax.set_ylabel('S1 Rate (%)', fontsize=12)
    ax.set_title('Opinion Framing Effect on Sycophancy (Sharma Boundary Condition)', fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(SHORT, fontsize=10)
    ax.legend(fontsize=10)
    ax.set_ylim(0, max(max(neut), max(opin)) + 4)
    plt.tight_layout()
    plt.savefig(f'{OUT_DIR}/sharma_opinion_effect.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved {OUT_DIR}/sharma_opinion_effect.png')


def plot_basin_escape(data):
    s1_t0 = defaultdict(set)
    for r in data:
        if r['temperature'] == 0.0 and r['gpt4o_label'] == 'S1':
            for m in MODELS:
                if m in r['model']:
                    s1_t0[m].add((r['model'], r['fact_id'], r['framing']))

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(MODELS))
    stay, esc_c, esc_h, esc_o = [], [], [], []
    n_combos = []
    for m in MODELS:
        combos = s1_t0[m]
        n_combos.append(len(combos))
        if not combos:
            stay.append(0); esc_c.append(0); esc_h.append(0); esc_o.append(0)
            continue
        t07 = [r for r in data if r['temperature'] == 0.7 and (r['model'], r['fact_id'], r['framing']) in combos]
        t = len(t07)
        c = Counter(r['gpt4o_label'] for r in t07)
        stay.append(100 * c.get('S1', 0) / t)
        esc_h.append(100 * c.get('H', 0) / t)
        esc_c.append(100 * c.get('C', 0) / t)
        esc_o.append(100 * (t - c.get('S1',0) - c.get('C',0) - c.get('H',0)) / t)

    ax.bar(x, stay, 0.6, label='Stay S1', color='#e74c3c')
    ax.bar(x, esc_h, 0.6, bottom=stay, label='Escape → H (hedge)', color='#f39c12')
    b2 = [a+b for a,b in zip(stay, esc_h)]
    ax.bar(x, esc_c, 0.6, bottom=b2, label='Escape → C (correct)', color='#2ecc71')
    b3 = [a+b for a,b in zip(b2, esc_c)]
    ax.bar(x, esc_o, 0.6, bottom=b3, label='Escape → other', color='#95a5a6')
    for i in range(len(MODELS)):
        ax.text(i, 102, f'n={n_combos[i]}\n{100-stay[i]:.0f}% escape', ha='center', fontsize=9, fontweight='bold')
    ax.set_ylabel('% of T=0 S1 responses at T=0.7', fontsize=11)
    ax.set_title('Basin Escape: What happens to T=0 sycophantic responses at T=0.7?', fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(SHORT, fontsize=10)
    ax.legend(loc='center right', fontsize=9)
    ax.set_ylim(0, 118)
    plt.tight_layout()
    plt.savefig(f'{OUT_DIR}/basin_escape.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved {OUT_DIR}/basin_escape.png')


def plot_entropy_kdg(data):
    with open(ENTROPY_FILE) as f:
        entropy_data = json.load(f)

    kdg_vals, ent_vals = [], []
    for m in MODELS:
        neut = get_subsets(data, m, 'neutral')
        framed = [r for r in data if m in r['model'] and r['framing'] != 'neutral']
        kdg_vals.append(correct_rate(neut) - correct_rate(framed))
        vals = [r['entropy'] for r in entropy_data if m in r['model'] and r['temperature'] == 0.7]
        ent_vals.append(sum(vals) / len(vals) if vals else 0)

    fig, ax = plt.subplots(figsize=(10, 7))
    offsets = [(0.012,-0.003),(0.012,0.002),(-0.005,0.004),(0.012,-0.003),(0.008,0.003),(0.008,-0.004)]
    for i in range(len(MODELS)):
        ax.scatter(kdg_vals[i], ent_vals[i], s=250, c=COLORS[i], zorder=5, edgecolors='black', linewidth=1)
        dx, dy = offsets[i]
        ax.annotate(SHORT_INLINE[i], (kdg_vals[i]+dx, ent_vals[i]+dy), fontsize=12, fontweight='bold', color=COLORS[i])

    ax.axhline(y=0.08, color='grey', linewidth=0.8, linestyle='--', alpha=0.4)
    ax.axvline(x=0.05, color='grey', linewidth=0.8, linestyle='--', alpha=0.4)
    ax.text(-0.03, 0.112, 'Noisy but robust\n(variable, correct)', fontsize=10, fontstyle='italic', color='#7f8c8d', ha='center', va='top')
    ax.text(0.16, 0.112, 'Noisy basin\n(variable, suppressible)', fontsize=10, fontstyle='italic', color='#7f8c8d', ha='center', va='top')
    ax.text(-0.03, 0.048, 'Flat landscape\n(robust alignment)', fontsize=10, fontstyle='italic', color='#7f8c8d', ha='center', va='bottom')
    ax.text(0.16, 0.048, 'Deep basin\n(deterministic sycophant)', fontsize=10, fontstyle='italic', color='#7f8c8d', ha='center', va='bottom')
    ax.set_xlabel('Mean KDG (knowledge suppression under framing)', fontsize=12)
    ax.set_ylabel('Mean Entropy at T=0.7 (behavioral variability)', fontsize=12)
    ax.set_title('Basin Depth as Alignment Signature: Entropy × KDG', fontsize=14)
    ax.set_xlim(-0.06, 0.26)
    ax.set_ylim(0.045, 0.115)
    plt.tight_layout()
    plt.savefig(f'{OUT_DIR}/entropy_kdg_scatter.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved {OUT_DIR}/entropy_kdg_scatter.png')


if __name__ == '__main__':
    data = load_data()
    print(f'Loaded {len(data)} labeled responses')
    plot_kdg_heatmap(data)
    plot_sharma(data)
    plot_basin_escape(data)
    plot_entropy_kdg(data)
    print('Done.')
