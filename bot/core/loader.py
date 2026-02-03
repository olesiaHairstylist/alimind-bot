# bot/core/loader.py

import json
from pathlib import Path
from bot.core.registry import registry

# корень проекта: .../alimind_bot
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "objects"

def preload_catalog() -> int:
    registry.clear()
    count = 0

    if not DATA_PATH.exists():
        return 0

    for file in DATA_PATH.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                for obj in data:
                    if isinstance(obj, dict):
                        obj_id = obj.get("id")
                        if obj_id:
                            registry[obj_id] = obj
                            count += 1

            elif isinstance(data, dict):
                obj_id = data.get("id")
                if obj_id:
                    registry[obj_id] = data
                    count += 1

        except Exception:
            continue

    return count
