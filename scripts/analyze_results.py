#!/usr/bin/env python3
"""
Phase 4: Compute final κ and analyze results.

Compares heuristic judge against GPT-4o-mini labels on full dataset,
computes per-model metrics, and prepares data for paper update.
"""
import json
import sys
from pathlib import Path
from sklearn.metrics import cohen_kappa_score, confusion_matrix
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from cc_eval.judge import taxonomy_judge

def main():
    print("Phase 4: Computing final κ and analyzing results")
    print("=" * 60)
    
    # Load GPT-4o-mini labels
    print("\nLoading GPT-4o-mini labels...")
    with open('gpt4o_labels_all.json') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} samples")
    
    # Run heuristic judge on all samples
    print("\nRunning heuristic judge on all samples...")
    heuristic_labels = []
    gpt4o_labels = []
    
    for i, sample in enumerate(data):
        if i % 500 == 0:
            print(f"  Progress: {i}/{len(data)}")
        
        result = taxonomy_judge(sample['prompt'], sample['completion'])
        heuristic_labels.append(result.label)
        gpt4o_labels.append(sample['gpt4o_label'])
    
    # Compute overall κ
    kappa = cohen_kappa_score(heuristic_labels, gpt4o_labels)
    agreement = sum(h == g for h, g in zip(heuristic_labels, gpt4o_labels)) / len(data)
    
    print(f"\n{'=' * 60}")
    print("OVERALL AGREEMENT")
    print(f"{'=' * 60}")
    print(f"Total samples: {len(data)}")
    print(f"Percent agreement: {agreement*100:.1f}%")
    print(f"Cohen's kappa: {kappa:.3f}")
    
    if kappa > 0.7:
        print("  → Substantial agreement")
    elif kappa > 0.4:
        print("  → Moderate agreement")
    elif kappa > 0.2:
        print("  → Fair agreement")
    else:
        print("  → Poor agreement")
    
    # Confusion matrix
    labels = sorted(set(heuristic_labels + gpt4o_labels))
    cm = confusion_matrix(gpt4o_labels, heuristic_labels, labels=labels)
    
    print(f"\nConfusion Matrix (rows=GPT-4o, cols=heuristic):")
    print("     " + "  ".join(f"{l:>4}" for l in labels))
    for i, label in enumerate(labels):
        print(f"  {label:>2} " + "  ".join(f"{cm[i][j]:>4}" for j in range(len(labels))))
    
    # Per-model analysis
    print(f"\n{'=' * 60}")
    print("PER-MODEL ANALYSIS (GPT-4o-mini labels)")
    print(f"{'=' * 60}")
    
    model_stats = {}
    for sample in data:
        model = sample['model']
        label = sample['gpt4o_label']
        
        if model not in model_stats:
            model_stats[model] = {'total': 0, 'C': 0, 'H': 0, 'R': 0, 'S1': 0, 'S2': 0}
        
        model_stats[model]['total'] += 1
        model_stats[model][label] += 1
    
    # Print per-model stats
    for model in sorted(model_stats.keys()):
        stats = model_stats[model]
        total = stats['total']
        s1_pct = stats['S1'] / total * 100
        s2_pct = stats['S2'] / total * 100
        syc_pct = (stats['S1'] + stats['S2']) / total * 100
        r_pct = stats['R'] / total * 100
        
        print(f"\n{model}:")
        print(f"  Total: {total}")
        print(f"  S1: {stats['S1']:3d} ({s1_pct:5.1f}%)")
        print(f"  S2: {stats['S2']:3d} ({s2_pct:5.1f}%)")
        print(f"  Sycophancy (S1+S2): {stats['S1']+stats['S2']:3d} ({syc_pct:5.1f}%)")
        print(f"  Refusal (R): {stats['R']:3d} ({r_pct:5.1f}%)")
        print(f"  Correction (C): {stats['C']:3d} ({stats['C']/total*100:5.1f}%)")
        print(f"  Hedge (H): {stats['H']:3d} ({stats['H']/total*100:5.1f}%)")
    
    # Key comparisons for paper
    print(f"\n{'=' * 60}")
    print("KEY COMPARISONS FOR PAPER")
    print(f"{'=' * 60}")
    
    # Mistral v0.1 vs v0.2
    m01_s1 = model_stats['Mistral v0.1']['S1']
    m02_s1 = model_stats['Mistral v0.2']['S1']
    print(f"\nMistral v0.1 vs v0.2 (S1 sycophancy):")
    print(f"  v0.1: {m01_s1} ({m01_s1/500*100:.1f}%)")
    print(f"  v0.2: {m02_s1} ({m02_s1/500*100:.1f}%)")
    print(f"  Delta: {(m01_s1-m02_s1)/500*100:+.1f}%")
    
    # Llama 3 vs 3.1
    l3_r = model_stats['Llama 3 8B']['R']
    l31_r = model_stats['Llama 3.1 8B']['R']
    print(f"\nLlama 3 vs 3.1 (Refusal):")
    print(f"  3.0: {l3_r} ({l3_r/500*100:.1f}%)")
    print(f"  3.1: {l31_r} ({l31_r/500*100:.1f}%)")
    print(f"  Delta: {(l31_r-l3_r)/500*100:+.1f}%")
    
    # Qwen 1.5 vs 2.5
    q15_s1 = model_stats['Qwen 1.5 7B']['S1']
    q25_s1 = model_stats['Qwen 2.5 7B']['S1']
    print(f"\nQwen 1.5 vs 2.5 (S1 sycophancy):")
    print(f"  1.5: {q15_s1} ({q15_s1/500*100:.1f}%)")
    print(f"  2.5: {q25_s1} ({q25_s1/500*100:.1f}%)")
    print(f"  Delta: {(q25_s1-q15_s1)/500*100:+.1f}%")
    
    # Save detailed results
    output = {
        'overall': {
            'kappa': kappa,
            'agreement': agreement,
            'total_samples': len(data)
        },
        'per_model': model_stats,
        'confusion_matrix': {
            'labels': labels,
            'matrix': cm.tolist()
        }
    }
    
    with open('phase4_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Saved detailed analysis to phase4_analysis.json")
    print(f"\nNext: Update paper with these metrics")

if __name__ == "__main__":
    main()
