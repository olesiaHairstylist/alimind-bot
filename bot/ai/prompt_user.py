# bot/ai/prompt_user.py

import json

def build_user_prompt(query: str, lang: str, snippet: dict, answer_max_chars: int) -> str:
    snippet_json = json.dumps(snippet, ensure_ascii=False)

    return (
        f"User query language: {lang}\n"
        f"User query: {query}\n\n"
        f"JSON snippet (ONLY source of truth):\n{snippet_json}\n\n"
        f"RESPONSE RULES:\n"
        f"- Answer in language: {lang}\n"
        f"- Plain text, no Markdown\n"
        f"- Max {answer_max_chars} characters\n"
        f"- Use ONLY facts from the JSON snippet\n"
        f"- If not found: say there is no data in the project database\n"
    )
