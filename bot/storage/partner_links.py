# bot/storage/partner_links.py
# PARTNER_LINKS_STORE_V1
#
# Хранилище привязок партнёров: card_id -> chat_id (+ username, connected_at)
# - НЕ трогаем core
# - Файл состояния лежит в data/state/partner_links.json (вне data/objects)
# - Пишем атомарно (через tmp + replace), чтобы не убить файл при падении

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


# Europe/Istanbul (+03:00) — фиксируем как в проекте
_TZ = timezone(timedelta(hours=3))


def _now_iso() -> str:
    return datetime.now(_TZ).isoformat(timespec="seconds")


# Корень проекта: .../alimind_bot
PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = PROJECT_ROOT / "data" / "state"
LINKS_PATH = STATE_DIR / "partner_links.json"


@dataclass
class PartnerLink:
    chat_id: int
    username: Optional[str] = None
    connected_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"chat_id": int(self.chat_id)}
        if self.username:
            d["username"] = str(self.username)
        if self.connected_at:
            d["connected_at"] = str(self.connected_at)
        return d


def _ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_links() -> Dict[str, Dict[str, Any]]:
    """
    Возвращает dict вида:
      { "BEAUTY_OLESYA": {"chat_id": 123, "username": "...", "connected_at": "..."} }
    """
    try:
        if not LINKS_PATH.exists():
            return {}
        raw = LINKS_PATH.read_text(encoding="utf-8").strip()
        if not raw:
            return {}
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}
        # простая валидация значений
        out: Dict[str, Dict[str, Any]] = {}
        for k, v in data.items():
            if not isinstance(k, str):
                continue
            if not isinstance(v, dict):
                continue
            chat_id = v.get("chat_id")
            if not isinstance(chat_id, int):
                # иногда могут сохранить строкой — попробуем привести
                try:
                    chat_id = int(chat_id)
                except Exception:
                    continue
            item: Dict[str, Any] = {"chat_id": chat_id}
            username = v.get("username")
            if isinstance(username, str) and username.strip():
                item["username"] = username.strip()
            connected_at = v.get("connected_at")
            if isinstance(connected_at, str) and connected_at.strip():
                item["connected_at"] = connected_at.strip()
            out[k.strip()] = item
        return out
    except Exception:
        # не падаем — просто считаем, что привязок нет
        return {}


def save_links(data: Dict[str, Dict[str, Any]]) -> None:
    """
    Атомарная запись:
    - пишем в tmp
    - replace поверх основной
    """
    _ensure_state_dir()

    if not isinstance(data, dict):
        raise ValueError("save_links ожидает dict")

    tmp_path = LINKS_PATH.with_suffix(".tmp")

    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    tmp_path.write_text(payload, encoding="utf-8")
    tmp_path.replace(LINKS_PATH)


def set_link(card_id: str, chat_id: int, username: Optional[str] = None) -> None:
    cid = (card_id or "").strip()
    if not cid:
        raise ValueError("card_id пустой")
    if not isinstance(chat_id, int) or chat_id == 0:
        raise ValueError("chat_id некорректный")

    links = load_links()
    links[cid] = PartnerLink(
        chat_id=chat_id,
        username=(username or "").strip() or None,
        connected_at=_now_iso(),
    ).to_dict()
    save_links(links)


def get_chat_id(card_id: str) -> Optional[int]:
    cid = (card_id or "").strip()
    if not cid:
        return None
    links = load_links()
    item = links.get(cid)
    if not isinstance(item, dict):
        return None
    chat_id = item.get("chat_id")
    if isinstance(chat_id, int) and chat_id != 0:
        return chat_id
    try:
        val = int(chat_id)
        return val if val !=0 else None
    except Exception:
        return None


def get_link(card_id: str) -> Optional[Dict[str, Any]]:
    """
    Полезно для отладки: вернуть весь объект привязки.
    """
    cid = (card_id or "").strip()
    if not cid:
        return None
    links = load_links()
    item = links.get(cid)
    return item if isinstance(item, dict) else None
{
  "BEAUTY_OLESYA": {
    "chat_id": -1002611625063
  }
}




