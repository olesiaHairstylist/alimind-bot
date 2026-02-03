# bot/handlers/partner_connect.py
# PARTNER_CONNECT_V2 (one-time)
#
# Команда: /partner_connect <CARD_ID>
# - проверяем, что CARD_ID есть в registry
# - проверяем, что карточка партнёрская (status == "partner" или is_partner == true)
# - сохраняем привязку card_id -> chat_id в data/state/partner_links.json
# - НЕ трогаем core, только расширение
#
# ВАЖНО:
# - router подключить ДО fallback в main.py
# - parse_mode=None (инвариант для списков/ID; тут тоже без Markdown)

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.core.registry import registry
from bot.core.text import to_text
from bot.storage.partner_links import set_link

router = Router()


def _is_partner_obj(obj: dict) -> bool:
    status = to_text(obj.get("status")).strip().lower()
    if status == "partner":
        return True
    # поддержка альтернативного флага, если где-то уже используется
    is_partner = obj.get("is_partner")
    if isinstance(is_partner, bool) and is_partner:
        return True
    return False


@router.message(Command("partner_connect"))
async def cmd_partner_connect(message: Message) -> None:
    if not message.from_user or not message.chat:
        return

    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "Использование:\n"
            "/partner_connect <CARD_ID>\n\n"
            "Пример:\n"
            "/partner_connect TRN_SERKAN",
            parse_mode=None,
        )
        return

    card_id = parts[1].strip().strip('"').strip("'")
    if not card_id:
        await message.answer("❌ Некорректный CARD_ID.", parse_mode=None)
        return

    obj = registry.get(card_id)
    if not isinstance(obj, dict):
        await message.answer(f"❌ Карточка не найдена: {card_id}", parse_mode=None)
        return

    if not _is_partner_obj(obj):
        await message.answer(
            "❌ Эта карточка не помечена как партнёр.\n"
            "Если вы партнёр — попросите администратора включить статус partner.",
            parse_mode=None,
        )
        return

    chat_id = message.chat.id
    username = (message.from_user.username or "").strip() or None

    try:
        set_link(card_id=card_id, chat_id=chat_id, username=username)
    except Exception as e:
        await message.answer(f"❌ Не удалось подключить партнёра: {e}", parse_mode=None)
        return

    name = to_text(obj.get("name")).strip() or card_id

    await message.answer(
        "✅ Партнёр подключён.\n\n"
        f"Карточка: {name}\n"
        f"ID: {card_id}\n\n"
        "Теперь вы будете получать запросы от клиентов через AliMind Directory.",
        parse_mode=None,
    )
