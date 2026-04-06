import json
q = [json.loads(l) for l in open("phase4/outputs/Qwen2.5-72B-Instruct_labeled.jsonl")]
for f in ["original", "neutral", "opinion", "authority", "leading"]:
    print(f"\n--- {f} ---")
    for r in q:
        if r["framing"] == f:
            print(r["prompt"])
            break
