# bot/handlers/favorites.py

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

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
from bot.handlers.recents import log_recent

router = Router()

PER_PAGE = 5

print("[FAVORITES] loaded from:", __file__)

# ====== FAVORITES STORAGE (in-memory) ======
# user_id -> list of object ids
_fav: Dict[int, List[str]] = {}


def is_favorite(user_id: int, obj_id: str) -> bool:
    oid = to_text(obj_id).strip()
    if not oid:
        return False
    return oid in _fav.get(user_id, [])


def add_favorite(user_id: int, obj_id: str) -> bool:
    oid = to_text(obj_id).strip()
    if not oid:
        return False
    lst = _fav.setdefault(user_id, [])
    if oid in lst:
        return False
    lst.append(oid)
    return True


def remove_favorite(user_id: int, obj_id: str) -> bool:
    oid = to_text(obj_id).strip()
    if not oid:
        return False
    lst = _fav.get(user_id, [])
    if oid not in lst:
        return False
    lst.remove(oid)
    return True


def get_favorites(user_id: int) -> List[str]:
    return list(_fav.get(user_id, []))


     # ====== TOGGLE KB FOR CARDS ======
def make_fav_toggle_kb(user_id: int, obj_id: str) -> InlineKeyboardMarkup:
    oid = to_text(obj_id).strip()
    obj = registry.get(oid) if oid else None

    b = InlineKeyboardBuilder()

    # 1) ACTIONS из JSON (ровно один раз)
    actions = []
    if obj:
        actions = obj.get("actions") or []

        # ✅ Авто-кнопка "Связаться", если requests включены, но actions не заданы
        if (not actions) and bool(obj.get("accept_requests")):
            oid2 = to_text(obj.get("id")).strip() or oid
            actions = [{"label": "📨 Связаться", "callback": f"preq:{oid2}"}]

        if isinstance(actions, list):
            for a in actions:
                label = to_text(a.get("label")).strip()
                cb = to_text(a.get("callback")).strip()
                if label and cb:
                    b.button(text=label, callback_data=cb)

    # если actions были — делаем их отдельными строками
    if actions:
        b.adjust(1)

    # 2) Избранное (как у тебя было)
    if oid and is_favorite(user_id, oid):
        b.button(text="⭐ Убрать", callback_data=f"fav:rm:{oid}")
    else:
        b.button(text="⭐ В избранное", callback_data=f"fav:add:{oid}")

    # 3) Открыть список избранного
    b.button(text="📌 Избранное", callback_data="fav:open")

    # низ — в 2 колонки
    b.adjust(1, 2) if actions else b.adjust(2)

    return b.as_markup()










# ====== FAVORITES LIST PAGING (stale guard) ======
@dataclass
class FavListCtx:
    ids: List[str]
    key: int
    msg_id: int


_fav_ctx: Dict[int, FavListCtx] = {}
_seq: Dict[int, int] = {}


def _next_key(user_id: int) -> int:
    _seq[user_id] = _seq.get(user_id, 0) + 1
    return _seq[user_id]


def _pages(total: int) -> int:
    return max(1, math.ceil(max(0, total) / PER_PAGE))


def _build_fav_page(ctx: FavListCtx, page: int) -> tuple[str, Optional[InlineKeyboardMarkup]]:
    ids = ctx.ids
    total = len(ids)
    pages = _pages(total)
    page = max(1, min(page, pages))

    if total == 0:
        text = (
            "⭐ Избранное\n"
            "Пока пусто.\n\n"
            "Откройте карточку и нажмите ⭐ В избранное."
        )
        return text, None

    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    chunk = ids[start:end]

    lines = [
        "⭐ Избранное",
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

    # кнопки ID текущей страницы
    for oid in chunk:
        b.button(text=oid, callback_data=f"fav:openid:{ctx.key}:{oid}")
    if chunk:
        b.adjust(2)

    nav: list[InlineKeyboardButton] = []
    if pages > 1:
        if page > 1:
            nav.append(InlineKeyboardButton(text="◀️", callback_data=f"fav:page:{ctx.key}:{page-1}"))
        if page < pages:
            nav.append(InlineKeyboardButton(text="▶️", callback_data=f"fav:page:{ctx.key}:{page+1}"))
    if nav:
        b.row(*nav)

    return text, b.as_markup()


async def _refresh_fav_list_if_open(bot, chat_id: int, user_id: int) -> None:
    ctx = _fav_ctx.get(user_id)
    if not ctx:
        return
    # обновляем ids, но key/msg_id сохраняем
    ids = [oid for oid in get_favorites(user_id) if oid in registry]
    ctx.ids = ids

    text, kb = _build_fav_page(ctx, page=1)
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=ctx.msg_id,
            text=text,
            reply_markup=kb,
            parse_mode=None,
        )
    except Exception:
        # если сообщение нельзя редактировать — молча игнорим
        return


