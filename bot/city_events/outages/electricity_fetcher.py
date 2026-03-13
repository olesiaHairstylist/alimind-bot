from __future__ import annotations

import requests
from typing import Any
from datetime import datetime
from zoneinfo import ZoneInfo

URL = "https://www.akdenizedas.com.tr/elektrik-getir"


def fetch_electricity_items() -> list[dict[str, Any]]:

    payload = {
        "countryName": "ANTALYA",
        "cityName": "ALANYA",
    }

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    r = requests.post(
        URL,
        data=payload,
        headers=headers,
        timeout=20,
    )

    r.raise_for_status()

    data = r.json()

    print("JSON ITEMS:", len(data))

    return data if isinstance(data, list) else []


def parse_electricity(data: list[dict[str, Any]]) -> list[dict[str, str]]:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    items: list[dict[str, str]] = []
    today = datetime.now(ZoneInfo("Europe/Istanbul")).date()

    for row in data:
        planned = row.get("plannedOutage") or {}
        if not isinstance(planned, dict):
            continue

        city = str(planned.get("city", "")).strip().upper()
        county = str(planned.get("county", "")).strip().upper()

        if city != "ANTALYA" or county != "ALANYA":
            continue

        start = str(planned.get("startDateTime", "")).strip()
        end = str(planned.get("endDateTime", "")).strip()
        reason = str(planned.get("reason", "")).strip()
        message = str(planned.get("message", "")).strip()

        if not start:
            continue

        try:
            start_date = datetime.strptime(start[:10], "%Y-%m-%d").date()
        except Exception:
            continue

        if start_date != today:
            continue

        area = "Alanya"
        if message:
            parts = [p.strip() for p in message.split(",") if p.strip()]
            if len(parts) >= 3:
                area = parts[2]

        period = f"{start} - {end}" if start and end else start

        items.append(
            {
                "type": "electricity",
                "area": area,
                "period": period,
                "reason": reason or message,
            }
        )

    print("FILTERED TODAY ITEMS:", len(items))
    return items