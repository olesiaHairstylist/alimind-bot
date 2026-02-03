# bot/core/formatter.py


from html import escape as _h
from bot.core.text import to_text
def format_object_card(obj: dict) -> str:
    name = to_text(obj.get("name")) or "Без названия"
    category = to_text(obj.get("category"))
    address = to_text(obj.get("address"))
    phone = to_text(obj.get("phone"))
    description = to_text(obj.get("description"))

    lines = [f"📍 *{name}*"]

    if category:
        lines.append(f"🏷 {category}")
    if address:
        lines.append(f"📌 {address}")
    if phone:
        lines.append(f"📞 {phone}")
    if description:
        lines.append("")
        lines.append(description)

    return "\n".join(lines)
def format_object_card_html(obj: dict) -> str:
    """
    Telegram-safe HTML card. All dynamic values escaped.
    Use with parse_mode="HTML".
    """
    oid = to_text(obj.get("id")).strip()
    name = to_text(obj.get("name")).strip() or "Без названия"
    category = to_text(obj.get("category")).strip()
    typ = to_text(obj.get("type")).strip()
    status_raw = to_text(obj.get("status")).strip()

    address = to_text(obj.get("address")).strip()
    phone = to_text(obj.get("phone")).strip()
    whatsapp = to_text(obj.get("whatsapp")).strip()
    languages = to_text(obj.get("languages")).strip()
    desc = to_text(obj.get("description")).strip()
    maps_link = to_text(obj.get("maps")).strip() or to_text(obj.get("maps_link")).strip()
    website = to_text(obj.get("website")).strip()

    telegram = to_text(obj.get("telegram")).strip()
    instagram = to_text(obj.get("instagram")).strip()

    # ---- hide tech fields for product cards ----
    obj_type = to_text(obj.get("type")).strip().lower()
    status_l = to_text(obj.get("status")).strip().lower()
    is_partner = bool(obj.get("is_partner", False)) or (status_l == "partner")

    HIDE_TECH_TYPES = {"entry_point", "service_entry", "service_extension"}
    hide_tech = (obj_type in HIDE_TECH_TYPES) and (not is_partner)

    lines: list[str] = []

    # Заголовок
    lines.append(f"<b>{_h(name)}</b>")

    # Helper
    def add(label: str, value: str) -> None:
        v = (value or "").strip()
        if v:
            lines.append(f"<b>{_h(label)}:</b> {_h(v)}")

    # Техполя (только если не hide_tech)
    if not hide_tech:
        if oid:
            lines.append(f"ID: <code>{_h(oid)}</code>")
        add("Категория", category)
        add("Тип", typ)
        add("Статус", status_raw)

    # Нормальные поля — всегда
    add("Адрес", address)
    add("Телефон", phone)
    add("WhatsApp", whatsapp)

    if telegram:
        tg_link = telegram if telegram.startswith("http") else f"https://t.me/{telegram.lstrip('@')}"
        lines.append(f"<b>Telegram:</b> <a href=\"{_h(tg_link, quote=True)}\">{_h(telegram)}</a>")

    if instagram:
        lines.append(f"<b>Instagram:</b> <a href=\"{_h(instagram, quote=True)}\">{_h(instagram)}</a>")

    add("Языки", languages)

    if desc:
        lines.append("")
        lines.append("<b>Описание:</b>")
        lines.append(_h(desc))

    # Ссылки
    links: list[str] = []
    if maps_link:
        links.append(f'🗺 <a href="{_h(maps_link, quote=True)}">Открыть на карте</a>')
    if website:
        links.append(f'🌐 <a href="{_h(website, quote=True)}">Сайт</a>')

    if links:
        lines.append("")
        lines.extend(links)

    return "\n".join(lines)
