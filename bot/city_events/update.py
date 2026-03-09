# bot/city_events/update.py
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from bot.city_events.sources import fetch_duty_pharmacies, fetch_planned_outages
from bot.city_events.storage import write_today_pharmacies, write_today_outages


TZ = ZoneInfo("Europe/Istanbul")


async def update_events_today() -> None:
    today = datetime.now(TZ).date()

    # Тихо и безопасно: любая ошибка => как "нет данных"
    try:
        pharmacies = await fetch_duty_pharmacies()
    except Exception:
        pharmacies = []

    try:
        outages = await fetch_planned_outages()
    except Exception:
        outages = []

    write_today_pharmacies(pharmacies, today)
    write_today_outages(outages, today)
