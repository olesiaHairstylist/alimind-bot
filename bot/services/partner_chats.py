import json
from pathlib import Path
from typing import Dict, Optional

# корень проекта: .../alimind_bot
PROJECT_ROOT = Path(__file__).resolve().parents[2]
STORE_PATH = PROJECT_ROOT / "data" / "partner_chats.json"


def _ensure_store() -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text("{}", encoding="utf-8")
        return
    # если файл пустой/битый — не падаем, но и не затираем молча
    txt = STORE_PATH.read_text(encoding="utf-8").strip()
    if not txt:
        STORE_PATH.write_text("{}", encoding="utf-8")


def load_partner_chats() -> Dict[str, int]:
    _ensure_store()
    try:
        data = json.loads(STORE_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        out: Dict[str, int] = {}
        for k, v in data.items():
            if isinstance(k, str) and isinstance(v, int):
                out[k] = v
        return out
    except Exception:
        return {}


def save_partner_chats(data: Dict[str, int]) -> bool:
    _ensure_store()
    try:
        # атомарная запись
        tmp = STORE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(STORE_PATH)
        return True
    except Exception:
        return False


def get_partner_chat_id(partner_id: str) -> Optional[int]:
    pid = (partner_id or "").strip()
    if not pid:
        return None
    data = load_partner_chats()
    return data.get(pid)


def set_partner_chat_id(partner_id: str, chat_id: int) -> bool:
    pid = (partner_id or "").strip()
    if not pid or not isinstance(chat_id, int):
        return False
    data = load_partner_chats()
    data[pid] = chat_id
    return save_partner_chats(data)
