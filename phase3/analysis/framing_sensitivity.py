#!/usr/bin/env python3
"""
Framing Sensitivity
Analyzes and compares the impact of the 4 framing classes (Neutral, Leading, Authority, Social)
on affirmation and refusal probabilities.
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import collections

def main():
    label_files = [f for f in os.listdir("phase3/outputs/labels/") if f.endswith(".jsonl")]
    if not label_files:
        print("No label files found.")
        return
        
    stats = collections.defaultdict(lambda: collections.defaultdict(int))
    total_samples = collections.defaultdict(lambda: collections.defaultdict(int))
    
    for lf in label_files:
        with open(os.path.join("phase3/outputs/labels", lf), "r") as f:
            for line in f:
                item = json.loads(line.strip())
                label = item.get("gpt4o_label", "UNKNOWN")
                if label not in ["S1", "S2", "C", "H", "R"]:
                    continue
                model = item["model"].split('/')[-1]
                framing = item["framing"]
                stats[model][framing, label] += 1
                total_samples[model][framing] += 1
                
    results_s1 = collections.defaultdict(dict)
    results_r = collections.defaultdict(dict)
    
    for m in stats:
        for f_mode in ["neutral", "leading", "authority", "opinion", "original"]:
            results_s1[m][f_mode] = stats[m][f_mode, "S1"] / max(total_samples[m][f_mode], 1)
            results_r[m][f_mode] = stats[m][f_mode, "R"] / max(total_samples[m][f_mode], 1)
            
    # Print summary
    print("\n--- Sycophancy (S1) by Framing Class ---")
    for m in results_s1:
        s = " | ".join(f"{f}: {results_s1[m][f]:.2f}" for f in results_s1[m])
        print(f"{m:30s} -> {s}")
        
    print("\n--- Refusal (R) by Framing Class ---")
    for m in results_r:
        s = " | ".join(f"{f}: {results_r[m][f]:.2f}" for f in results_r[m])
        print(f"{m:30s} -> {s}")

if __name__ == "__main__":
    main()
