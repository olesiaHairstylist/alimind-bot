# bot/core/text.py

from typing import Any

def to_text(v: Any) -> str:
    """
    Нормализует значение в текст.
    Поддерживает:
      - str
      - dict (например {"ru": "...", "en": "..."})
      - None
      - любые другие типы через str()
    """
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        parts = []
        for val in v.values():
            if isinstance(val, str):
                parts.append(val)
        return " ".join(parts)
    return str(v)
