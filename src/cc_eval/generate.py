from typing import Any
import os, json
import numpy as np
from tqdm import tqdm

def set_seed(seed: int):
    import random
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except Exception:
        pass

def generate_outputs(tokenizer, model, prompts: list[dict[str, Any]], *,
                     max_new_tokens: int, temperature: float, top_p: float, seed: int, system_prompt: str = None):
    set_seed(seed)
    outputs = []
    for p in tqdm(prompts, desc="Generating"):
        text = p["prompt"]
        
        # Apply system prompt if provided (for chat models)
        if system_prompt:
            # Check if tokenizer has chat template
            if hasattr(tokenizer, 'chat_template') and tokenizer.chat_template is not None:
                try:
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ]
                    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                except (ValueError, AttributeError):
                    # Fallback for base models without chat template
                    text = f"{system_prompt}\n\nUser: {text}\nAssistant:"
            else:
                # Fallback: prepend system prompt for base models
                text = f"{system_prompt}\n\nUser: {text}\nAssistant:"
        
        inputs = tokenizer(text, return_tensors="pt", padding=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        with __import__("torch").no_grad():
            gen = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=(temperature > 0),
                temperature=temperature,
                top_p=top_p,
                pad_token_id=tokenizer.eos_token_id,
            )
        out = tokenizer.decode(gen[0], skip_special_tokens=True)
        completion = out[len(text):].strip() if out.startswith(text) else out.strip()
        outputs.append({**p, "completion": completion, "seed": seed})
    return outputs

def write_jsonl(path: str, rows: list[dict[str, Any]]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
