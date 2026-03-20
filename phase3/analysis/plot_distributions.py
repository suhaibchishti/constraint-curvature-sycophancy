#!/usr/bin/env python3
"""
Plot Distributions
Reads phase3/outputs/metrics/ and creates figures for KDG, Entropy, and categorical distribution.
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import collections
import numpy as np

def main():
    metrics_dir = "phase3/outputs/metrics"
    fig_dir = "phase3/outputs/figures"
    os.makedirs(fig_dir, exist_ok=True)

    # 1. Plot KDG
    try:
        with open(os.path.join(metrics_dir, "kdg_results.json")) as f:
            kdg_data = json.load(f)

        # Group by (model, framing) → list of KDG values
        summary_kdg = collections.defaultdict(list)
        for r in kdg_data:
            summary_kdg[(r["model"], r["framing"])].append(r["kdg"])

        models = sorted(set(r["model"] for r in kdg_data))
        short_names = [m.split("/")[-1] for m in models]
        framings = sorted(set(r["framing"] for r in kdg_data))

        plt.figure(figsize=(12, 6))
        width = 0.8 / len(framings)
        x = np.arange(len(models))

        for i, framing in enumerate(framings):
            avg_kdgs = []
            for m in models:
                vals = summary_kdg.get((m, framing), [0.0])
                avg_kdgs.append(sum(vals) / len(vals))
            plt.bar(x + (i - len(framings)/2) * width + width/2, avg_kdgs, width, label=framing)

        plt.xlabel("Model")
        plt.ylabel("KDG (Knowledge Deployment Gap)")
        plt.title("Knowledge Deployment Gap by Model and Framing")
        plt.xticks(x, short_names, rotation=45, ha="right")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(fig_dir, "kdg_by_model.png"), dpi=150)
        plt.close()
        print(f"Saved KDG plot to {fig_dir}/kdg_by_model.png")

    except FileNotFoundError:
        print("KDG results not found. Run compute_kdg.py first.")

    # 2. Plot Entropy by Model and Temperature
    try:
        with open(os.path.join(metrics_dir, "entropy_results.json")) as f:
            entropy_data = json.load(f)

        summary_ent = collections.defaultdict(list)
        for r in entropy_data:
            summary_ent[(r["model"], r["temperature"])].append(r["entropy"])

        models = sorted(set(r["model"] for r in entropy_data))
        short_names = [m.split("/")[-1] for m in models]
        temps = sorted(set(r["temperature"] for r in entropy_data))

        plt.figure(figsize=(12, 6))
        width = 0.8 / len(temps)
        x = np.arange(len(models))

        for i, t in enumerate(temps):
            avgs = []
            for m in models:
                vals = summary_ent.get((m, t), [0.0])
                avgs.append(sum(vals) / len(vals))
            plt.bar(x + (i - len(temps)/2) * width + width/2, avgs, width, label=f"T={t}")

        plt.xlabel("Model")
        plt.ylabel("Average Response Entropy")
        plt.title("Response Entropy by Model and Temperature")
        plt.xticks(x, short_names, rotation=45, ha="right")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(fig_dir, "entropy_by_model.png"), dpi=150)
        plt.close()
        print(f"Saved Entropy plot to {fig_dir}/entropy_by_model.png")

    except FileNotFoundError:
        print("Entropy results not found. Run compute_entropy.py first.")

if __name__ == "__main__":
    main()
