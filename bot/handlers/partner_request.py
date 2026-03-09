# bot/handlers/partner_request.py
# PARTNER_REQUEST_V2 (SAFE) + REQUEST_AUDIT_V1 (JSONL)
#
# Универсальный партнёрский запрос:
# - Кнопка на карточке партнёра: "📨 Оставить запрос" (callback: preq:<CARD_ID>)
# - FSM: вопрос -> контакт -> подтверждение
# - Доставка: по chat_id из data/state/partner_links.json (partner_links.get_chat_id)
# - Если партнёр не подключён: честно сообщаем пользователю
# - Ответы без Markdown (parse_mode=None)
#
# Аудит (append-only):
# - data/state/request_audit.jsonl
# - события: start / not_connected / cancel / confirm_ok / confirm_fail

from __future__ import annotations

import html
import re
import uuid
import os

from aiogram import Router, F
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.registry import registry
from bot.core.text import to_text
from bot.storage.partner_links import get_chat_id
from bot.storage.request_audit import append_event
from bot.storage.admin_chat import get_admin_chat_id


router = Router()

CB_PREFIX = "preq"

# Старт должен ловить только preq:<CARD_ID>, но НЕ confirm/cancel
CB_START_PATTERN = re.compile(rf"^{CB_PREFIX}:(?!confirm$|cancel$)(.+)$")


class PartnerRequestFSM(StatesGroup):
    waiting_question = State()
    waiting_contact = State()
    waiting_confirm = State()


def _kb_confirm() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Отправить", callback_data=f"{CB_PREFIX}:confirm")
    b.button(text="✖️ Отмена", callback_data=f"{CB_PREFIX}:cancel")
    b.adjust(2)
    return b.as_markup()


def _kb_cancel() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✖️ Отмена", callback_data=f"{CB_PREFIX}:cancel")

    return b.as_markup()


def _is_partner_obj(obj: dict) -> bool:
    status = to_text(obj.get("status")).strip().lower()
    if status == "partner":
        return True
    return bool(obj.get("is_partner"))


def _safe_one_line(s: str, limit: int = 500) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    if len(s) > limit:
        s = s[: limit - 1] + "…"
    return s


def _looks_like_contact(text: str) -> bool:
    """
    Простой эвристический фильтр контакта:
    - @username
    - номер (есть цифры и длина >= 7)
    - ссылка t.me/...
    """
    t = (text or "").strip()
    if not t:
        return False
    if t.startswith("@") and len(t) >= 4:
        return True
    if "t.me/" in t.lower():
        return True
    digits = re.sub(r"\D+", "", t)
    return len(digits) >= 7


def _build_partner_message(
    *,
    card_id: str,
    partner_name: str,
    category: str,
    user_name: str,
    user_id: int,
    question: str,
    contact: str,
    user_username: str | None = None,
) -> str:
    partner_name = html.escape(partner_name or "—")
    card_id = html.escape(card_id or "—")
    question = html.escape(question or "—")
    contact = html.escape(contact or "—")

    # username может отсутствовать — это нормально
    uname = (user_username or "").strip()
    uname_part = f" @{html.escape(uname)}" if uname else ""

    # кликабельный клиент по user_id (работает всегда)
    safe_user_name = html.escape(user_name or "Клиент")
    client_link = f'<a href="tg://user?id={user_id}">{safe_user_name}</a>'

    return (
        "📩 <b>Новая заявка на запись</b>\n\n"
        f"👤 <b>Партнёр:</b> {partner_name}\n"
        f"🆔 <b>CARD_ID:</b> {card_id}\n"
        f"👤 <b>Клиент:</b> {client_link}{uname_part} (id:{user_id})\n\n"
        f"✨ <b>Запрос:</b> {question}\n"
        f"📞 <b>Контакт:</b> {contact}\n\n"
        "Напишите клиенту и подтвердите время 💬\n"
        "📍 Источник: AliMind Directory (партнёрский запрос)"
    )

async def _notify_admin(bot, *, status: str, request_id: str, card_id: str, partner_chat_id: int | None, user_id: int) -> None:
    admin_chat_id = get_admin_chat_id()
    if not admin_chat_id:
        return

    # НИКАКОГО текста заявки и контакта
    text = (
        f"{'✅' if status == 'ok' else '❌'} PartnerRequest {status}\n"
        f"request_id: {request_id}\n"
        f"card_id: {card_id}\n"
        f"partner_chat_id: {partner_chat_id if partner_chat_id is not None else '—'}\n"
        f"user_id: {user_id}"
    )

    try:
        await bot.send_message(chat_id=admin_chat_id, text=text, parse_mode=None)
    except Exception:
        # админ-уведомления не должны ломать основной поток
        pass

