# bot/city_events/storage.py
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional

EVENTS_DIR = os.path.join("data", "events")

PHARMACIES_FILE = os.path.join(EVENTS_DIR, "duty_pharmacies.json")
OUTAGES_FILE = os.path.join(EVENTS_DIR, "planned_outages.json")


def _ensure_dirs() -> None:
    os.makedirs(EVENTS_DIR, exist_ok=True)


def _atomic_write_json(path: str, payload: Dict[str, Any]) -> None:
    _ensure_dirs()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def read_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        # тихо: при битом файле ведём себя как "нет данных"
        return None


def write_today_pharmacies(items: List[Dict[str, str]], today: date) -> None:
    _atomic_write_json(PHARMACIES_FILE, {"date": today.isoformat(), "items": items})


def write_today_outages(items: List[Dict[str, str]], today: date) -> None:
    _atomic_write_json(OUTAGES_FILE, {"date": today.isoformat(), "items": items})


def load_today_items(path: str, today: date) -> List[Dict[str, str]]:
    data = read_json(path)
    if not data:
        return []
    if data.get("date") != today.isoformat():
        # файл старый => считаем, что данных "на сегодня" нет
        return []
    items = data.get("items")
    if not isinstance(items, list):
        return []
    # приводим к dict[str,str] максимально мягко
    out: List[Dict[str, str]] = []
    for x in items:
        if isinstance(x, dict):
            out.append({k: str(v) for k, v in x.items()})
    return out
