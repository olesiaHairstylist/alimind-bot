import json
from pathlib import Path
from datetime import datetime, timezone

STATE_DIR = Path("data/state")
ADMIN_CHAT_PATH = STATE_DIR / "admin_chat.json"


def _ensure_state_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def set_admin_chat_id(chat_id: int) -> None:
    _ensure_state_dir()
    data = {
        "admin_chat_id": chat_id,
        "connected_at": datetime.now(timezone.utc).isoformat()
    }
    ADMIN_CHAT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_admin_chat_id() -> int | None:
    if not ADMIN_CHAT_PATH.exists():
        return None
    try:
        data = json.loads(ADMIN_CHAT_PATH.read_text(encoding="utf-8"))
        return int(data.get("admin_chat_id"))
    except Exception:
        return None
