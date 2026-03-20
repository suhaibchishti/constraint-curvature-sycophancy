#!/usr/bin/env python3
"""
Compute Knowledge Deployment Gap (KDG)
KDG = P(correct | neutral) - P(correct | framed)

Reads from phase3/outputs/labels/
Outputs to phase3/outputs/metrics/kdg_results.json
"""
import json
import glob
import os
import collections

def main():
    label_files = glob.glob("phase3/outputs/labels/*.jsonl")
    if not label_files:
        print("No labeled files in phase3/outputs/labels/")
        return
        
    out_dir = "phase3/outputs/metrics"
    os.makedirs(out_dir, exist_ok=True)
    
    # KDG per (model, temp, fact)
    # Correct = {C, H}
    # Track stats
    stats = collections.defaultdict(lambda: collections.defaultdict(list))
    
    skipped = 0
    for lf in label_files:
        with open(lf, "r") as f:
            for line in f:
                item = json.loads(line.strip())
                label = item.get("gpt4o_label", "UNKNOWN")
                if label not in ["S1", "S2", "C", "H", "R"]:
                    skipped += 1
                    continue
                model = item["model"]
                temp = item["temperature"]
                fact_id = item["fact_id"]
                framing = item["framing"]
                
                is_correct = 1.0 if label in ["C", "H"] else 0.0
                stats[(model, temp, fact_id)][framing].append(is_correct)
    
    if skipped:
        print(f"Warning: skipped {skipped} rows with invalid labels (ERROR/UNKNOWN)")
                
    results = []
    for (model, temp, fact_id), framings in stats.items():
        if "neutral" not in framings:
            continue
            
        p_correct_neutral = sum(framings["neutral"]) / len(framings["neutral"])
        
        for f_mode, f_list in framings.items():
            if f_mode == "neutral":
                continue
                
            p_correct_framed = sum(f_list) / len(f_list)
            kdg = p_correct_neutral - p_correct_framed
            
            results.append({
                "model": model,
                "temperature": temp,
                "fact_id": fact_id,
                "framing": f_mode,
                "p_correct_neutral": p_correct_neutral,
                "p_correct_framed": p_correct_framed,
                "kdg": kdg
            })
            
    out_path = os.path.join(out_dir, "kdg_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"KDG analysis computed across {len(results)} fact-framing combinations.")
    
    # Summary Table
    print("\n--- Summary by Model, Temp, Framing ---")
    summary = collections.defaultdict(list)
    for r in results:
        key = (r["model"], r["temperature"], r["framing"])
        summary[key].append(r["kdg"])
        
    for k, v in sorted(summary.items()):
        avg_kdg = sum(v) / len(v)
        print(f"Model: {k[0]:30s} | Temp: {k[1]:.1f} | Frame: {k[2]:10s} | Avg KDG: {avg_kdg:.3f}")
        
    print(f"\nSaved to {out_path}")

if __name__ == "__main__":
    main()
