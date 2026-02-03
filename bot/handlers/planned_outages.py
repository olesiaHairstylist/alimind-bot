from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

router = Router()

TODAY_JSON_PATH = Path("data/events/planned_outages/today.json")

HEADER_TEXT = (
    "Плановые отключения воды и электричества на сегодня.\n"
    "Информация публикуется по официальным данным города."
)

PLAN_B_TEXT = (
    "На сегодня данные о плановых отключениях воды и электричества отсутствуют.\n"
    "Информация публикуется по мере поступления от официальных служб."
)

TYPE_LABEL = {
    "water": "🚰 Вода",
    "electricity": "⚡ Электричество",
}


def _safe_read_today_items() -> list[dict[str, str]]:
    """
    Читает today.json.
    Любая проблема -> []
    """
    try:
        if not TODAY_JSON_PATH.exists():
            return []

        raw = TODAY_JSON_PATH.read_text(encoding="utf-8").strip()
        if not raw:
            return []

        data: Any = json.loads(raw)
        if not isinstance(data, list):
            return []

        items: list[dict[str, str]] = []
        for x in data:
            if not isinstance(x, dict):
                continue

            t = str(x.get("type", "")).strip().lower()
            area = str(x.get("area", "")).strip()
            period = str(x.get("period", "")).strip()
            reason = str(x.get("reason", "")).strip()

            # Жёсткая валидация по baseline:
            # - type только water/electricity
            # - area + period должны быть
            if t not in TYPE_LABEL:
                continue
            if not area or not period:
                continue

            items.append(
                {
                    "type": t,
                    "area": area,
                    "period": period,
                    "reason": reason,
                }
            )

        return items
    except Exception:
        return []


def _render_today(items: list[dict[str, str]]) -> str:
    if not items:
        return f"{HEADER_TEXT}\n\n{PLAN_B_TEXT}"

    blocks: list[str] = [HEADER_TEXT, ""]

    for it in items:
        lines = [
            TYPE_LABEL.get(it["type"], "—"),
            f"📍 {it['area']}",
            f"⏱ {it['period']}",
            f"🛠 {it['reason']}" if it["reason"] else "🛠 —",
        ]
        blocks.append("\n".join(lines))
        blocks.append("")

    return "\n".join(blocks).rstrip()


# Команда для smoke-теста
@router.message(Command("outages_today"))
async def outages_today_cmd(message: Message) -> None:
    items = _safe_read_today_items()
    text = _render_today(items)
    await message.answer(text, parse_mode=None)


# Callback для кнопки меню
# callback_data: "outages_today"
@router.callback_query(lambda c: c.data == "outages_today")
async def outages_today_cb(call: CallbackQuery) -> None:
    items = _safe_read_today_items()
    text = _render_today(items)

    await call.answer()

    try:
        await call.message.edit_text(text, parse_mode=None)
    except Exception:
        await call.message.answer(text, parse_mode=None)
