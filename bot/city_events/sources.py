from __future__ import annotations

from typing import Dict, List
import re
import aiohttp
from bs4 import BeautifulSoup


ALANYA_PHARMACY_URL = "https://www.alanyaeo.org.tr/tr/nobetci-eczaneler"


async def fetch_duty_pharmacies() -> List[Dict[str, str]]:
    """
    Получает список дежурных аптек Alanya
    источник: Alanya Eczacı Odası
    """

    pharmacies: List[Dict[str, str]] = []

    async with aiohttp.ClientSession() as session:
        async with session.get(ALANYA_PHARMACY_URL) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n", strip=True)
    lines = [x.strip() for x in text.splitlines() if x.strip()]

    current_name = None
    current_phone = None
    address_parts: List[str] = []

    for line in lines:

        # начало новой аптеки
        if "ECZANESİ" in line.upper():

            if current_name:
                pharmacies.append({
                    "name": current_name,
                    "district": "Alanya",
                    "address": " ".join(address_parts),
                    "phone": current_phone or "",
                })

            current_name = line
            current_phone = None
            address_parts = []
            continue

        # телефон
        if re.search(r"\d{3}\s?\d{3}\s?\d{2}\s?\d{2}", line):
            current_phone = line
            continue

        if current_name:
            address_parts.append(line)

    # последняя аптека
    if current_name:
        pharmacies.append({
            "name": current_name,
            "district": "Alanya",
            "address": " ".join(address_parts),
            "phone": current_phone or "",
        })

    return pharmacies


async def fetch_planned_outages() -> List[Dict[str, str]]:
    """
    Плановые отключения (пока заглушка)
    """

    return []