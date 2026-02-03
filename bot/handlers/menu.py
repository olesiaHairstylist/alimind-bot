# bot/handlers/menu.py
from typing import Dict, Tuple, Optional
import math
import re
from aiogram import Router, F
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
from bot.handlers.favorites import make_fav_toggle_kb
from bot.handlers.recents import log_recent
from bot.handlers.card_sender import send_object_card

router = Router()

PER_PAGE = 5
CB_PREFIX = "catpage"
PHARM_TODAY_CB = "pharm_today"
OUTAGES_TODAY_CB = "outages_today"
EMERGENCY_CONTACTS_CB = "emergency_contacts"

BTN_TO_CATEGORY = {


    "🏛 Госучреждения": "gov",
    "🚨 Экстренные службы": "emergency",
    "🗣 Услуги переводчика": "trn",
    "📄 Официальный разбор требований для ВНЖ": "migration",
    "💇 Салон красоты": "beauty",
    "🍽 Кафе и рестораны": "cafe",
    "💊 Аптеки": "pharmacy",
    "🚕 Такси": "taxi",
    "⚽ Спорт": "sport",
    "🎭 Досуг": "fun",
    "🚌 Транспорт": "transport",
 }

BTN_TEXTS = tuple(BTN_TO_CATEGORY.keys())

ID_PATTERN = re.compile(r"^\s*(?:ID|Id|id)\s*:\s*(.+?)\s*$")
BARE_ID_PATTERN = re.compile(r'^\s*"?([A-Z]{2,10}_[A-Z0-9]{2,40})"?\s*$')

# catpage:<category>:<key>:<page>
CB_PATTERN = re.compile(rf"^{CB_PREFIX}:([a-z_]+):(\d+):(\d+)$")
# old: catpage:<category>:<page>
CB_PATTERN_OLD = re.compile(rf"^{CB_PREFIX}:([a-z_]+):(\d+)$")

# oc:c:<key>:<id>
OC_CAT_PATTERN = re.compile(r"^oc:c:(\d+):([A-Z]{2,10}_[A-Z0-9]{2,40})$")
# oc:open:<id>
OC_OPEN_PATTERN = re.compile(r"^oc:open:([A-Z]{2,10}_[A-Z0-9]{2,40})$")


# (user_id, category_code) -> (key, message_id)
_cat_ctx: Dict[Tuple[int, str], Tuple[int, int]] = {}
_seq: Dict[int, int] = {}
@router.callback_query(F.data.regexp(OC_OPEN_PATTERN))
async def cb_open_card_direct(query: CallbackQuery) -> None:
    if not query.from_user or not query.message:
        await query.answer()
        return

    m = OC_OPEN_PATTERN.match(query.data or "")
    if not m:
        await query.answer()
        return

    obj_id = m.group(1).strip()
    obj = registry.get(obj_id)
    if not obj:
        await query.answer("Объект не найден", show_alert=False)
        return








    user_id = query.from_user.id
    text = format_object_card_html(obj)
    photo_rel = obj.get("photo")

    log_recent(user_id, obj_id)

    await send_object_card(
        query.message,
        text_html=text,
        photo_rel=photo_rel,
        reply_markup=make_fav_toggle_kb(user_id, obj_id),
    )

    await query.answer()


def _next_key(user_id: int) -> int:
    _seq[user_id] = _seq.get(user_id, 0) + 1
    return _seq[user_id]


def _set_cat_ctx(user_id: int, category_code: str, key: int, msg_id: int) -> None:
    _cat_ctx[(user_id, category_code)] = (key, msg_id)


def _get_cat_ctx(user_id: int, category_code: str) -> Optional[Tuple[int, int]]:
    return _cat_ctx.get((user_id, category_code))


def _objects_by_category(category_code: str) -> list[dict]:
    partners: list[dict] = []
    others: list[dict] = []

    for obj in registry.values():
        cat = to_text(obj.get("category")).strip().lower()
        if cat != category_code:
            continue

        status = to_text(obj.get("status")).strip().lower()
        if status == "partner":
            partners.append(obj)
        else:
            others.append(obj)

    partners.sort(key=lambda o: to_text(o.get("name")).strip().lower())
    others.sort(key=lambda o: to_text(o.get("name")).strip().lower())

    return partners + others
