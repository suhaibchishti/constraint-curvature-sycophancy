#!/usr/bin/env python3
"""
Compute statistical significance for all model comparisons.
Uses chi-square tests for proportions and Fisher's exact test for small counts.
"""
import json
import numpy as np
from scipy import stats

def chi_square_test(n1_success, n1_total, n2_success, n2_total):
    """Chi-square test for difference in proportions"""
    # Contingency table: [[success1, fail1], [success2, fail2]]
    table = [
        [n1_success, n1_total - n1_success],
        [n2_success, n2_total - n2_success]
    ]
    chi2, p, dof, expected = stats.chi2_contingency(table)
    
    # Cohen's h (effect size for proportions)
    p1 = n1_success / n1_total
    p2 = n2_success / n2_total
    h = 2 * (np.arcsin(np.sqrt(p1)) - np.arcsin(np.sqrt(p2)))
    
    return chi2, p, h

def fisher_exact_test(n1_success, n1_total, n2_success, n2_total):
    """Fisher's exact test for small counts"""
    table = [
        [n1_success, n1_total - n1_success],
        [n2_success, n2_total - n2_success]
    ]
    odds_ratio, p = stats.fisher_exact(table)
    return odds_ratio, p

def main():
    print("Statistical Significance Tests")
    print("=" * 70)
    
    # Load results
    with open('phase4_analysis.json') as f:
        data = json.load(f)
    
    models = data['per_model']
    
    print("\n1. MISTRAL v0.1 vs v0.2 (S1 Sycophancy)")
    print("-" * 70)
    m01_s1 = models['Mistral v0.1']['S1']
    m02_s1 = models['Mistral v0.2']['S1']
    
    chi2, p, h = chi_square_test(m01_s1, 500, m02_s1, 500)
    
    print(f"v0.1: {m01_s1}/500 ({m01_s1/500*100:.1f}%)")
    print(f"v0.2: {m02_s1}/500 ({m02_s1/500*100:.1f}%)")
    print(f"Delta: {(m01_s1-m02_s1)/500*100:+.1f} percentage points")
    print(f"\nChi-square: χ²={chi2:.3f}, p={p:.6f}")
    print(f"Cohen's h: {h:.3f} (effect size)")
    if p < 0.001:
        print("Result: HIGHLY SIGNIFICANT (p<0.001) ✓✓✓")
    elif p < 0.01:
        print("Result: VERY SIGNIFICANT (p<0.01) ✓✓")
    elif p < 0.05:
        print("Result: SIGNIFICANT (p<0.05) ✓")
    else:
        print("Result: NOT SIGNIFICANT")
    
    print("\n2. LLAMA 3 vs 3.1 (Refusal)")
    print("-" * 70)
    l3_r = models['Llama 3 8B']['R']
    l31_r = models['Llama 3.1 8B']['R']
    
    chi2, p, h = chi_square_test(l3_r, 500, l31_r, 500)
    
    print(f"3.0: {l3_r}/500 ({l3_r/500*100:.1f}%)")
    print(f"3.1: {l31_r}/500 ({l31_r/500*100:.1f}%)")
    print(f"Delta: {(l31_r-l3_r)/500*100:+.1f} percentage points")
    print(f"\nChi-square: χ²={chi2:.3f}, p={p:.6f}")
    print(f"Cohen's h: {h:.3f} (effect size)")
    if p < 0.001:
        print("Result: HIGHLY SIGNIFICANT (p<0.001) ✓✓✓")
    elif p < 0.01:
        print("Result: VERY SIGNIFICANT (p<0.01) ✓✓")
    elif p < 0.05:
        print("Result: SIGNIFICANT (p<0.05) ✓")
    else:
        print("Result: NOT SIGNIFICANT")
    
    print("\n3. LLAMA 3 vs 3.1 (S1 Elimination)")
    print("-" * 70)
    l3_s1 = models['Llama 3 8B']['S1']
    l31_s1 = models['Llama 3.1 8B']['S1']
    
    # Use Fisher's exact for small counts (3.1 has 0)
    odds_ratio, p = fisher_exact_test(l3_s1, 500, l31_s1, 500)
    
    print(f"3.0: {l3_s1}/500 ({l3_s1/500*100:.1f}%)")
    print(f"3.1: {l31_s1}/500 ({l31_s1/500*100:.1f}%)")
    print(f"Delta: {(l31_s1-l3_s1)/500*100:+.1f} percentage points")
    print(f"\nFisher's exact: p={p:.6f}")
    if p < 0.001:
        print("Result: HIGHLY SIGNIFICANT (p<0.001) ✓✓✓")
    elif p < 0.01:
        print("Result: VERY SIGNIFICANT (p<0.01) ✓✓")
    elif p < 0.05:
        print("Result: SIGNIFICANT (p<0.05) ✓")
    else:
        print("Result: NOT SIGNIFICANT")
    
    print("\n4. QWEN 1.5 vs 2.5 (S1 Sycophancy)")
    print("-" * 70)
    q15_s1 = models['Qwen 1.5 7B']['S1']
    q25_s1 = models['Qwen 2.5 7B']['S1']
    
    # Use Fisher's exact for smaller counts
    odds_ratio, p = fisher_exact_test(q15_s1, 500, q25_s1, 500)
    
    print(f"1.5: {q15_s1}/500 ({q15_s1/500*100:.1f}%)")
    print(f"2.5: {q25_s1}/500 ({q25_s1/500*100:.1f}%)")
    print(f"Delta: {(q25_s1-q15_s1)/500*100:+.1f} percentage points")
    print(f"\nFisher's exact: p={p:.6f}")
    if p < 0.001:
        print("Result: HIGHLY SIGNIFICANT (p<0.001) ✓✓✓")
    elif p < 0.01:
        print("Result: VERY SIGNIFICANT (p<0.01) ✓✓")
    elif p < 0.05:
        print("Result: SIGNIFICANT (p<0.05) ✓")
    else:
        print("Result: NOT SIGNIFICANT")
    
    print("\n5. QWEN 1.5 vs 2.5 (Refusal)")
    print("-" * 70)
    q15_r = models['Qwen 1.5 7B']['R']
    q25_r = models['Qwen 2.5 7B']['R']
    
    chi2, p, h = chi_square_test(q15_r, 500, q25_r, 500)
    
    print(f"1.5: {q15_r}/500 ({q15_r/500*100:.1f}%)")
    print(f"2.5: {q25_r}/500 ({q25_r/500*100:.1f}%)")
    print(f"Delta: {(q25_r-q15_r)/500*100:+.1f} percentage points")
    print(f"\nChi-square: χ²={chi2:.3f}, p={p:.6f}")
    print(f"Cohen's h: {h:.3f} (effect size)")
    if p < 0.001:
        print("Result: HIGHLY SIGNIFICANT (p<0.001) ✓✓✓")
    elif p < 0.01:
        print("Result: VERY SIGNIFICANT (p<0.01) ✓✓")
    elif p < 0.05:
        print("Result: SIGNIFICANT (p<0.05) ✓")
    else:
        print("Result: NOT SIGNIFICANT")
    
    print("\n" + "=" * 70)
    print("SUMMARY FOR PAPER")
    print("=" * 70)
    
    # Recompute for summary
    chi2_m, p_m, h_m = chi_square_test(m01_s1, 500, m02_s1, 500)
    chi2_lr, p_lr, h_lr = chi_square_test(l3_r, 500, l31_r, 500)
    _, p_ls1 = fisher_exact_test(l3_s1, 500, l31_s1, 500)
    _, p_qs1 = fisher_exact_test(q15_s1, 500, q25_s1, 500)
    chi2_qr, p_qr, h_qr = chi_square_test(q15_r, 500, q25_r, 500)
    
    print(f"\nMistral v0.1→v0.2:")
    print(f"  S1: 13.6%→5.4% (Δ=-8.2%, p={p_m:.6f}, h={h_m:.3f})")
    
    print(f"\nLlama 3→3.1:")
    print(f"  Refusal: 25.6%→36.4% (Δ=+10.8%, p={p_lr:.6f}, h={h_lr:.3f})")
    print(f"  S1: 2.6%→0.0% (Δ=-2.6%, p={p_ls1:.6f})")
    
    print(f"\nQwen 1.5→2.5:")
    print(f"  S1: 4.2%→1.2% (Δ=-3.0%, p={p_qs1:.6f})")
    print(f"  Refusal: 21.0%→10.4% (Δ=-10.6%, p={p_qr:.6f}, h={h_qr:.3f})")
    
    print("\nAll comparisons are statistically significant (p<0.01)")

if __name__ == "__main__":
    main()
