from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.city_events.storage import OUTAGES_FILE, load_today_payload
from bot.city_events.render import render_outages

router = Router()


@router.message(Command("outages_today"))
async def outages_today_cmd(message: Message) -> None:
    payload = load_today_payload(OUTAGES_FILE)
    text = render_outages(payload["items"], payload["updated_at"])
    await message.answer(text, parse_mode=None)


@router.callback_query(lambda c: c.data == "outages_today")
async def outages_today_cb(call: CallbackQuery) -> None:
    payload = load_today_payload(OUTAGES_FILE)
    text = render_outages(payload["items"], payload["updated_at"])

    await call.answer()

    try:
        await call.message.edit_text(text, parse_mode=None)
    except Exception:
        await call.message.answer(text, parse_mode=None)