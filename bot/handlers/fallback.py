from aiogram import Router
from aiogram.types import Message

from bot.handlers.admin_guard import is_admin_chat

router = Router()


@router.message()
async def fallback_handler(message: Message):
    text = (message.text or "").strip()

    # 🔒 скрываем админ-команды от всех, кроме админа
    if text.startswith("/admin_") and not is_admin_chat(message.chat.id):
        return

    # обычный fallback для пользователей
    await message.answer(
        "Команда не распознана.\n\n"
        "Доступно:\n"
        "/start — меню\n"
        "/search — поиск\n"
        "/recent — последние\n"
        "/fav — избранное\n"
        "/help — справка",
        parse_mode=None
    )
