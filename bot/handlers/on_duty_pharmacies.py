from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.city_events.storage import PHARMACIES_FILE, load_today_payload
from bot.city_events.render import render_pharmacies

router = Router()


@router.message(Command("pharmacy_today"))
async def pharmacy_today_cmd(message: Message) -> None:
    payload = load_today_payload(PHARMACIES_FILE)
    text = render_pharmacies(payload["items"], payload["updated_at"])
    await message.answer(text, parse_mode=None)


@router.callback_query(lambda c: c.data == "pharm_today")
async def pharmacy_today_cb(call: CallbackQuery) -> None:
    payload = load_today_payload(PHARMACIES_FILE)
    text = render_pharmacies(payload["items"], payload["updated_at"])

    await call.answer()

    try:
        await call.message.edit_text(text, parse_mode=None)
    except Exception:
        await call.message.answer(text, parse_mode=None)