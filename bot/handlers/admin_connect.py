# bot/handlers/admin_connect.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.storage.admin_chat import set_admin_chat_id

router = Router()


@router.message(Command("admin_connect"))
async def cmd_admin_connect(message: Message):
    chat_id = message.chat.id
    set_admin_chat_id(chat_id)

    await message.answer(
        "✅ Администратор подключён.\n"
        "Уведомления будут приходить в этот чат.",
        parse_mode=None,
    )
