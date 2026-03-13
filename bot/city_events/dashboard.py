from __future__ import annotations

from datetime import datetime

from bot.city_events.storage import (
    PHARMACIES_FILE,
    OUTAGES_FILE,
    load_today_payload,
)

TYPE_LABEL = {
    "water": "🚰 Вода",
    "electricity": "⚡ Электричество",
}


def _fmt_updated_at(value: str | None) -> str:
    if not value:
        return "неизвестно"

    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return "неизвестно"


def _pick_latest_updated_at(*values: str | None) -> str | None:
    parsed: list[datetime] = []

    for value in values:
        if not value:
            continue
        try:
            parsed.append(datetime.fromisoformat(value))
        except Exception:
            continue

    if not parsed:
        return None

    return max(parsed).isoformat()


def _render_pharmacies_summary(items: list[dict], limit: int = 3) -> list[str]:
    if not items:
        return ["На сегодня данные отсутствуют."]

    lines: list[str] = []
    for it in items[:limit]:
        name = str(it.get("name", "")).strip() or "Без названия"
        district = str(it.get("district", "")).strip() or "Район не указан"
        lines.append(f"• {name} — {district}")

    if len(items) > limit:
        lines.append(f"… и ещё {len(items) - limit}")

    return lines


def _render_outages_summary(items: list[dict], limit: int = 3) -> list[str]:
    if not items:
        return ["На сегодня данные отсутствуют."]

    lines: list[str] = []
    for it in items[:limit]:
        item_type = str(it.get("type", "")).strip().lower()
        area = str(it.get("area", "")).strip() or "Район не указан"
        period = str(it.get("period", "")).strip() or "Время не указано"
        label = TYPE_LABEL.get(item_type, "🔧 Событие")
        lines.append(f"• {label} — {area}")
        lines.append(f"  ⏱ {period}")

    if len(items) > limit:
        lines.append(f"… и ещё {len(items) - limit}")

    return lines


def render_city_today_dashboard() -> str:
    pharm_payload = load_today_payload(PHARMACIES_FILE)
    outages_payload = load_today_payload(OUTAGES_FILE)

    latest_updated_at = _pick_latest_updated_at(
        pharm_payload.get("updated_at"),
        outages_payload.get("updated_at"),
    )

    lines: list[str] = [
        "🌆 События города сегодня",
        "",
        f"Последнее обновление: {_fmt_updated_at(latest_updated_at)}",
        "",
        "💊 Дежурные аптеки",
        *_render_pharmacies_summary(pharm_payload.get("items", [])),
        "",
        "🔌 Плановые отключения",
        *_render_outages_summary(outages_payload.get("items", [])),
        "",
        "ℹ️ Информация публикуется по официальным данным города.",
    ]

    return "\n".join(lines).strip()