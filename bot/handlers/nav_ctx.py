# bot/handlers/nav_ctx.py
# MODULE_22: CARD_NAVIGATION_SAFE_V1
# Контекст навигации (БЕЗ aiogram)

from typing import Dict, Optional, List


# user_id -> navigation context
# {
#   "source": "recent" | "fav" | "search" | "category",
#   "ids": ["BEAUTY_01", "GOV_01", ...],
#   "index": 0,
#   "msg_id": 123
# }
_nav_ctx: Dict[int, dict] = {}


def set_nav_ctx(
    user_id: int,
    source: str,
    ids: List[str],
    index: int,
    msg_id: int,
) -> None:
    _nav_ctx[user_id] = {
        "source": source,
        "ids": ids,
        "index": index,
        "msg_id": msg_id,
    }


def get_nav_ctx(user_id: int) -> Optional[dict]:
    return _nav_ctx.get(user_id)


def update_nav_index(user_id: int, index: int) -> None:
    if user_id in _nav_ctx:
        _nav_ctx[user_id]["index"] = index


def clear_nav_ctx(user_id: int) -> None:
    _nav_ctx.pop(user_id, None)
