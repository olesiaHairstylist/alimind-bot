from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from aiogram import Router, F
from aiogram.filters import Command, CommandObject, BaseFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.search import search_by_name_or_description
from bot.core.text import to_text
from bot.core.registry import registry
from bot.core.formatter import format_object_card_html
from bot.handlers.favorites import make_fav_toggle_kb
from bot.handlers.recents import log_recent

router = Router()

PAGE_SIZE = 5

# ловим ID в начале строки (в т.ч. "17. GOV_ADLIYE — ...")
LIST_LINE_ID_PATTERN = re.compile(r"^\s*(?:\d+\.\s*)?([A-Z]{2,10}_[A-Z0-9]{2,40})\b")

# NEW: open-card кнопки из поиска:
# oc:s:<key>:<id>
OC_SEARCH_PATTERN = re.compile(r"^oc:s:(\d+):([A-Z]{2,10}_[A-Z0-9]{2,40})$")


@dataclass
class SearchCtx:
    query: str
    ids: List[str]
    key: int          # nonce для защиты от "старых" кнопок
    msg_id: int       # message_id сообщения с результатами (которое листаем)


_search_ctx: Dict[int, SearchCtx] = {}
_pending: Dict[int, bool] = {}
_pending_key: Dict[int, int] = {}
_pending_msg_id: Dict[int, int] = {}
_seq: Dict[int, int] = {}


def _next_key(user_id: int) -> int:
    _seq[user_id] = _seq.get(user_id, 0) + 1
    return _seq[user_id]


def _clear_search(user_id: int) -> None:
    _search_ctx.pop(user_id, None)
    _pending.pop(user_id, None)
    _pending_key.pop(user_id, None)
    _pending_msg_id.pop(user_id, None)


def _total_pages(n: int, page_size: int = PAGE_SIZE) -> int:
    if n <= 0:
        return 1
    return max(1, math.ceil(n / page_size))


def _build_search_page(ctx: SearchCtx, page: int) -> tuple[str, Optional[InlineKeyboardMarkup]]:
    ids = ctx.ids
    n = len(ids)
    pages = _total_pages(n, PAGE_SIZE)

    page = max(1, min(page, pages))

    if n == 0:
        text = (
            f"Поиск: {ctx.query}\n"
            f"Найдено: 0\n\n"
            "Ничего не найдено."
        )
        return text, None

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    chunk = ids[start:end]

    # подтягиваем name по query (core не трогаем)
    id_to_name: Dict[str, str] = {}
    for obj in search_by_name_or_description(ctx.query):
        oid = to_text(obj.get("id")).strip()
        if oid:
            id_to_name[oid] = to_text(obj.get("name")).strip()

    lines = [f"{obj_id} — {id_to_name.get(obj_id, '')}".rstrip() for obj_id in chunk]

    text = (
        f"Поиск: {ctx.query}\n"
        f"Найдено: {n}\n\n"
        + "\n".join(lines)
        + f"\n\nСтраница {page}/{pages}"
    )

    b = InlineKeyboardBuilder()

    # NEW: кнопки ID текущей страницы
    for obj_id in chunk:
        b.button(text=obj_id, callback_data=f"oc:s:{ctx.key}:{obj_id}")
    if chunk:
        b.adjust(2)

    # paging row
    nav: list[InlineKeyboardButton] = []
    if pages > 1:
        if page > 1:
            nav.append(InlineKeyboardButton(text="◀️", callback_data=f"searchpage:{ctx.key}:{page-1}"))
        if page < pages:
            nav.append(InlineKeyboardButton(text="▶️", callback_data=f"searchpage:{ctx.key}:{page+1}"))
    if nav:
        b.row(*nav)

    markup = b.as_markup() if (chunk or nav) else None
    return text, markup


class SearchPendingFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        return bool(_pending.get(message.from_user.id, False))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message) -> None:
    if not message.from_user:
        return
    _clear_search(message.from_user.id)
    await message.answer("Ок, отменено. Можете снова: /search", parse_mode=None)


@router.message(Command("search"))
async def cmd_search(message: Message, command: CommandObject) -> None:
    if not message.from_user:
        return

    user_id = message.from_user.id

    raw_args = (command.args or "").strip()
    if raw_args:
        q = to_text(raw_args).strip()
        if len(q) < 2:
            await message.answer("Запрос слишком короткий. Введите хотя бы 2 символа.", parse_mode=None)
            return

        key = _next_key(user_id)
        results = search_by_name_or_description(q)
        ids = [to_text(o.get("id")).strip() for o in results if to_text(o.get("id")).strip()]

        temp_ctx = SearchCtx(query=q, ids=ids, key=key, msg_id=0)
        text, markup = _build_search_page(temp_ctx, page=1)
        sent = await message.answer(text, reply_markup=markup, parse_mode=None)

        _search_ctx[user_id] = SearchCtx(query=q, ids=ids, key=key, msg_id=sent.message_id)
        return

    _pending[user_id] = True
    key = _next_key(user_id)
    _pending_key[user_id] = key

    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data=f"searchcancel:{key}")

    sent = await message.answer(
        "Введите запрос для поиска.\n/cancel — отмена",
        reply_markup=kb.as_markup(),
        parse_mode=None
    )
    _pending_msg_id[user_id] = sent.message_id


