import json
from typing import List, Dict

def load_recipes(path: str) -> List[Dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_recipes(recipes, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
