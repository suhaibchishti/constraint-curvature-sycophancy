#!/usr/bin/env python3
"""
Plot Distributions
Reads phase3/outputs/metrics/ and creates figures for KDG, Entropy, and categorical distribution.
"""
import json
import os
import matplotlib.pyplot as plt
import collections
import numpy as np

def main():
    metrics_dir = "phase3/outputs/metrics"
    fig_dir = "phase3/outputs/figures"
    os.makedirs(fig_dir, exist_ok=True)
    
    # 1. Plot KDG
    try:
        with open(os.path.join(metrics_dir, "kdg_results.json"), "r") as f:
            kdg_data = json.load(f)
            
        summary_kdg = collections.defaultdict(list)
        for r in kdg_data:
            key = (r["model"], r["framing"])
            summary_kdg[key].append(r["kdg"])
            
        models = sorted(list(set([r["model"].split('/')[-1] for r in kdg_data])))
        framings = sorted(list(set([r["framing"] for r in kdg_data])))
        
        plt.figure(figsize=(10, 6))
        
        width = 0.2
        x = np.arange(len(models))
        
        for i, framing in enumerate(framings):
            avg_kdgs = []
            for m in models:
                raw_m = next(r["model"] for r in kdg_data if m in r["model"])
                key = (raw_m, framing)
                
                if key in summary_kdg:
                    avg_kdgs.append(sum(summary_kdg[key]) / len(summary_kdg[key]))
                else:
                    avg_kdgs.append(0.0)
                    
            plt.bar(x + (i - len(framings)/2) * width + width/2, avg_kdgs, width, label=framing)
            
        plt.xlabel('Model')
        plt.ylabel('KDG (Knowledge Deployment Gap)')
        plt.title('Knowledge Deployment Gap by Model and Framing')
        plt.xticks(x, models, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(fig_dir, "kdg_by_model.png"))
        print(f"Saved KDG plot to {fig_dir}/kdg_by_model.png")
        
    except FileNotFoundError:
        print("KDG results not found. Run compute_kdg.py first.")
        
    # 2. Plot Entropy
    try:
        with open(os.path.join(metrics_dir, "entropy_results.json"), "r") as f:
            entropy_data = json.load(f)
            
        summary_ent = collections.defaultdict(list)
        for r in entropy_data:
            key = r["model"]
            summary_ent[key].append(r["entropy"])
            
        models = sorted(list(set([r["model"].split('/')[-1] for r in entropy_data])))
        
        plt.figure(figsize=(8, 6))
        
        avg_ents = []
        for m in models:
            raw_m = next(r["model"] for r in entropy_data if m in r["model"])
            v = summary_ent[raw_m]
            avg_ents.append(sum(v) / len(v))
            
        plt.bar(models, avg_ents, color='skyblue')
        plt.xlabel('Model')
        plt.ylabel('Average Response Entropy')
        plt.title('Response Stability (Entropy) by Model')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(fig_dir, "entropy_by_model.png"))
        print(f"Saved Entropy plot to {fig_dir}/entropy_by_model.png")
        
    except FileNotFoundError:
        print("Entropy results not found. Run compute_entropy.py first.")

if __name__ == "__main__":
    main()
