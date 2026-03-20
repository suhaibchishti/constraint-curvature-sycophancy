#!/usr/bin/env python3
"""
Compute Response Entropy
H = -sum_i p_i log2(p_i) over labels {S1, S2, C, H, R}
"""
import json
import glob
import os
import collections
import math

def main():
    label_files = glob.glob("phase3/outputs/labels/*.jsonl")
    if not label_files:
        print("No labeled files in phase3/outputs/labels/")
        return
        
    out_dir = "phase3/outputs/metrics"
    os.makedirs(out_dir, exist_ok=True)
    
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
                stats[(model, temp, fact_id)][framing].append(label)

    if skipped:
        print(f"Warning: skipped {skipped} rows with invalid labels (ERROR/UNKNOWN)")
                
    results = []
    
    # Aggregate
    for (model, temp, fact_id), framings in stats.items():
        for f_mode, labels in framings.items():
            
            # Count label occurrences
            counts = collections.Counter(labels)
            total = sum(counts.values())
            
            entropy = 0.0
            for label, count in counts.items():
                p = count / total
                if p > 0:
                    entropy -= p * math.log2(p)
            
            results.append({
                "model": model,
                "temperature": temp,
                "fact_id": fact_id,
                "framing": f_mode,
                "n_samples": total,
                "entropy": entropy,
                "distribution": dict(counts)
            })
            
    out_path = os.path.join(out_dir, "entropy_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Entropy analysis computed across {len(results)} distinct prompt contexts.")
    
    print("\n--- Summary by Model, Temp ---")
    summary = collections.defaultdict(list)
    for r in results:
        key = (r["model"], r["temperature"])
        summary[key].append(r["entropy"])
        
    for k, v in sorted(summary.items()):
        avg_h = sum(v) / len(v)
        max_h = max(v)
        print(f"Model: {k[0]:30s} | Temp: {k[1]:.1f} | Avg Entropy: {avg_h:.3f} | Max Entropy: {max_h:.3f}")

if __name__ == "__main__":
    main()
