# bot/ai/snippet.py

from bot.core.search import search_by_name_or_description
from bot.core.text import to_text

WHITELIST_FIELDS = {
    "id",
    "title",
    "address",
    "work_hours",
    "phone",
    "whatsapp",
    "maps",
    "links",
}

def _trim_object(obj: dict) -> dict:
    return {k: obj.get(k) for k in WHITELIST_FIELDS if k in obj}

def build_snippet(query: str, max_chars: int) -> dict:
    hits = search_by_name_or_description(query)

    objects = []
    total_len = 0

    for obj in hits:
        trimmed = _trim_object(obj)
        chunk_len = len(to_text(trimmed))

        if total_len + chunk_len > max_chars:
            break

        objects.append(trimmed)
        total_len += chunk_len

    return {"objects": objects}
