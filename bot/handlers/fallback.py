from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter

router = Router()

# FALLBACK_SAFE_V1:
# - только текст
# - не команда
# - ТОЛЬКО когда FSM = None
@router.message(StateFilter(None), F.text, ~F.text.startswith("/"))
async def fallback_text(message: Message) -> None:
    await message.answer(
        "Не понял запрос.\n"
        "/start — меню\n"
        "/search — поиск\n"
        "/recent — последние\n"
        "/fav — избранное\n"
        "/help — справка\n\n"
        "Карточка: отправьте ID (например, GOV_ASAT).",
        parse_mode=None,
    )

# UNKNOWN_COMMAND_FALLBACK_V1:
# - команды
# - ТОЛЬКО когда FSM = None
@router.message(StateFilter(None), F.text, F.text.startswith("/"))
async def fallback_command(message: Message) -> None:
    cmd = (message.text or "").strip()
    await message.answer(
        f"Команда не распознана: {cmd}\n\n"
        "Доступно:\n"
        "/start — меню\n"
        "/search — поиск\n"
        "/recent — последние\n"
        "/fav — избранное\n"
        "/help — справка",
        parse_mode=None,
    )