@router.callback_query(F.data.startswith(f"{CB_PREFIX}:"), F.data.regexp(CB_START_PATTERN))
async def cb_start_partner_request(query: CallbackQuery, state: FSMContext) -> None:
    if not query.from_user or not query.message:
        await query.answer()
        return

    m = CB_START_PATTERN.match(query.data or "")
    if not m:
        await query.answer()
        return

    card_id = (m.group(1) or "").strip()
    obj = registry.get(card_id)

    if not isinstance(obj, dict):
        await query.answer("Карточка не найдена", show_alert=False)
        return

    if not _is_partner_obj(obj):
        await query.answer("Запрос доступен только для партнёров", show_alert=False)
        return

    partner_chat_id = get_chat_id(card_id)
    if not partner_chat_id:
        append_event(
            event="not_connected",
            request_id=uuid.uuid4().hex[:12],
            card_id=card_id,
            user_id=query.from_user.id,
            user_name=query.from_user.full_name or "—",
        )
        await query.answer()
        await query.message.answer(
            "⚠️ Партнёр пока не подключил приём заявок через систему.\n"
            "Попробуйте позже.",
            parse_mode=None,
        )
        return

    partner_name = to_text(obj.get("name")).strip() or card_id
    request_id = uuid.uuid4().hex[:12]

    await state.clear()
    await state.set_state(PartnerRequestFSM.waiting_question)
    await state.update_data(card_id=card_id, partner_name=partner_name, request_id=request_id)

    append_event(
        event="start",
        request_id=request_id,
        card_id=card_id,
        user_id=query.from_user.id,
        user_name=query.from_user.full_name or "—",
        partner_chat_id=partner_chat_id,
    )

    await query.answer()
    await query.message.answer(
        f"📨 Запрос для партнёра: {partner_name}\n\n"
        "Коротко опишите ваш запрос.",
        reply_markup=_kb_cancel(),
        parse_mode=None,
    )


@router.message(StateFilter(PartnerRequestFSM.waiting_question), F.text)
async def fsm_got_question(message: Message, state: FSMContext) -> None:
    text = _safe_one_line(message.text or "", limit=500)

    if len(text) < 2:
        await message.answer("Напишите пару слов: что именно нужно?", parse_mode=None)
        return

    await state.update_data(question=text)
    await state.set_state(PartnerRequestFSM.waiting_contact)

    await message.answer(
        "Оставьте контакт для связи (телефон или Telegram).\n"
        "Пример: +90 5xx xxx xx xx или @username",
        reply_markup=_kb_cancel(),
        parse_mode=None,
    )


@router.message(StateFilter(PartnerRequestFSM.waiting_contact), F.text)
async def fsm_got_contact(message: Message, state: FSMContext) -> None:
    contact = _safe_one_line(message.text or "", limit=120)

    if not _looks_like_contact(contact):
        await message.answer(
            "Похоже, это не контакт.\n"
            "Укажите телефон (цифры) или Telegram (@username).",
            parse_mode=None,
        )
        return

    await state.update_data(contact=contact)
    await state.set_state(PartnerRequestFSM.waiting_confirm)

    data = await state.get_data()
    partner_name = to_text(data.get("partner_name")).strip() or "партнёр"
    question = to_text(data.get("question")).strip()

    await message.answer(
        "Проверьте и подтвердите отправку:\n\n"
        f"Партнёр: {partner_name}\n"
        f"Запрос: {question}\n"
        f"Контакт: {contact}",
        reply_markup=_kb_confirm(),
        parse_mode=None,
    )


