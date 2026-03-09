# bot/city_events/render.py
from __future__ import annotations

from typing import Dict, List

PLAN_B_OUTAGES_TEXT = (
    "**На сегодня данные о плановых отключениях воды и электричества отсутствуют.**\n"
    "Информация публикуется по мере поступления от официальных служб."
)

PHARM_HEADER = (
    "**Дежурные аптеки на сегодня.**\n"
    "Информация публикуется по официальным данным города."
)

def render_pharmacies(items: List[Dict[str, str]]) -> str:
    # 4 поля: name, district, address, phone
    if not items:
        # для аптек baseline заглушки не задан — делаем тихо и честно
        return PHARM_HEADER + "\n\n" + "На сегодня список дежурных аптек отсутствует."
    lines = [PHARM_HEADER, ""]
    for it in items:
        name = it.get("name", "").strip()
        district = it.get("district", "").strip()
        address = it.get("address", "").strip()
        phone = it.get("phone", "").strip()

        # минимально, без лишних украшений
        lines.append(f"{name}")
        if district:
            lines.append(f"{district}")
        if address:
            lines.append(f"{address}")
        if phone:
            lines.append(f"{phone}")
        lines.append("")  # пустая строка между карточками

    return "\n".join(lines).strip()


def render_outages(items: List[Dict[str, str]]) -> str:
    # Ровно 4 поля: type, area, period, reason
    if not items:
        return PLAN_B_OUTAGES_TEXT

    lines: List[str] = []
    for it in items:
        t = it.get("type", "").strip()          # "Вода" / "Электричество"
        area = it.get("area", "").strip()       # "Mahmutlar — Barbaros Cd."
        period = it.get("period", "").strip()   # "Сегодня, с 09:00 до 17:00"
        reason = it.get("reason", "").strip()   # "Плановые технические работы"

        # жёстко 4 строки
        lines.append(t)
        lines.append(area)
        lines.append(period)
        lines.append(reason)
        lines.append("")

    return "\n".join(lines).strip()
