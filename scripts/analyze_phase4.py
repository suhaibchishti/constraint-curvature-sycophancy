#!/usr/bin/env python3
"""
Phase 4: Analyze 70B results and compare against 7-8B baseline.

Usage:
    python scripts/analyze_phase4.py

Outputs:
    phase4/outputs/phase4_kdg_comparison.json
    phase4/outputs/phase4_summary.md
"""
import json, glob
from collections import defaultdict

PHASE3_LABELS = "huggingface_upload/phase3_distributional"
PHASE4_LABELS = "phase4/outputs"

MODEL_LABELS = {
    # Phase 3 (7-8B)
    "Mistral-7B-Instruct-v0.1":  "Mistral v0.1 (7B)",
    "Mistral-7B-Instruct-v0.2":  "Mistral v0.2 (7B)",
    "Meta-Llama-3-8B-Instruct":  "Llama 3 (8B)",
    "Llama-3.1-8B-Instruct":     "Llama 3.1 (8B)",
    "Qwen1.5-7B-Chat":           "Qwen 1.5 (7B)",
    "Qwen2.5-7B-Instruct":       "Qwen 2.5 (7B)",
    # Phase 4 (70B)
    "Llama-3.1-70B-Instruct":    "Llama 3.1 (70B)",
    "Qwen2.5-72B-Instruct":      "Qwen 2.5 (72B)",
}

FRAMINGS = ["original", "authority", "leading", "opinion"]


def load_counts(label_dir, model_short):
    """Load label counts per (framing, temperature) for a model."""
    counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    pattern = f"{label_dir}/{model_short}*_labeled.jsonl"
    files = glob.glob(pattern)
    if not files:
        return None
    for f in files:
        for line in open(f):
            d = json.loads(line)
            m = d["model"].split("/")[-1]
            counts[m][d["framing"]][d["gpt4o_label"]] += 1
    return counts


def kdg_decomp(model_counts, framing):
    """Compute KDG, KDG_S1, KDG_R for a model-framing pair (all temps)."""
    cn = model_counts["original"]
    cf = model_counts[framing]
    tn = sum(cn.values())
    tf = sum(cf.values())
    if tn == 0 or tf == 0:
        return None
    p_ch_n = (cn.get("C", 0) + cn.get("H", 0)) / tn
    p_ch_f = (cf.get("C", 0) + cf.get("H", 0)) / tf
    kdg    = p_ch_n - p_ch_f
    kdg_s1 = cf.get("S1", 0) / tf - cn.get("S1", 0) / tn
    kdg_r  = cf.get("R",  0) / tf - cn.get("R",  0) / tn
    return {"kdg": round(kdg, 3), "kdg_s1": round(kdg_s1, 3), "kdg_r": round(kdg_r, 3)}


def basin_escape(labeled_path):
    """Compute escape rate at T=0.7 for combos that are deterministically S1 at T=0.0.

    Returns dict with stay_s1, escape_to_c, escape_to_h, total_escape rates,
    or None if no data available.
    """
    import glob
    from collections import defaultdict

    files = glob.glob(labeled_path)
    if not files:
        return None

    # Group by (model, fact_id, framing) → {temp: [labels]}
    combos = defaultdict(lambda: defaultdict(list))
    for f in files:
        for line in open(f):
            d = json.loads(line)
            key = (d["model"].split("/")[-1], d["fact_id"], d["framing"])
            combos[key][d["temperature"]].append(d["gpt4o_label"])

    # Find combos where ALL samples at T=0.0 are S1
    s1_at_t0 = []
    for key, temps in combos.items():
        t0_labels = temps.get(0.0, [])
        if t0_labels and all(l == "S1" for l in t0_labels):
            s1_at_t0.append(key)

    if not s1_at_t0:
        return {"n_s1_at_t0": 0}

    # Track what happens at T=0.7
    stay_s1 = escape_c = escape_h = escape_other = 0
    total = 0
    for key in s1_at_t0:
        t7_labels = combos[key].get(0.7, [])
        for lbl in t7_labels:
            total += 1
            if lbl == "S1":
                stay_s1 += 1
            elif lbl == "C":
                escape_c += 1
            elif lbl == "H":
                escape_h += 1
            else:
                escape_other += 1

    if total == 0:
        return {"n_s1_at_t0": len(s1_at_t0), "total_samples_t7": 0}

    return {
        "n_s1_at_t0":    len(s1_at_t0),
        "total_samples":  total,
        "stay_s1":        round(stay_s1 / total, 3),
        "escape_to_c":    round(escape_c / total, 3),
        "escape_to_h":    round(escape_h / total, 3),
        "escape_other":   round(escape_other / total, 3),
        "total_escape":   round((escape_c + escape_h + escape_other) / total, 3),
    }