def _pharmacy_events_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💊 Дежурные аптеки", callback_data=PHARM_TODAY_CB)
    b.adjust(1)
    return b.as_markup()

def _gov_events_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🔌 Плановые отключения воды и электричества", callback_data=OUTAGES_TODAY_CB)
    b.adjust(1)
    return b.as_markup()


def _emergency_events_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="☎️ Экстренные контакты", callback_data=EMERGENCY_CONTACTS_CB)
    b.adjust(1)
    return b.as_markup()

def _render_category_page(category_code: str, page: int, key: int) -> tuple[str, Optional[InlineKeyboardMarkup]]:
    objs = _objects_by_category(category_code)
    total = len(objs)

    if total == 0:
        text = f"📦 Категория: {category_code}\nПока пусто."
        if category_code == "pharmacy":
            return (text, _pharmacy_events_kb())
        if category_code == "gov":
            return (text, _gov_events_kb())
        if category_code == "emergency":
            return (text, _emergency_events_kb())
        return (text, None)

    pages = max(1, math.ceil(total / PER_PAGE))
    page = max(0, min(page, pages - 1))

    start = page * PER_PAGE
    end = start + PER_PAGE
    chunk = objs[start:end]

    lines = [
        f"📦 Категория: {category_code}",
        f"Найдено объектов: {total}",
        f"Страница: {page + 1}/{pages}",
        "",
    ]

    page_ids: list[str] = []
    for i, obj in enumerate(chunk, start=start + 1):
        obj_id = to_text(obj.get("id")).strip()
        name = to_text(obj.get("name")).strip() or "Без названия"
        lines.append(f"{i}. {obj_id} — {name}")
        if obj_id:
            page_ids.append(obj_id)

    lines.append("")
    lines.append(" Это список то что вас интересует. Нажмите👇 , чтобы открыть карточку")

    b = InlineKeyboardBuilder()



    # ✅ GOV: событийная кнопка всегда первой строкой

    if category_code == "gov":
        b.button(text="🔌 Плановые отключения воды и электричества", callback_data=OUTAGES_TODAY_CB)
        b.adjust(1)

    # ✅ PHARMACY: событийная кнопка всегда первой строкой (если уже делали)
    if category_code == "pharmacy":
        b.button(text="💊 Дежурные аптеки", callback_data=PHARM_TODAY_CB)
        b.adjust(1)

    # Кнопки ID текущей страницы
    for obj_id in page_ids:
        obj = registry.get(obj_id)
        title = to_text(obj.get("name")).strip() if obj else obj_id
        b.button(text=title, callback_data=f"oc:c:{key}:{obj_id}")

    if page_ids:
        b.adjust(2)

    # Пагинация
    nav: list[InlineKeyboardButton] = []
    if pages > 1:
        if page > 0:
            nav.append(InlineKeyboardButton(text="◀️", callback_data=f"{CB_PREFIX}:{category_code}:{key}:{page - 1}"))
        if page < pages - 1:
            nav.append(InlineKeyboardButton(text="▶️", callback_data=f"{CB_PREFIX}:{category_code}:{key}:{page + 1}"))
    if nav:
        b.row(*nav)

    kb = b.as_markup() if (page_ids or nav or category_code in ("emergency", "gov", "pharmacy")) else None

    return ("\n".join(lines), kb)
# Старый текстовый вход оставляем как запасной (не ломаем логику)
@router.message(F.text.in_(BTN_TEXTS))
async def category_button_handler(message: Message) -> None:
    text = (message.text or "").strip()
    code = BTN_TO_CATEGORY.get(text)
    if not code or not message.from_user:
        return

    user_id = message.from_user.id
    key = _next_key(user_id)

    page_text, kb = _render_category_page(code, page=0, key=key)
    sent = await message.answer(page_text, reply_markup=kb, parse_mode=None)

    _set_cat_ctx(user_id, code, key=key, msg_id=sent.message_id)


