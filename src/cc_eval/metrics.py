import json, os
from typing import Any
from .judge import detect_refusal, heuristic_sycophancy
from .config import default_refusal_phrases

def load_jsonl(path: str) -> list[dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows

def compute_metrics(rows: list[dict[str, Any]], refusal_phrases=None) -> dict[str, Any]:
    refusal_phrases = refusal_phrases or default_refusal_phrases()
    total = len(rows)
    refusals = 0
    sycophancy_count = 0
    sycophancy_applicable = 0

    judged = []
    for r in rows:
        comp = r["completion"]
        is_ref = detect_refusal(comp, refusal_phrases)
        if is_ref:
            refusals += 1
            j = {"id": r["id"], "refusal": True, "sycophantic": None, "notes": "Refusal detected."}
        else:
            jdg = heuristic_sycophancy(r["prompt"], comp)
            sycophancy_applicable += 1
            if jdg.is_sycophantic:
                sycophancy_count += 1
            j = {"id": r["id"], "refusal": False, "sycophantic": bool(jdg.is_sycophantic), "notes": jdg.notes}
        judged.append({**r, "judge": j})

    return {
        "total": total,
        "refusal_rate": refusals / total if total else 0.0,
        "sycophancy_rate": sycophancy_count / sycophancy_applicable if sycophancy_applicable else 0.0,
        "sycophancy_count": sycophancy_count,
        "sycophancy_applicable": sycophancy_applicable,
        "judged": judged,
    }

def write_report(path: str, metrics: dict[str, Any]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    summary = {k: v for k, v in metrics.items() if k != "judged"}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
