from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

router = Router()

# EVENTS DATA (НЕ core, не loader)
TODAY_JSON_PATH = Path("data/events/on_duty_pharmacies/today.json")

HEADER_TEXT = (
    "Дежурные аптеки на сегодня.\n"
    "Информация публикуется по официальным данным города."
)

PLAN_B_TEXT = (
    "На сегодня данные о дежурных аптеках отсутствуют.\n"
    "Информация публикуется по мере поступления от официальных служб."
)


def _safe_read_today_items() -> list[dict[str, str]]:
    """
    Читает today.json.
    Любая проблема (нет файла / пусто / битый json / неправильная структура) -> []
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

            name = str(x.get("name", "")).strip()
            district = str(x.get("district", "")).strip()
            address = str(x.get("address", "")).strip()
            phone = str(x.get("phone", "")).strip()

            # Жёсткое правило: показываем только если есть хотя бы name + district
            # (остальное может быть пустым, но лучше не ломать выдачу)
            if not name or not district:
                continue

            items.append(
                {
                    "name": name,
                    "district": district,
                    "address": address,
                    "phone": phone,
                }
            )

        return items
    except Exception:
        return []


def _render_today(items: list[dict[str, str]]) -> str:
    if not items:
        return f"{HEADER_TEXT}\n\n{PLAN_B_TEXT}"

    blocks: list[str] = [HEADER_TEXT, ""]  # header + пустая строка

    for it in items:
        # Минимальная карточка: 4 поля (как в baseline)
        lines = [
            f"🏥 {it['name']}",
            f"📍 {it['district']}",
            f"🧭 {it['address']}" if it["address"] else "🧭 —",
            f"📞 {it['phone']}" if it["phone"] else "📞 —",
        ]
        blocks.append("\n".join(lines))
        blocks.append("")  # пустая строка между карточками

    return "\n".join(blocks).rstrip()


# Вариант 1: команда (удобно для теста)
@router.message(Command("pharmacy_today"))
async def pharmacy_today_cmd(message: Message) -> None:
    items = _safe_read_today_items()
    text = _render_today(items)
    await message.answer(text, parse_mode=None)


# Вариант 2: callback (подключите к кнопке меню)
# callback_data: "pharm_today"
@router.callback_query(lambda c: c.data == "pharm_today")
async def pharmacy_today_cb(call: CallbackQuery) -> None:
    items = _safe_read_today_items()
    text = _render_today(items)

    # чтобы Telegram не ругался, всегда отвечаем на callback
    await call.answer()

    # редактируем сообщение меню, если возможно; иначе — новым сообщением
    try:
        await call.message.edit_text(text, parse_mode=None)
    except Exception:
        await call.message.answer(text, parse_mode=None)