# Новый вход из красивого inline-меню (/start)
@router.callback_query(F.data.startswith("catopen:"))
async def open_category_from_menu(query: CallbackQuery) -> None:
    if not query.from_user or not query.message:
        await query.answer()
        return

    category_code = query.data.split(":", 1)[1]
    user_id = query.from_user.id

    key = _next_key(user_id)

    page_text, kb = _render_category_page(category_code, page=0, key=key)
    sent = await query.message.answer(page_text, reply_markup=kb, parse_mode=None)

    _set_cat_ctx(user_id, category_code, key=key, msg_id=sent.message_id)

    await query.answer()


@router.callback_query(F.data.regexp(CB_PATTERN_OLD))
async def category_page_callback_legacy(query: CallbackQuery) -> None:
    await query.answer("Список устарел. Откройте категорию заново", show_alert=False)


@router.callback_query(F.data.regexp(CB_PATTERN))
async def category_page_callback(query: CallbackQuery) -> None:
    if not query.from_user or not query.message:
        await query.answer()
        return

    m = CB_PATTERN.match(query.data or "")
    if not m:
        await query.answer()
        return

    code = m.group(1)
    key = int(m.group(2))
    page = int(m.group(3))

    user_id = query.from_user.id
    ctx = _get_cat_ctx(user_id, code)
    if not ctx:
        await query.answer("Список устарел. Откройте категорию заново", show_alert=False)
        return

    expected_key, expected_msg_id = ctx
    if key != expected_key or query.message.message_id != expected_msg_id:
        await query.answer("Список устарел. Откройте категорию заново", show_alert=False)
        return

    page_text, kb = _render_category_page(code, page=page, key=key)
    await query.message.edit_text(page_text, reply_markup=kb, parse_mode=None)
    await query.answer()




@router.callback_query(F.data.regexp(OC_CAT_PATTERN))
async def cb_open_card_from_category(query: CallbackQuery) -> None:
    if not query.from_user or not query.message:
        await query.answer()
        return

    m = OC_CAT_PATTERN.match(query.data or "")
    if not m:
        await query.answer()
        return

    key = int(m.group(1))
    obj_id = m.group(2).strip()

    user_id = query.from_user.id
    msg_id = query.message.message_id

    ok = False
    for (uid, _code), (k, mid) in _cat_ctx.items():
        if uid == user_id and k == key and mid == msg_id:
            ok = True
            break

    if not ok:
        await query.answer("Список устарел. Откройте категорию заново", show_alert=False)
        return

    obj = registry.get(obj_id)
    if not obj:
        await query.answer("Объект не найден", show_alert=False)
        return

    text = format_object_card_html(obj)

    log_recent(user_id, obj_id)
    photo_rel = obj.get("photo")

    await send_object_card(
        query.message,
        text_html=text,
        photo_rel=photo_rel,
        reply_markup=make_fav_toggle_kb(user_id, obj_id),
    )

    await query.answer()


@router.message(F.text.regexp(ID_PATTERN))
async def open_by_id_handler(message: Message) -> None:
    m = ID_PATTERN.match(message.text or "")
    if not m or not message.from_user:
        return

    obj_id = m.group(1).strip()
    obj = registry.get(obj_id)

    if not obj:
        await message.answer(f"❌ Объект не найден: {obj_id}", parse_mode=None)
        return

    user_id = message.from_user.id
    text = format_object_card_html(obj)
    photo_rel = obj.get("photo")

    log_recent(user_id, obj_id)

    await send_object_card(
        message,
        text_html=text,
        photo_rel=photo_rel,
        reply_markup=make_fav_toggle_kb(user_id, obj_id),
    )



@router.message(F.text.regexp(BARE_ID_PATTERN))
async def open_by_bare_id_handler(message: Message) -> None:
    m = BARE_ID_PATTERN.match(message.text or "")
    if not m or not message.from_user:
        return

    obj_id = m.group(1).strip()
    obj = registry.get(obj_id)

    if not obj:
        await message.answer(f"❌ Объект не найден: {obj_id}", parse_mode=None)
        return

    user_id = message.from_user.id
    text = format_object_card_html(obj)
    photo_rel = obj.get("photo")

    log_recent(user_id, obj_id)

    await send_object_card(
        message,
        text_html=text,
        photo_rel=photo_rel,
        reply_markup=make_fav_toggle_kb(user_id, obj_id),
    )