# ====== COMMANDS / CALLBACKS ======
@router.message(Command("fav"))
async def cmd_fav(message: Message) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id

    ids = [oid for oid in get_favorites(user_id) if oid in registry]
    key = _next_key(user_id)

    temp = FavListCtx(ids=ids, key=key, msg_id=0)
    text, kb = _build_fav_page(temp, page=1)

    sent = await message.answer(text, reply_markup=kb, parse_mode=None)
    _fav_ctx[user_id] = FavListCtx(ids=ids, key=key, msg_id=sent.message_id)


@router.callback_query(F.data == "fav:open")
async def cb_open_fav(callback: CallbackQuery) -> None:
    # быстрый доступ к /fav с карточки
    if not callback.from_user:
        return
    user_id = callback.from_user.id
    msg = callback.message
    if not msg:
        await callback.answer()
        return

    ids = [oid for oid in get_favorites(user_id) if oid in registry]
    key = _next_key(user_id)

    temp = FavListCtx(ids=ids, key=key, msg_id=0)
    text, kb = _build_fav_page(temp, page=1)

    sent = await msg.answer(text, reply_markup=kb, parse_mode=None)
    _fav_ctx[user_id] = FavListCtx(ids=ids, key=key, msg_id=sent.message_id)

    await callback.answer()


@router.callback_query(F.data.startswith("fav:add:"))
async def cb_fav_add(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        await callback.answer()
        return
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    oid = (callback.data or "").split("fav:add:", 1)[1].strip()
    if not oid:
        await callback.answer("Некорректный ID", show_alert=False)
        return

    changed = add_favorite(user_id, oid)
    # обновим клавиатуру карточки
    try:
        await callback.message.edit_reply_markup(reply_markup=make_fav_toggle_kb(user_id, oid))
    except Exception:
        pass

    # обновим /fav если открыт
    await _refresh_fav_list_if_open(callback.bot, chat_id, user_id)

    await callback.answer("Добавлено" if changed else "Уже в избранном", show_alert=False)


@router.callback_query(F.data.startswith("fav:rm:"))
async def cb_fav_rm(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        await callback.answer()
        return
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    oid = (callback.data or "").split("fav:rm:", 1)[1].strip()
    if not oid:
        await callback.answer("Некорректный ID", show_alert=False)
        return

    changed = remove_favorite(user_id, oid)
    try:
        await callback.message.edit_reply_markup(reply_markup=make_fav_toggle_kb(user_id, oid))
    except Exception:
        pass

    await _refresh_fav_list_if_open(callback.bot, chat_id, user_id)

    await callback.answer("Убрано" if changed else "Не было в избранном", show_alert=False)


@router.callback_query(F.data.startswith("fav:page:"))
async def cb_fav_page(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        await callback.answer()
        return
    user_id = callback.from_user.id
    ctx = _fav_ctx.get(user_id)
    if not ctx:
        await callback.answer("Список устарел. Откройте /fav заново", show_alert=False)
        return

    try:
        rest = (callback.data or "").split("fav:page:", 1)[1]
        key_str, page_str = rest.split(":", 1)
        key = int(key_str)
        page = int(page_str)
    except Exception:
        await callback.answer("Некорректная страница", show_alert=False)
        return

    if key != ctx.key or callback.message.message_id != ctx.msg_id:
        await callback.answer("Список устарел. Откройте /fav заново", show_alert=False)
        return

    text, kb = _build_fav_page(ctx, page=page)
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=None)
    except Exception:
        await callback.answer("Сообщение устарело. Откройте /fav заново", show_alert=False)
        return

    await callback.answer()


@router.callback_query(F.data.startswith("fav:openid:"))
async def cb_fav_open_id(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        await callback.answer()
        return
    user_id = callback.from_user.id
    ctx = _fav_ctx.get(user_id)
    if not ctx:
        await callback.answer("Список устарел. Откройте /fav заново", show_alert=False)
        return

    try:
        rest = (callback.data or "").split("fav:openid:", 1)[1]
        key_str, oid = rest.split(":", 1)
        key = int(key_str)
        oid = oid.strip()
    except Exception:
        await callback.answer("Некорректная кнопка", show_alert=False)
        return

    if key != ctx.key or callback.message.message_id != ctx.msg_id:
        await callback.answer("Список устарел. Откройте /fav заново", show_alert=False)
        return

    obj = registry.get(oid)
    if not obj:
        await callback.answer("Объект не найден", show_alert=False)
        return
    log_recent(user_id, oid)

    text = format_object_card_html(obj)
    await callback.message.answer(text, reply_markup=make_fav_toggle_kb(user_id, oid), parse_mode="HTML")
    await callback.answer()
