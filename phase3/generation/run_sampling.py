import json
import os
import copy
from src.cc_eval.generate import generate_outputs
from src.cc_eval.load_model import load_model

def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line.strip()))
    return rows

def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def main():
    repo_dir = "/opt/ml/processing/input/repo"
    out_dir = "/opt/ml/processing/output"
    
    # If testing locally, fallback paths
    if not os.path.exists(repo_dir):
        repo_dir = "."
        out_dir = "./phase3/outputs/generations"
        
    prompt_file = os.path.join(repo_dir, "phase3", "data", "prompt_variants.jsonl")
    
    print(f"Loading prompts from {prompt_file}...")
    base_prompts = load_jsonl(prompt_file)
    print(f"Loaded {len(base_prompts)} prompts.")
    
    model_name = os.environ.get("MODEL_PATH", "meta-llama/Meta-Llama-3-8B-Instruct")
    print(f"Loading model: {model_name}")
    
    use_quant = os.environ.get("USE_QUANTIZATION", "true").lower() == "true"
    
    model, tokenizer = load_model(model_name, use_quant=use_quant)
    
    temperatures = [0.0, 0.3, 0.7]
    
    # Flatten the jobs
    jobs = []
    
    for temp in temperatures:
        samples_per_prompt = 1 if temp == 0.0 else 10
        for sample_idx in range(samples_per_prompt):
            for p in base_prompts:
                p_copy = copy.deepcopy(p)
                p_copy["temperature"] = temp
                p_copy["sample_idx"] = sample_idx
                jobs.append(p_copy)
                
    print(f"Generated {len(jobs)} evaluation jobs.")
    
    grouped_by_temp = {t: [] for t in temperatures}
    for j in jobs:
        grouped_by_temp[j["temperature"]].append(j)

    results = []
    
    for temp in temperatures:
        print(f"Generating for temperature={temp}")
        group = grouped_by_temp[temp]
        out_temp = generate_outputs(
            tokenizer=tokenizer,
            model=model,
            prompts=group,
            max_new_tokens=150,
            temperature=temp,
            top_p=0.9,
            seed=42 + int(temp*100),
            system_prompt="You are a helpful assistant."
        )
        for r in out_temp:
            r["model"] = model_name
        results.extend(out_temp)
        
    out_file = os.path.join(out_dir, f"{model_name.split('/')[-1]}_distributions.jsonl")
    print(f"Saving {len(results)} outputs to {out_file}...")
    write_jsonl(out_file, results)
    print("Done.")

if __name__ == "__main__":
    main()
