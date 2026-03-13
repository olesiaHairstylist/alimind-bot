from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from bot.city_events.storage import write_today_electricity
from bot.city_events.outages.electricity_fetcher import (
    fetch_electricity_items,
    parse_electricity,
)

TZ = ZoneInfo("Europe/Istanbul")


def update_outages_today() -> None:
    items: list[dict[str, str]] = []

    try:
        raw_data = fetch_electricity_items()
        items = parse_electricity(raw_data)
        print(f"[CITY_EVENTS] electricity items: {len(items)}")
    except Exception as e:
        print(f"[CITY_EVENTS] outages fetch failed: {e}")

    today = datetime.now(TZ).date()
    write_today_electricity(items, today)
    