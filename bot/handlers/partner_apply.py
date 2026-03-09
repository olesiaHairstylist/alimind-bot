import html
import os

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from bot.handlers.start import _send_start
from bot.states.partner_apply import PartnerApplyFSM
from aiogram.exceptions import TelegramBadRequest
load_dotenv()

router = Router()

ADMIN_CHAT_ID = (os.getenv("ADMIN_CHAT_ID") or "").strip()


def _get_admin_chat_id() -> int:
    if not ADMIN_CHAT_ID:
        raise RuntimeError("ADMIN_CHAT_ID is missing in .env")
    return int(ADMIN_CHAT_ID)


def _escape(text: str) -> str:
    return html.escape((text or "").strip())


def partner_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить бизнес в каталог",
                    callback_data="partner:add",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Нужен бот",
                    callback_data="bizbot:open",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 В меню",
                    callback_data="partner:to_menu",
                )
            ],
        ]
    )


def partner_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="partner:cancel",
                )
            ]
        ]
    )


def partner_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Отправить",
                    callback_data="partner:confirm",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Заполнить заново",
                    callback_data="partner:restart",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="partner:cancel",
                )
            ],
        ]
    )


def partner_done_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 В меню",
                    callback_data="partner:to_menu",
                )
            ]
        ]
    )


@router.callback_query(F.data == "partner:open")
async def partner_open(query: CallbackQuery, state: FSMContext):
    await state.clear()

    if query.message:
        await query.message.edit_text(
            "🤝 <b>Партнёрство с AliMind</b>\n\n"
            "Вы можете:\n"
            "• добавить бизнес в каталог\n"
            "• получать обращения клиентов\n"
            "• подключить Telegram-бота\n\n"
            "<b>Выберите действие:</b>",
            parse_mode="HTML",
            reply_markup=partner_kb(),
        )
    await query.answer()


@router.callback_query(F.data == "partner:add")
async def partner_add(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(PartnerApplyFSM.business_name)

    if query.message:
        await query.message.edit_text(
            "<b>Шаг 1 из 4</b>\n\n"
            "Как называется ваш бизнес?",
            parse_mode="HTML",
            reply_markup=partner_cancel_kb(),
        )
    await query.answer()


@router.message(StateFilter(PartnerApplyFSM.business_name))
async def partner_business_name(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer("Введите название бизнеса.")
        return

    await state.update_data(business_name=text)
    await state.set_state(PartnerApplyFSM.category)

    await message.answer(
        "<b>Шаг 2 из 4</b>\n\n"
        "Укажите категорию или сферу бизнеса.\n\n"
        "Например: салон красоты, кафе, спорт, такси.",
        parse_mode="HTML",
        reply_markup=partner_cancel_kb(),
    )


@router.message(StateFilter(PartnerApplyFSM.category))
async def partner_category(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer("Укажите категорию или сферу бизнеса.")
        return

    await state.update_data(category=text)
    await state.set_state(PartnerApplyFSM.request)

    await message.answer(
        "<b>Шаг 3 из 4</b>\n\n"
        "Что именно вам нужно?\n\n"
        "Например: добавить бизнес в каталог, получать заявки, подключить бота.",
        parse_mode="HTML",
        reply_markup=partner_cancel_kb(),
    )


@router.message(StateFilter(PartnerApplyFSM.request))
async def partner_request(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer("Коротко опишите запрос.")
        return

    await state.update_data(request=text)
    await state.set_state(PartnerApplyFSM.contact)

    await message.answer(
        "<b>Шаг 4 из 4</b>\n\n"
        "Оставьте контакт для связи: Telegram, телефон или WhatsApp.",
        parse_mode="HTML",
        reply_markup=partner_cancel_kb(),
    )


@router.message(StateFilter(PartnerApplyFSM.contact))
async def partner_contact(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer("Оставьте контакт для связи.")
        return

    await state.update_data(contact=text)
    data = await state.get_data()
    await state.set_state(PartnerApplyFSM.confirm)

    summary = (
        "<b>Проверьте заявку</b>\n\n"
        f"<b>Бизнес:</b> {_escape(data.get('business_name', ''))}\n"
        f"<b>Категория:</b> {_escape(data.get('category', ''))}\n"
        f"<b>Запрос:</b> {_escape(data.get('request', ''))}\n"
        f"<b>Контакт:</b> {_escape(text)}"
    )

    await message.answer(
        summary,
        parse_mode="HTML",
        reply_markup=partner_confirm_kb(),
    )


@router.callback_query(F.data == "partner:restart")
async def partner_restart(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(PartnerApplyFSM.business_name)

    if query.message:
        await query.message.edit_text(
            "<b>Шаг 1 из 4</b>\n\n"
            "Заполняем заново.\n\n"
            "Как называется ваш бизнес?",
            parse_mode="HTML",
            reply_markup=partner_cancel_kb(),
        )
    await query.answer("Заполняем заново")


@router.callback_query(F.data == "partner:cancel")
async def partner_cancel(query: CallbackQuery, state: FSMContext):
    await state.clear()

    if query.message:
        await query.message.edit_text(
            "Заявка отменена.",
            parse_mode="HTML",
            reply_markup=partner_done_kb(),
        )
    await query.answer("Отменено")


@router.callback_query(F.data == "partner:confirm", StateFilter(PartnerApplyFSM.confirm))
async def partner_confirm(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    admin_text = (
        "<b>🤝 Новая партнёрская заявка</b>\n\n"
        f"<b>Бизнес:</b> {_escape(data.get('business_name', ''))}\n"
        f"<b>Категория:</b> {_escape(data.get('category', ''))}\n"
        f"<b>Запрос:</b> {_escape(data.get('request', ''))}\n"
        f"<b>Контакт:</b> {_escape(data.get('contact', ''))}\n\n"
        "<b>📍 Источник:</b> AliMind / Partner Apply"
    )

    try:
        await query.bot.send_message(
            chat_id=_get_admin_chat_id(),
            text=admin_text,
            parse_mode="HTML",
        )

        await state.clear()

        if query.message:
            await query.message.edit_text(
                "Спасибо. Партнёрская заявка отправлена.\n"
                "Мы посмотрим запрос и свяжемся с вами по указанному контакту.",
                parse_mode="HTML",
                reply_markup=partner_done_kb(),
            )

        await query.answer("Заявка отправлена")

    except Exception as e:
        await query.answer("Ошибка отправки", show_alert=True)
        if query.message:
            await query.message.answer(
                f"Не удалось отправить заявку.\nОшибка: <code>{html.escape(str(e))}</code>",
                parse_mode="HTML",
            )


@router.callback_query(F.data == "partner:to_menu")
async def partner_to_menu(query: CallbackQuery, state: FSMContext):
    await state.clear()
    if query.message:
        await _send_start(query.message)
    await query.answer()

async def _safe_edit(query: CallbackQuery, text: str, reply_markup=None):
    if not query.message:
        await query.answer()
        return

    try:
        await query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise

    await query.answer()