# bot/handlers/city_events.py
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.city_events.storage import PHARMACIES_FILE, OUTAGES_FILE, load_today_items
from bot.city_events.render import render_pharmacies, render_outages

router = Router()

TZ = ZoneInfo("Europe/Istanbul")


@router.callback_query(F.data == "ev:pharmacies_today")
async def ev_pharmacies_today(cb: CallbackQuery) -> None:
    today = datetime.now(TZ).date()
    items = load_today_items(PHARMACIES_FILE, today)
    text = render_pharmacies(items)
    await cb.message.answer(text, parse_mode="Markdown")  # если решите убрать ** — ставим parse_mode=None
    await cb.answer()


@router.callback_query(F.data == "ev:planned_outages")
async def ev_planned_outages(cb: CallbackQuery) -> None:
    today = datetime.now(TZ).date()
    items = load_today_items(OUTAGES_FILE, today)
    text = render_outages(items)
    await cb.message.answer(text, parse_mode="Markdown")
    await cb.answer()
