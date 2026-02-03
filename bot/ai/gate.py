# bot/ai/gate.py

from bot.core.text import to_text
from bot.ai.snippet import build_snippet
from bot.ai.render import render_answer_from_snippet, NO_DATA

SNIPPET_MAX_CHARS = 12_000
ANSWER_MAX_CHARS = 1_200
AI_QUERY_MAX_CHARS = 500

def detect_language(text: str) -> str:
    t = (text or "").lower()

    if any("а" <= c <= "я" for c in t):
        return "ru"
    if any(c in t for c in ("ğ", "ş", "ı", "ç", "ö", "ü")):
        return "tr"
    return "en"

def ai_one_shot_answer(user_text: str) -> dict:
    text = to_text(user_text).strip()
    if not text:
        return {"ok": False, "error": "empty_query"}

    if len(text) > AI_QUERY_MAX_CHARS:
        return {"ok": False, "error": "query_too_long"}

    lang = detect_language(text)

    snippet = build_snippet(
        query=text,
        max_chars=SNIPPET_MAX_CHARS
    )

    answer = render_answer_from_snippet(snippet=snippet, lang=lang)

    # строгое "нет данных"
    if snippet.get("objects") == []:
        answer = NO_DATA.get(lang, NO_DATA["en"])

    if len(answer) > ANSWER_MAX_CHARS:
        answer = answer[:ANSWER_MAX_CHARS - 1].rstrip() + "…"

    return {
        "ok": True,
        "lang": lang,
        "answer": answer,
        "objects_count": len(snippet.get("objects") or []),
    }
