from __future__ import annotations

import math
from typing import Dict, List, Optional
from dataclasses import dataclass

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.registry import registry
from bot.core.text import to_text
from bot.core.formatter import format_object_card_html

router = Router()

PER_PAGE = 5
MAX_RECENT = 20

# =========
# STORAGE
# =========
# user_id -> list[obj_id]
_recent: Dict[int, List[str]] = {}


def log_recent(user_id: int, obj_id: str) -> None:
    oid = to_text(obj_id).strip()
    if not oid:
        return

    lst = _recent.setdefault(user_id, [])
    if oid in lst:
        lst.remove(oid)
    lst.insert(0, oid)

    del lst[MAX_RECENT:]


def get_recent(user_id: int) -> List[str]:
    return list(_recent.get(user_id, []))


# =========
# CONTEXT (stale-guard)
# =========
@dataclass
class RecentCtx:
    ids: List[str]
    key: int
    msg_id: int


_recent_ctx: Dict[int, RecentCtx] = {}
_seq: Dict[int, int] = {}


def _next_key(user_id: int) -> int:
    _seq[user_id] = _seq.get(user_id, 0) + 1
    return _seq[user_id]


def _pages(total: int) -> int:
    return max(1, math.ceil(max(0, total) / PER_PAGE))


# =========
# UI HELPERS
# =========
def _back_btn() -> InlineKeyboardButton:
    return InlineKeyboardButton(text="⬅️ К последним", callback_data="recent:back")


def _fav_kb(user_id: int, obj_id: str) -> InlineKeyboardMarkup:
    # локальный импорт — разрывает циклический импорт
    from bot.handlers.favorites import make_fav_toggle_kb
    return make_fav_toggle_kb(user_id, obj_id)


def _build_recent_page(
    ctx: RecentCtx, page: int
) -> tuple[str, Optional[InlineKeyboardMarkup]]:
    ids = ctx.ids
    total = len(ids)
    pages = _pages(total)
    page = max(1, min(page, pages))

    if total == 0:
        text = (
            "🕘 Последние открытые карточки\n"
            "Пока пусто.\n\n"
            "Откройте любую карточку — она появится здесь."
        )
        return text, None

    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    chunk = ids[start:end]

    lines = [
        "🕘 Последние открытые карточки",
        f"Всего: {total}",
        f"Страница: {page}/{pages}",
        "",
    ]

    for i, oid in enumerate(chunk, start=start + 1):
        obj = registry.get(oid)
        name = to_text(obj.get("name")).strip() if obj else ""
        name = name or "Без названия"
        lines.append(f"{i}. {oid} — {name}")

    text = "\n".join(lines)

    b = InlineKeyboardBuilder()

    for oid in chunk:
        b.button(text=oid, callback_data=f"recent:open:{ctx.key}:{oid}")

    if chunk:
        b.adjust(2)

    nav: list[InlineKeyboardButton] = []
    if pages > 1:
        if page > 1:
            nav.append(
                InlineKeyboardButton(
                    text="◀️", callback_data=f"recent:page:{ctx.key}:{page-1}"
                )
            )
        if page < pages:
            nav.append(
                InlineKeyboardButton(
                    text="▶️", callback_data=f"recent:page:{ctx.key}:{page+1}"
                )
            )
    if nav:
        b.row(*nav)

    return text, b.as_markup()


# =========
# /recent
# =========
@router.message(Command("recent"))
async def cmd_recent(message: Message) -> None:
    if not message.from_user:
        return

    user_id = message.from_user.id
    ids = [oid for oid in get_recent(user_id) if oid in registry]
    key = _next_key(user_id)

    temp = RecentCtx(ids=ids, key=key, msg_id=0)
    text, kb = _build_recent_page(temp, page=1)

    sent = await message.answer(text, reply_markup=kb, parse_mode=None)
    _recent_ctx[user_id] = RecentCtx(ids=ids, key=key, msg_id=sent.message_id)




# =========
# PAGING
# =========
@router.callback_query(F.data.startswith("recent:page:"))
async def cb_recent_page(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        await callback.answer()
        return

    user_id = callback.from_user.id
    ctx = _recent_ctx.get(user_id)
    if not ctx:
        await callback.answer("Список устарел", show_alert=False)
        return

    try:
        _, _, key_str, page_str = callback.data.split(":", 3)
        key = int(key_str)
        page = int(page_str)
    except Exception:
        await callback.answer("Некорректная кнопка", show_alert=False)
        return

    if key != ctx.key or callback.message.message_id != ctx.msg_id:
        await callback.answer("Список устарел", show_alert=False)
        return

    text, kb = _build_recent_page(ctx, page=page)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode=None)
    await callback.answer()


# =========
# OPEN CARD
# =========
@router.callback_query(F.data.startswith("recent:open:"))
async def cb_recent_open(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        await callback.answer()
        return

    user_id = callback.from_user.id

    try:
        _, _, key_str, oid = callback.data.split(":", 3)
        key = int(key_str)
        oid = oid.strip()
    except Exception:
        await callback.answer("Некорректная кнопка", show_alert=False)
        return

    ctx = _recent_ctx.get(user_id)
    if not ctx or key != ctx.key or callback.message.message_id != ctx.msg_id:
        await callback.answer("Список устарел", show_alert=False)
        return

    obj = registry.get(oid)
    if not obj:
        await callback.answer("Объект не найден", show_alert=False)
        return

    text = format_object_card_html(obj)
    obj = registry.get(oid)
    if not obj:
        await callback.answer("Объект не найден", show_alert=False)
        return

    log_recent(user_id, oid)  # ✅ relog чтобы карточка стала №1 в /recent
    text = format_object_card_html(obj)

    b = InlineKeyboardBuilder()
    fav_kb = _fav_kb(user_id, oid)
    for row in fav_kb.inline_keyboard:
        b.row(*row)
    b.row(_back_btn())

    await callback.message.answer(
        text,
        reply_markup=b.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


# =========
# BACK TO LIST (MODULE_22)
# =========
@router.callback_query(F.data == "recent:back")
async def cb_recent_back(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        await callback.answer()
        return

    user_id = callback.from_user.id

    # если контекста нет — кнопка считается устаревшей
    if user_id not in _recent_ctx:
        await callback.answer("Список устарел. Откройте /recent", show_alert=False)
        return

    ids = [oid for oid in get_recent(user_id) if oid in registry]
    key = _next_key(user_id)

    temp = RecentCtx(ids=ids, key=key, msg_id=0)
    text, kb = _build_recent_page(temp, page=1)

    sent = await callback.message.answer(text, reply_markup=kb, parse_mode=None)
    _recent_ctx[user_id] = RecentCtx(ids=ids, key=key, msg_id=sent.message_id)

    await callback.answer()
