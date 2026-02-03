# bot/core/search.py

from bot.core.registry import registry
from bot.core.text import to_text

def search_by_name_or_description(query: str) -> list[dict]:
    q = to_text(query).lower().strip()
    if len(q) < 2:
        return []

    results: list[dict] = []
    seen: set[str] = set()

    for obj in registry.values():
        name = to_text(obj.get("name")).lower()
        desc = to_text(obj.get("description")).lower()

        if q in name or q in desc:
            obj_id = obj.get("id")
            if obj_id and obj_id not in seen:
                results.append(obj)
                seen.add(obj_id)

    return results
