# bot/ai/render.py

from bot.core.text import to_text

ANSWER_MAX_CHARS = 1_200

WARNING_EXTERNAL = {
    "ru": "⚠️ Вы переходите на внешний сайт. Актуальность информации определяется источником.",
    "tr": "⚠️ Harici bir siteye gidiyorsunuz. Bilginin doğruluğu kaynağa bağlıdır.",
    "en": "⚠️ You are going to an external website. Information accuracy is determined by the source.",
}

NO_DATA = {
    "ru": "В базе проекта нет данных по этому запросу.",
    "tr": "Proje veritabanında bu sorgu için veri yok.",
    "en": "There is no data in the project database for this query.",
}

LABELS = {
    "ru": {"address": "Адрес", "hours": "Часы", "phone": "Телефон", "whatsapp": "WhatsApp", "maps": "Карта", "links": "Официальные ссылки"},
    "tr": {"address": "Adres", "hours": "Saatler", "phone": "Telefon", "whatsapp": "WhatsApp", "maps": "Harita", "links": "Resmi bağlantılar"},
    "en": {"address": "Address", "hours": "Hours", "phone": "Phone", "whatsapp": "WhatsApp", "maps": "Map", "links": "Official links"},
}

def _pick_lang(lang: str) -> str:
    return lang if lang in ("ru", "tr", "en") else "en"

def _title_in_lang(title_value, lang: str) -> str:
    # title can be str/dict/None; prefer dict[lang]
    lang = _pick_lang(lang)
    if isinstance(title_value, dict):
        return to_text(title_value.get(lang) or title_value.get("en") or title_value.get("ru") or title_value.get("tr"))
    return to_text(title_value)

def _only_official_links(links_value):
    """
    links can be list[dict|str]. We keep as-is but caller says they're official.
    If you later store type flags, filter here.
    """
    if not links_value:
        return []
    if isinstance(links_value, list):
        return links_value
    return [links_value]

def render_answer_from_snippet(snippet: dict, lang: str) -> str:
    lang = _pick_lang(lang)
    objects = snippet.get("objects") or []
    if not objects:
        return NO_DATA[lang]

    L = LABELS[lang]
    lines = []
    shown_links = False

    # show up to 3 objects to keep "1 screen"
    for obj in objects[:3]:
        obj_id = to_text(obj.get("id")).strip()
        title = _title_in_lang(obj.get("title"), lang).strip()

        header = f"{title}" if title else obj_id
        if obj_id and title:
            header = f"{title} ({obj_id})"
        lines.append(header)

        address = to_text(obj.get("address")).strip()
        if address:
            lines.append(f"{L['address']}: {address}")

        hours = to_text(obj.get("work_hours")).strip()
        if hours:
            lines.append(f"{L['hours']}: {hours}")

        phone = to_text(obj.get("phone")).strip()
        if phone:
            lines.append(f"{L['phone']}: {phone}")

        wa = to_text(obj.get("whatsapp")).strip()
        if wa:
            lines.append(f"{L['whatsapp']}: {wa}")

        maps_ = to_text(obj.get("maps")).strip()
        if maps_:
            lines.append(f"{L['maps']}: {maps_}")

        links = _only_official_links(obj.get("links"))
        if links:
            lines.append(f"{L['links']}:")
            for li in links[:3]:
                if isinstance(li, dict):
                    name = to_text(li.get("title") or li.get("name") or li.get("label")).strip()
                    url = to_text(li.get("url") or li.get("link")).strip()
                    if name and url:
                        lines.append(f"- {name}: {url}")
                    elif url:
                        lines.append(f"- {url}")
                else:
                    url = to_text(li).strip()
                    if url:
                        lines.append(f"- {url}")
            shown_links = True

        lines.append("")  # spacer

    if shown_links:
        lines.append(WARNING_EXTERNAL[lang])

    answer = "\n".join(lines).strip()

    # enforce one-screen limit
    if len(answer) > ANSWER_MAX_CHARS:
        answer = answer[:ANSWER_MAX_CHARS - 1].rstrip() + "…"

    return answer
