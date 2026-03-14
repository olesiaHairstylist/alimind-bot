from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.city_events.storage import (
    ELECTRICITY_FILE,
    WATER_FILE,
    load_today_payload,
)
from bot.city_events.render import render_outages

router = Router()


def _merge_outages_payload() -> tuple[list[dict[str, str]], str | None]:
    electricity_payload = load_today_payload(ELECTRICITY_FILE)
    water_payload = load_today_payload(WATER_FILE)

    electricity_items = electricity_payload.get("items", [])
    water_items = water_payload.get("items", [])

    items: list[dict[str, str]] = []
    if isinstance(water_items, list):
        items.extend(water_items)
    if isinstance(electricity_items, list):
        items.extend(electricity_items)

    updated_candidates = [
        water_payload.get("updated_at"),
        electricity_payload.get("updated_at"),
    ]
    updated_at = next(
        (x for x in updated_candidates if isinstance(x, str) and x.strip()),
        None,
    )

    return items, updated_at


@router.message(Command("outages_today"))
async def outages_today_cmd(message: Message) -> None:
    items, updated_at = _merge_outages_payload()
    text = render_outages(items, updated_at)
    await message.answer(text, parse_mode=None)


@router.callback_query(lambda c: c.data == "outages_today")
async def outages_today_cb(call: CallbackQuery) -> None:
    items, updated_at = _merge_outages_payload()
    text = render_outages(items, updated_at)

    await call.answer()

    try:
        await call.message.edit_text(text, parse_mode=None)
    except Exception:
        await call.message.answer(text, parse_mode=None)