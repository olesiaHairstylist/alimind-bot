from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

router = Router()

LIST_JSON_PATH = Path("data/events/emergency_contacts/list.json")

HEADER_TEXT = (
    "Экстренные контакты.\n"
    "Используйте в случае срочной необходимости."
)

PLAN_B_TEXT = (
    "Контакты временно недоступны.\n"
    "Информация публикуется по мере поступления от официальных служб."
)

CB = "emergency_contacts"


def _safe_read_items() -> list[dict[str, str]]:
    try:
        if not LIST_JSON_PATH.exists():
            return []

        raw = LIST_JSON_PATH.read_text(encoding="utf-8").strip()
        if not raw:
            return []

        data: Any = json.loads(raw)
        if not isinstance(data, list):
            return []

        items: list[dict[str, str]] = []
        for x in data:
            if not isinstance(x, dict):
                continue

            title = str(x.get("title", "")).strip()
            phone = str(x.get("phone", "")).strip()
            note = str(x.get("note", "")).strip()

            if not title or not phone:
                continue

            items.append({"title": title, "phone": phone, "note": note})

        return items
    except Exception:
        return []


def _render(items: list[dict[str, str]]) -> str:
    if not items:
        return f"{HEADER_TEXT}\n\n{PLAN_B_TEXT}"

    blocks: list[str] = [HEADER_TEXT, ""]
    for it in items:
        lines = [f"• {it['title']}", f"📞 {it['phone']}"]
        if it["note"]:
            lines.append(it["note"])
        blocks.append("\n".join(lines))
        blocks.append("")
    return "\n".join(blocks).rstrip()


@router.message(Command("emergency"))
async def cmd_emergency(message: Message) -> None:
    items = _safe_read_items()
    await message.answer(_render(items), parse_mode=None)


@router.callback_query(lambda c: c.data == CB)
async def cb_emergency(call: CallbackQuery) -> None:
    items = _safe_read_items()
    text = _render(items)

    await call.answer()
    try:
        await call.message.edit_text(text, parse_mode=None)
    except Exception:
        await call.message.answer(text, parse_mode=None)
