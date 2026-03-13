from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from datetime import date
PHARMACIES_FILE = Path("data/events/on_duty_pharmacies/today.json")
ELECTRICITY_FILE = Path("data/events/electricity_outages/today.json")
WATER_FILE = Path("data/events/water_outages/today.json")


def _empty_payload() -> dict[str, Any]:
    return {
        "updated_at": None,
        "items": [],
    }


def save_today_payload(path: Path, items: list[dict[str, Any]], updated_at: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "updated_at": updated_at,
        "items": items,
    }

    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_today_payload(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return _empty_payload()

        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return _empty_payload()

        data = json.loads(raw)
        if not isinstance(data, dict):
            return _empty_payload()

        updated_at = data.get("updated_at")
        items = data.get("items", [])

        if updated_at is not None and not isinstance(updated_at, str):
            updated_at = None

        if not isinstance(items, list):
            items = []

        return {
            "updated_at": updated_at,
            "items": items,
        }
    except Exception:
        return _empty_payload()

def write_today_pharmacies(items: list[dict[str, Any]], today: date) -> None:
    save_today_payload(
        PHARMACIES_FILE,
        items,
        today.isoformat(),
    )


def write_today_outages(items: list[dict[str, Any]], today: date) -> None:
    save_today_payload(
        OUTAGES_FILE,
        items,
        today.isoformat(),
    )
def write_today_electricity(items: list[dict[str, Any]], today: date) -> None:
    save_today_payload(
        ELECTRICITY_FILE,
        items,
        today.isoformat(),
    )


def write_today_water(items: list[dict[str, Any]], today: date) -> None:
    save_today_payload(
        WATER_FILE,
        items,
        today.isoformat(),
    )