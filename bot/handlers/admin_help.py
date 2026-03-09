from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.handlers.admin_guard import admin_only

router = Router()


@router.message(Command("admin_help"))
@admin_only
async def admin_help(message: Message):
    await message.answer(
        "🛡 Админ-справка\n\n"
        "Доступные команды:\n"
        "/admin_status — состояние системы\n"
        "/admin_funnel — воронка и проценты\n"
        "/admin_connect — назначить этот чат админ-чатом\n"
        "/admin_help — эта справка\n\n"
        "Примечание:\n"
        "Админ-команды работают только в этом чате.\n"
        "Вне админ-чата команды скрыты.",
        parse_mode=None
    )
