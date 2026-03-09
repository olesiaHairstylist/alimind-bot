# bot/handlers/start.py
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)

from bot.handlers.menu import BTN_TO_CATEGORY

router = Router()

# корень проекта: .../bot/handlers/start.py -> parents[2] == project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
START_IMAGE = PROJECT_ROOT / "assets" / "start.png"


def build_main_menu_kb() -> InlineKeyboardMarkup:
    rows = []
    for title, code in BTN_TO_CATEGORY.items():
        rows.append([InlineKeyboardButton(text=title, callback_data=f"catopen:{code}")])

    rows.append([InlineKeyboardButton(text="🤖 Бот для бизнеса", callback_data="bizbot:open")])
    rows.append([InlineKeyboardButton(text="🤝 Стать партнёром AliMind", callback_data="partner:open")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _send_start(message: Message) -> None:
    # 1) Картинка (если есть)
    try:
        if START_IMAGE.exists() and START_IMAGE.stat().st_size > 0:
            await message.answer_photo(FSInputFile(str(START_IMAGE)))
    except Exception:
        # если фото не отправилось — продолжаем без падения
        pass

    # 2) Приветствие + меню
    await message.answer(
        "Выберите раздел:\n"
        "ℹ️ Если нужна справка — напишите /help",
        reply_markup=build_main_menu_kb(),
        parse_mode=None,
    )


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await _send_start(message)


# Страховка: ловит /start, /start <payload>, /start@BotName
@router.message(F.text.regexp(r"^/start(\s|@|$)"))
async def start_any_handler(message: Message) -> None:
    await _send_start(message)
