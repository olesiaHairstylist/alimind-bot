from functools import wraps
from aiogram.types import Message

from bot.storage.admin_chat import get_admin_chat_id


def is_admin_chat(chat_id: int) -> bool:
    admin_chat_id = get_admin_chat_id()
    return bool(admin_chat_id and chat_id == admin_chat_id)


def admin_only(handler):
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if not is_admin_chat(message.chat.id):
            return None
        return await handler(message, *args, **kwargs)
    return wrapper
