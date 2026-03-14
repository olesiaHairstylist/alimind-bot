# bot/handlers/start.py
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)

router = Router()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
START_IMAGE = PROJECT_ROOT / "assets" / "start.png"


def build_main_menu_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="🌆 События города", callback_data="city_today")],
        [InlineKeyboardButton(text="☎️ Важные службы города", callback_data="emergency_contacts")],
        [InlineKeyboardButton(text="📄 ВНЖ", callback_data="catopen:migration")],
        [InlineKeyboardButton(text="🚌 Транспорт", callback_data="catopen:transport")],

        [InlineKeyboardButton(text="🗣 Услуги переводчика", callback_data="catopen:trn")],
        [InlineKeyboardButton(text="💇 Салон красоты", callback_data="catopen:beauty")],
        [InlineKeyboardButton(text="🍽 Кафе и рестораны", callback_data="catopen:cafe")],
        [InlineKeyboardButton(text="🚕 Такси", callback_data="catopen:taxi")],
        [InlineKeyboardButton(text="⚽ Спорт", callback_data="catopen:sport")],
        [InlineKeyboardButton(text="🎭 Досуг", callback_data="catopen:fun")],

        [InlineKeyboardButton(text="🤝 Стать партнёром AliMind", callback_data="partner:open")],
        [InlineKeyboardButton(text="🤖 Бот для бизнеса", callback_data="bizbot:open")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _send_start(message: Message) -> None:
    try:
        if START_IMAGE.exists() and START_IMAGE.stat().st_size > 0:
            await message.answer_photo(FSInputFile(str(START_IMAGE)))
    except Exception:
        pass

    await message.answer(
        "Выберите раздел:\n"
        "ℹ️ Если нужна справка — напишите /help",
        reply_markup=build_main_menu_kb(),
        parse_mode=None,
    )


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await _send_start(message)


@router.message(F.text.regexp(r"^/start(\s|@|$)"))
async def start_any_handler(message: Message) -> None:
    await _send_start(message)


@router.callback_query(F.data == "back_main_menu")
async def back_main_menu_handler(query: CallbackQuery) -> None:
    await query.answer()

    try:
        await query.message.delete()
    except Exception:
        pass

    await query.message.answer(
        "Выберите раздел:\n"
        "ℹ️ Если нужна справка — напишите /help",
        reply_markup=build_main_menu_kb(),
        parse_mode=None,
    )