def main():
    import os
    os.makedirs("phase4/outputs", exist_ok=True)

    results = {}

    # Load Phase 3 data
    for f in glob.glob(f"{PHASE3_LABELS}/*_labeled.jsonl"):
        for line in open(f):
            d = json.loads(line)
            m = d["model"].split("/")[-1]
            if m not in results:
                results[m] = defaultdict(lambda: defaultdict(int))
            results[m][d["framing"]][d["gpt4o_label"]] += 1

    # Load Phase 4 data
    for f in glob.glob(f"{PHASE4_LABELS}/*_labeled.jsonl"):
        for line in open(f):
            d = json.loads(line)
            m = d["model"].split("/")[-1]
            if m not in results:
                results[m] = defaultdict(lambda: defaultdict(int))
            results[m][d["framing"]][d["gpt4o_label"]] += 1

    # Compute KDG for all models
    comparison = {}
    for model, counts in results.items():
        label = MODEL_LABELS.get(model, model)
        comparison[label] = {}
        for framing in FRAMINGS:
            decomp = kdg_decomp(counts, framing)
            if decomp:
                comparison[label][framing] = decomp

    # Save JSON
    with open("phase4/outputs/phase4_kdg_comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)

    # Print summary table
    print(f"\n{'Model':<25} {'Framing':<12} {'KDG':>8} {'KDG_S1':>8} {'KDG_R':>8}")
    print("-" * 65)
    for label in sorted(comparison):
        for framing in ["authority", "opinion"]:
            d = comparison[label].get(framing)
            if d:
                print(f"{label:<25} {framing:<12} {d['kdg']:>+8.3f} {d['kdg_s1']:>+8.3f} {d['kdg_r']:>+8.3f}")

    print(f"\nFull results saved to phase4/outputs/phase4_kdg_comparison.json")

    # Basin escape analysis (Phase 4 only)
    print(f"\n{'='*65}")
    print("Basin Escape Analysis (T=0.0 → T=0.7)")
    print(f"{'='*65}")
    for model_key in ["Llama-3.1-70B-Instruct", "Qwen2.5-72B-Instruct"]:
        esc = basin_escape(f"{PHASE4_LABELS}/{model_key}*_labeled.jsonl")
        label = MODEL_LABELS.get(model_key, model_key)
        if esc and esc.get("total_samples", 0) > 0:
            print(f"\n  {label}:")
            print(f"    S1 combos at T=0: {esc['n_s1_at_t0']}")
            print(f"    Stay S1:     {esc['stay_s1']:.1%}")
            print(f"    Escape → C:  {esc['escape_to_c']:.1%}")
            print(f"    Escape → H:  {esc['escape_to_h']:.1%}")
            print(f"    Total escape: {esc['total_escape']:.1%}")
        elif esc:
            print(f"\n  {label}: {esc.get('n_s1_at_t0', 0)} S1 combos at T=0 (no T=0.7 data)")
        else:
            print(f"\n  {label}: No labeled data found")

    # Sharma opinion boundary (Δ S1 = opinion − neutral)
    print(f"\n{'='*65}")
    print("Sharma Boundary Check (ΔS1 = opinion − neutral)")
    print(f"{'='*65}")
    for label in sorted(comparison):
        op = comparison[label].get("opinion")
        if op:
            delta_pp = op["kdg_s1"] * 100  # already opinion S1 - neutral S1
            sign = "+" if delta_pp >= 0 else ""
            print(f"  {label:<25} {sign}{delta_pp:.1f} pp")


if __name__ == "__main__":
    main()
