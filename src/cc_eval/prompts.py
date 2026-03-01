import yaml
from dataclasses import dataclass
from typing import Any

@dataclass
class PromptItem:
    id: str
    category: str
    prompt: str
    expected: str

def load_yaml_items(path: str) -> list[PromptItem]:
    with open(path, "r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)
    items = []
    for it in data["items"]:
        items.append(PromptItem(
            id=str(it["id"]),
            category=str(it.get("category", "")),
            prompt=str(it["prompt"]),
            expected=str(it.get("expected", "")),
        ))
    return items