@router.message(SearchPendingFilter(), F.text)
async def search_query_input(message: Message) -> None:
    if not message.from_user:
        return

    user_id = message.from_user.id
    _pending[user_id] = False

    # при pending: если похоже на ID/строку списка — открываем карточку
    m_id = LIST_LINE_ID_PATTERN.match(message.text or "")
    if m_id:
        obj_id = m_id.group(1).strip()
        obj = registry.get(obj_id)

        _pending_key.pop(user_id, None)
        _pending_msg_id.pop(user_id, None)

        if not obj:
            await message.answer(f"❌ Объект не найден: {obj_id}", parse_mode=None)
            return

        # MODULE_20: покрытие /recent
        log_recent(user_id, obj_id)

        text = format_object_card_html(obj)
        await message.answer(text, parse_mode="HTML")
        return

    q = to_text(message.text).strip()
    if len(q) < 2:
        await message.answer("Запрос слишком короткий. Введите хотя бы 2 символа.", parse_mode=None)
        _pending[user_id] = True
        return

    key = _pending_key.get(user_id) or _next_key(user_id)

    results = search_by_name_or_description(q)
    ids = [to_text(o.get("id")).strip() for o in results if to_text(o.get("id")).strip()]

    temp_ctx = SearchCtx(query=q, ids=ids, key=key, msg_id=0)
    text, markup = _build_search_page(temp_ctx, page=1)
    sent = await message.answer(text, reply_markup=markup, parse_mode=None)

    _search_ctx[user_id] = SearchCtx(query=q, ids=ids, key=key, msg_id=sent.message_id)

    _pending_key.pop(user_id, None)
    _pending_msg_id.pop(user_id, None)


@router.callback_query(F.data.startswith("searchcancel:"))
async def cb_search_cancel(callback: CallbackQuery) -> None:
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    data = callback.data or ""

    try:
        key = int(data.split("searchcancel:", 1)[1])
    except Exception:
        await callback.answer("Некорректная кнопка", show_alert=False)
        return

    expected_key = _pending_key.get(user_id)
    expected_msg_id = _pending_msg_id.get(user_id)
    current_msg_id = callback.message.message_id if callback.message else None

    if not expected_key or expected_key != key or (expected_msg_id and current_msg_id != expected_msg_id):
        await callback.answer("Устарело. Запустите /search заново", show_alert=False)
        return

    _clear_search(user_id)

    text = "Ок, отменено. Можете снова: /search"
    msg = callback.message
    if msg:
        try:
            await msg.edit_text(text, reply_markup=None, parse_mode=None)
        except Exception:
            await msg.answer(text, parse_mode=None)

    await callback.answer()


@router.callback_query(F.data.regexp(OC_SEARCH_PATTERN))
async def cb_open_card_from_search(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        await callback.answer()
        return

    m = OC_SEARCH_PATTERN.match(callback.data or "")
    if not m:
        await callback.answer()
        return

    key = int(m.group(1))
    obj_id = m.group(2).strip()

    user_id = callback.from_user.id
    ctx = _search_ctx.get(user_id)

    if not ctx or key != ctx.key or callback.message.message_id != ctx.msg_id:
        await callback.answer("Устарело. Запустите /search заново", show_alert=False)
        return

    obj = registry.get(obj_id)
    if not obj:
        await callback.answer("Объект не найден", show_alert=False)
        return

    # MODULE_20: покрытие /recent
    log_recent(user_id, obj_id)

    text = format_object_card_html(obj)
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("searchpage:"))
async def cb_search_page(callback: CallbackQuery) -> None:
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    ctx = _search_ctx.get(user_id)
    if not ctx:
        await callback.answer("Поиск устарел. Запустите /search", show_alert=False)
        return

    data = callback.data or ""
    try:
        rest = data.split("searchpage:", 1)[1]
        key_str, page_str = rest.split(":", 1)
        key = int(key_str)
        page = int(page_str)
    except Exception:
        await callback.answer("Некорректная страница", show_alert=False)
        return

    msg = callback.message
    if key != ctx.key or not msg or msg.message_id != ctx.msg_id:
        await callback.answer("Устарело. Запустите /search заново", show_alert=False)
        return

    text, markup = _build_search_page(ctx, page=page)

    try:
        await msg.edit_text(text, reply_markup=markup, parse_mode=None)
    except Exception:
        await callback.answer("Сообщение устарело. Запустите /search заново", show_alert=False)
        return

    await callback.answer()
