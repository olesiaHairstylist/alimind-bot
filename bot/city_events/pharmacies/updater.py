from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
import re

import requests
from bs4 import BeautifulSoup

from bot.city_events.storage import PHARMACIES_FILE, save_today_payload

TZ = ZoneInfo("Europe/Istanbul")
ALANYA_PHARMACY_URL = "https://www.alanyaeo.org.tr/tr/nobetci-eczaneler"


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _looks_like_phone(text: str) -> bool:
    digits = re.sub(r"\D", "", text)
    return len(digits) >= 10


def _parse_pharmacies_from_html(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    lines = [_clean(x) for x in text.splitlines() if _clean(x)]

    items: list[dict[str, str]] = []

    current_name = None
    current_phone = None
    address_parts: list[str] = []

    for line in lines:

        # остановка на служебном блоке сайта
        if "Türk Eczacıları Birliği" in line or "©" in line:
            break

        upper = line.upper()

        if "ECZANESİ" in upper and len(line) < 100:

            if current_name:
                items.append({
                    "name": current_name,
                    "district": "Alanya",
                    "address": _clean(" ".join(address_parts)),
                    "phone": current_phone or "",
                })

            current_name = line
            current_phone = None
            address_parts = []
            continue

        if current_name and _looks_like_phone(line):
            current_phone = line
            continue

        if current_name:
            address_parts.append(line)

    if current_name:
        items.append({
            "name": current_name,
            "district": "Alanya",
            "address": _clean(" ".join(address_parts)),
            "phone": current_phone or "",
        })

    return items


def update_pharmacies_today() -> None:

    items: list[dict[str, str]] = []

    try:
        response = requests.get(ALANYA_PHARMACY_URL, timeout=20)
        response.raise_for_status()

        items = _parse_pharmacies_from_html(response.text)

    except Exception as e:
        print(f"[CITY_EVENTS] pharmacy fetch failed: {e}")

    updated_at = datetime.now(TZ).isoformat()

    save_today_payload(PHARMACIES_FILE, items, updated_at)