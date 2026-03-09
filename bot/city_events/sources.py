# bot/city_events/sources.py
from __future__ import annotations

from typing import Dict, List

# TODO: заменить на реальные fetch'и из официальных источников
# Сейчас — безопасные заглушки: всегда возвращают пусто, чтобы UI показывал PLAN B / "нет списка".


async def fetch_duty_pharmacies() -> List[Dict[str, str]]:
    """
    Возвращает список аптек на сегодня.
    Каждая запись: name, district, address, phone
    """
    return []


async def fetch_planned_outages() -> List[Dict[str, str]]:
    """
    Возвращает список плановых отключений на сегодня.
    Каждая запись: type, area, period, reason
    """
    return []
