import argparse, os, json
from .config import default_refusal_phrases
from .prompts import load_yaml_items
from .load_model import load_hf_model
from .generate import generate_outputs, write_jsonl
from .metrics import compute_metrics, write_report
from .gate import gate, GateThresholds

def run_eval(model_name: str, model_path: str, eval_path: str, out_prefix: str,
             max_new_tokens: int, temperature: float, top_p: float, seed: int, use_quantization: bool):
    items = load_yaml_items(eval_path)
    prompts = [{"id": it.id, "category": it.category, "expected": it.expected, "prompt": it.prompt} for it in items]
    tok, mdl = load_hf_model(model_path, use_quantization=use_quantization)
    rows = generate_outputs(tok, mdl, prompts,
                            max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p, seed=seed)
    out_jsonl = f"{out_prefix}.{model_name}.seed{seed}.jsonl"
    write_jsonl(out_jsonl, rows)
    m = compute_metrics(rows, refusal_phrases=default_refusal_phrases())
    write_report(f"{out_prefix}.{model_name}.seed{seed}.metrics.json", m)
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-a", required=True, help="HF repo id or local path")
    ap.add_argument("--model-b", required=True, help="HF repo id or local path")
    ap.add_argument("--outdir", default="artifacts")
    ap.add_argument("--syc-set", default="evals/sycophancy_set.yaml")
    ap.add_argument("--border-set", default="evals/borderline_safety_set.yaml")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--temp", type=float, default=0.2)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--quantize", action="store_true", help="Use 4-bit quantization")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    prefix_syc = os.path.join(args.outdir, "sycophancy")
    prefix_bor = os.path.join(args.outdir, "borderline")

    mA_syc = run_eval("A", args.model_a, args.syc_set, prefix_syc, args.max_new, args.temp, args.top_p, args.seed, args.quantize)
    mB_syc = run_eval("B", args.model_b, args.syc_set, prefix_syc, args.max_new, args.temp, args.top_p, args.seed, args.quantize)

    mA_bor = run_eval("A", args.model_a, args.border_set, prefix_bor, args.max_new, args.temp, args.top_p, args.seed, args.quantize)
    mB_bor = run_eval("B", args.model_b, args.border_set, prefix_bor, args.max_new, args.temp, args.top_p, args.seed, args.quantize)

    gate_input_A = {"sycophancy_rate": mA_syc["sycophancy_rate"], "refusal_rate": mA_bor["refusal_rate"]}
    gate_input_B = {"sycophancy_rate": mB_syc["sycophancy_rate"], "refusal_rate": mB_bor["refusal_rate"]}

    ok, msgs = gate(gate_input_A, gate_input_B, GateThresholds())
    summary = {
        "model_a": gate_input_A,
        "model_b": gate_input_B,
        "gate_ok": ok,
        "messages": msgs,
    }
    with open(os.path.join(args.outdir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n".join(msgs))
    if not ok:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
