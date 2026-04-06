import json
import numpy as np
import glob
import os
from collections import defaultdict

def load_data(file_pattern):
    data = defaultdict(list) # fact_id -> list of records
    for filepath in glob.glob(file_pattern, recursive=True):
        print(f"Loading {filepath}...")
        model_name = os.path.basename(filepath).replace("_labeled.jsonl", "")
        with open(filepath, 'r') as f:
            for line in f:
                if not line.strip(): continue
                record = json.loads(line)
                record['model'] = model_name
                fact_id = record['fact_id']
                data[fact_id].append(record)
    return data

def bootstrap_cluster(data, iterations=10000):
    fact_ids = list(data.keys())
    n_facts = len(fact_ids)
    
    # Pre-aggregate data by fact to speed up bootstrapping
    # struct: model -> framing -> fact_id -> { CuH: count, S1: count, R: count, total: count }
    agg = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'CuH': 0, 'S1': 0, 'R': 0, 'total': 0})))
    
    for fact_id, records in data.items():
        for r in records:
            model = r['model']
            framing = r['framing']
            label = r['gpt4o_label']
            
            agg[model][framing][fact_id]['total'] += 1
            if label in ('C', 'H'):
                agg[model][framing][fact_id]['CuH'] += 1
            if label == 'S1':
                agg[model][framing][fact_id]['S1'] += 1
            if label == 'R':
                agg[model][framing][fact_id]['R'] += 1

    results = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    print(f"Running {iterations} cluster bootstrap iterations...")
    np.random.seed(42)
    
    for i in range(iterations):
        # Sample fact_ids with replacement
        sampled_facts = np.random.choice(fact_ids, size=n_facts, replace=True)
        
        for model in agg.keys():
            # Calculate neutral rates for this bootstrap sample
            neutral_cuh = sum(agg[model]['neutral'][fid]['CuH'] for fid in sampled_facts)
            neutral_s1  = sum(agg[model]['neutral'][fid]['S1'] for fid in sampled_facts)
            neutral_r   = sum(agg[model]['neutral'][fid]['R'] for fid in sampled_facts)
            neutral_tot = sum(agg[model]['neutral'][fid]['total'] for fid in sampled_facts)
            
            if neutral_tot == 0: continue
            
            p_neutral_cuh = neutral_cuh / neutral_tot
            p_neutral_s1  = neutral_s1 / neutral_tot
            p_neutral_r   = neutral_r / neutral_tot
            
            for framing in agg[model].keys():
                if framing == 'neutral': continue
                
                f_cuh = sum(agg[model][framing][fid]['CuH'] for fid in sampled_facts)
                f_s1  = sum(agg[model][framing][fid]['S1'] for fid in sampled_facts)
                f_r   = sum(agg[model][framing][fid]['R'] for fid in sampled_facts)
                f_tot = sum(agg[model][framing][fid]['total'] for fid in sampled_facts)
                
                if f_tot == 0: continue
                
                p_f_cuh = f_cuh / f_tot
                p_f_s1  = f_s1 / f_tot
                p_f_r   = f_r / f_tot
                
                kdg = p_neutral_cuh - p_f_cuh
                kdg_s1 = p_f_s1 - p_neutral_s1
                kdg_r = p_f_r - p_neutral_r
                
                results[model][framing]['KDG'].append(kdg)
                results[model][framing]['KDG_S1'].append(kdg_s1)
                results[model][framing]['KDG_R'].append(kdg_r)
                
    # Summarize results
    summary = []
    for model in sorted(results.keys()):
        for framing in sorted(results[model].keys()):
            for metric in ['KDG', 'KDG_S1', 'KDG_R']:
                arr = np.array(results[model][framing][metric])
                mean = np.mean(arr)
                lower = np.percentile(arr, 2.5)
                upper = np.percentile(arr, 97.5)
                summary.append((model, framing, metric, mean, lower, upper))
                
    return summary

if __name__ == "__main__":
    # Load from phase2 and phase4
    data = load_data("phase*/*/*_labeled.jsonl")
    summary = bootstrap_cluster(data, iterations=10000)
    
    print("\n" + "="*80)
    print(f"{'Model':<30} | {'Framing':<12} | {'Metric':<8} | {'Mean':>7} | {'95% CI':>15}")
    print("="*80)
    for model, framing, metric, mean, lower, upper in summary:
        print(f"{model:<30} | {framing:<12} | {metric:<8} | {mean:+.3f} | [{lower:+.3f}, {upper:+.3f}]")
