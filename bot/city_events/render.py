from __future__ import annotations

from datetime import datetime


PHARM_HEADER_TEXT = (
    "Дежурные аптеки на сегодня.\n"
    "Информация публикуется по официальным данным города."
)

PHARM_PLAN_B_TEXT = (
    "На сегодня данные о дежурных аптеках отсутствуют.\n"
    "Информация публикуется по мере поступления от официальных служб."
)


OUTAGES_HEADER_TEXT = (
    "Отключения электричества на сегодня.\n"
    "Информация публикуется по официальным данным города."
)

OUTAGES_PLAN_B_TEXT = (
    "На сегодня данные об отключениях электричества отсутствуют.\n"
    "Информация публикуется по мере поступления от официальных служб."
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


def render_pharmacies(items: list[dict[str, str]], updated_at: str | None) -> str:
    header = [
        "💊 Дежурные аптеки на сегодня",
        "Информация публикуется по официальным данным города.",
        "",
        f"Последнее обновление: {_fmt_updated_at(updated_at)}",
        "",
    ]

    if not items:
        return "\n".join(header + [PHARM_PLAN_B_TEXT])

    blocks: list[str] = header[:]

    for it in items:
        name = str(it.get("name", "")).strip()
        district = str(it.get("district", "")).strip()
        address = str(it.get("address", "")).strip()
        phone = str(it.get("phone", "")).strip()

        lines = [f"🏥 {name or '—'}"]

        if district:
            lines.append(f"📍 Район: {district}")
        else:
            lines.append("📍 Район: —")

        if address:
            lines.append(f"🧭 Адрес: {address}")
        else:
            lines.append("🧭 Адрес: —")

        if phone:
            lines.append(f"📞 Телефон: {phone}")
        else:
            lines.append("📞 Телефон: —")

        blocks.append("\n".join(lines))
        blocks.append("")

    return "\n".join(blocks).rstrip()


def render_outages(items: list[dict[str, str]], updated_at: str | None) -> str:
    header = [
        OUTAGES_HEADER_TEXT,
        "",
        f"Последнее обновление: {_fmt_updated_at(updated_at)}",
        "",
    ]

    if not items:
        return "".join([]) or "\n".join(header + [OUTAGES_PLAN_B_TEXT])

    blocks: list[str] = header[:]

    for it in items:
        item_type = str(it.get("type", "")).strip().lower()
        area = str(it.get("area", "")).strip()
        period = str(it.get("period", "")).strip()
        reason = str(it.get("reason", "")).strip()

        lines = [
            TYPE_LABEL.get(item_type, "—"),
            f"📍 {area or '—'}",
            f"⏱ {period or '—'}",
            f"🛠 {reason}" if reason else "🛠 —",
        ]
        blocks.append("\n".join(lines))
        blocks.append("")

    return "\n".join(blocks).rstrip()