@router.callback_query(StateFilter(PartnerRequestFSM), F.data == f"{CB_PREFIX}:cancel")
async def cb_cancel(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    append_event(
        event="cancel",
        request_id=to_text(data.get("request_id")).strip() or "—",
        card_id=to_text(data.get("card_id")).strip() or "—",
        user_id=query.from_user.id if query.from_user else 0,
        user_name=query.from_user.full_name if query.from_user else "—",
    )

    await state.clear()
    if query.message:
        await query.message.answer("✖️ Отменено.", parse_mode=None)
    await query.answer()


@router.callback_query(StateFilter(PartnerRequestFSM.waiting_confirm), F.data == f"{CB_PREFIX}:confirm")
async def cb_confirm(query: CallbackQuery, state: FSMContext) -> None:
    if not query.from_user or not query.message:
        await query.answer()
        return

    data = await state.get_data()
    request_id = to_text(data.get("request_id")).strip() or "—"

    card_id = to_text(data.get("card_id")).strip()
    partner_name = to_text(data.get("partner_name")).strip() or card_id
    question = to_text(data.get("question")).strip()
    contact = to_text(data.get("contact")).strip()

    if not card_id or not question or not contact:
        append_event(
            event="confirm_fail",
            request_id=request_id,
            card_id=card_id or "—",
            user_id=query.from_user.id,
            user_name=query.from_user.full_name or "—",
            question=question,
            contact=contact,
            error="stale_data",
        )
        await state.clear()
        await query.message.answer("⚠️ Данные запроса устарели. Попробуйте снова.", parse_mode=None)
        await query.answer()
        return

    obj = registry.get(card_id)
    if not isinstance(obj, dict):
        append_event(
            event="confirm_fail",
            request_id=request_id,
            card_id=card_id,
            user_id=query.from_user.id,
            user_name=query.from_user.full_name or "—",
            question=question,
            contact=contact,
            error="card_not_found",
        )
        await state.clear()
        await query.message.answer("⚠️ Карточка не найдена. Попробуйте снова.", parse_mode=None)
        await query.answer()
        return

    partner_chat_id = get_chat_id(card_id)
    if not partner_chat_id:
        append_event(
            event="not_connected",
            request_id=request_id,
            card_id=card_id,
            user_id=query.from_user.id,
            user_name=query.from_user.full_name or "—",
            question=question,
            contact=contact,
        )
        await state.clear()
        await query.message.answer(
            "⚠️ Партнёр пока не подключил приём заявок через систему.\n"
            "Попробуйте позже.",
            parse_mode=None,
        )
        await query.answer()
        return

    category = to_text(obj.get("category")).strip() or "—"
    user_name = (query.from_user.full_name or "").strip() or "—"
    user_id = query.from_user.id
    user_username = query.from_user.username  # без @

    text_to_partner = _build_partner_message(
        card_id=card_id,
        partner_name=partner_name,
        category=category,
        user_name=user_name,
        user_id=user_id,
        question=question,
        contact=contact,
        user_username=user_username,
    )

    try:
        await query.bot.send_message(
            chat_id=partner_chat_id,
            text=text_to_partner,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except TelegramForbiddenError as e:
        append_event(
            event="confirm_fail",
            request_id=request_id,
            card_id=card_id,
            user_id=user_id,
            user_name=user_name,
            partner_chat_id=partner_chat_id,
            question=question,
            contact=contact,
            error=repr(e),
        )
        await state.clear()
        await query.message.answer("❌ Партнёр недоступен для сообщений.", parse_mode=None)
        await query.answer()
        return
    except TelegramBadRequest as e:
        append_event(
            event="confirm_fail",
            request_id=request_id,
            card_id=card_id,
            user_id=user_id,
            user_name=user_name,
            partner_chat_id=partner_chat_id,
            question=question,
            contact=contact,
            error=repr(e),
        )
        await state.clear()
        await query.message.answer("❌ Не удалось доставить запрос партнёру.", parse_mode=None)
        await query.answer()
        return
    except Exception as e:
        append_event(
            event="confirm_fail",
            request_id=request_id,
            card_id=card_id,
            user_id=user_id,
            user_name=user_name,
            partner_chat_id=partner_chat_id,
            question=question,
            contact=contact,
            error=repr(e),
        )
        await state.clear()
        await query.message.answer("❌ Не удалось доставить запрос партнёру.", parse_mode=None)
        await query.answer()
        return

    append_event(
        event="confirm_ok",
        request_id=request_id,
        card_id=card_id,
        user_id=user_id,
        user_name=user_name,
        partner_chat_id=partner_chat_id,
        question=question,
        contact=contact,
    )

    await state.clear()
    await query.message.answer(
        "✅ Запрос отправлен.\n"
        "Ожидайте ответа — партнёр свяжется с вами по оставленному контакту.",
        parse_mode=None,
    )
    await query.answer()
