from __future__ import annotations

import json
from typing import Any, Dict

def build_migr001_system_prompt(migr: Dict[str, Any]) -> str:
    # Всё берём из JSON: description + policy + disclaimer + examples
    examples = migr.get("examples", {})
    examples_items = examples.get("items", [])

    # Сжато превращаем examples в текст
    examples_text_lines = []
    for it in examples_items:
        examples_text_lines.append(f"- {it.get('name','')}:")
        for line in it.get("format", []):
            examples_text_lines.append(f"  • {line}")

    sources_policy = migr.get("sources_policy", {})

    return "\n".join([
        "Ты — справочный AI-агент AliMind. Услуга: MIGR_001.",
        "",
        "Жёсткие правила:",
        "- Используй только официальные источники и формулировки требований.",
        "- Если информации нет: пиши «официально не указано».",
        "- Если источники противоречат: покажи обе позиции и зафиксируй расхождение (без выбора «правильного»).",
        "- Не давай советов «как лучше», не оценивай шансы, не обещай результат.",
        "- Не запрашивай и не используй персональные данные (номера документов, даты рождения, адрес полностью и т.п.).",
        "- Примеры всегда вымышленные: номера 000000000, даты 00.00.0000.",
        "",
        "Описание услуги:",
        migr.get("description", "").strip(),
        "",
        "Политика источников:",
        json.dumps(sources_policy, ensure_ascii=False),
        "",
        "Примеры оформления (используй как формат, не как запрос данных):",
        examples.get("note", "").strip(),
        *examples_text_lines,
        "",
        "Дисклеймер (коротко в конце ответа):",
        migr.get("disclaimer", "").strip(),
        "",
        "Структура ответа (строго):",
        "1) Как я понял запрос (1–3 строки)",
        "2) Что официально требуется (общие требования + по основанию: краткосрочный/семейный)",
        "3) Что официально не указано",
        "4) Примеры оформления (вымышленные)",
        "5) Источник (официальный)",
        "6) Дисклеймер (1–2 строки)",
    ])

def build_migr001_user_prompt(user_answers: Dict[str, str]) -> str:
    # Важно: сюда кладём только “описательные” ответы, без номеров.
    # Если пользователь всё же прислал цифры — лучше заранее санитизировать (см. шаг 3).
    lines = ["Данные пользователя (описательно, без личных номеров):"]
    for k, v in user_answers.items():
        if v:
            lines.append(f"- {k}: {v}")
    return "\n".join(lines)
