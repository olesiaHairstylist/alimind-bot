from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

_TZ = timezone(timedelta(hours=3))  # Europe/Istanbul (+03:00)
DEFAULT_PATH = Path("data/state/request_audit.jsonl")


def _now_iso() -> str:
    return datetime.now(_TZ).isoformat(timespec="seconds")


def _safe_trim(s: Optional[str], limit: int) -> str:
    s = (s or "").strip()
    if len(s) > limit:
        return s[: limit - 1] + "…"
    return s


def append_event(
    *,
    event: str,
    request_id: str,
    card_id: str,
    user_id: int,
    user_name: str,
    partner_chat_id: Optional[int] = None,
    question: Optional[str] = None,
    contact: Optional[str] = None,
    error: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    path: Path = DEFAULT_PATH,
) -> None:
    """
    Append-only audit log. Никогда не падаем наружу: логирование не должно ломать UX.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        rec: Dict[str, Any] = {
            "ts": _now_iso(),
            "event": event,
            "request_id": request_id,
            "card_id": card_id,
            "user_id": user_id,
            "user_name": _safe_trim(user_name, 80),
            "partner_chat_id": partner_chat_id,
            "question": _safe_trim(question, 200),
            "contact": _safe_trim(contact, 120),
            "error": _safe_trim(error, 300),
        }
        if extra:
            rec["extra"] = extra

        # JSONL: одна запись = одна строка
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        # сознательно глотаем — аудит не должен ломать бот
        return
