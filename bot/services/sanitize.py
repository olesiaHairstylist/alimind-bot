from __future__ import annotations

import re

DIGIT_RUN = re.compile(r"\d{6,}")  # длинные номера

def sanitize_text(s: str) -> str:
    if not s:
        return s
    # заменяем длинные цифровые последовательности
    s = DIGIT_RUN.sub("000000", s)
    return s
