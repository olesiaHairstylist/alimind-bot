from datetime import datetime, timedelta, timezone
import os  # ← ВОТ ЭТОГО НЕ ХВАТАЛО

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.storage.admin_chat import get_admin_chat_id

router = Router()

STATE_DIR = os.path.join("data", "state")
PARTNER_LINKS_PATH = os.path.join(STATE_DIR, "partner_links.json")
AUDIT_PATH = os.path.join(STATE_DIR, "request_audit.jsonl")


@router.message(Command("admin_status"))
async def admin_status(message: Message) -> None:
    admin_chat_id = get_admin_chat_id()

    if admin_chat_id != message.chat.id:
        await message.answer("⛔ У вас нет прав администратора.", parse_mode=None)
        return

    text = (
        "🛡 <b>Admin status</b>\n\n"
        f"admin_chat_id: {admin_chat_id}\n"
        f"partner_links: {'OK' if os.path.exists(PARTNER_LINKS_PATH) else '—'}\n"
        f"audit_log: {'OK' if os.path.exists(AUDIT_PATH) else '—'}\n"
        f"time: {datetime.now(timezone.utc).isoformat()}"
    )

    await message.answer(text, parse_mode="HTML")
