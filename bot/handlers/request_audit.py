import json
import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

# TODO: replace with actual admin user IDs
ADMIN_USER_IDS = {123456789, 987654321}

AUDIT_PATH = os.path.join("data", "state", "request_audit.jsonl")
DEFAULT_N = 20
MAX_N = 50


def _parse_n(text: str | None) -> int:
    if not text:
        return DEFAULT_N
    parts = text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return DEFAULT_N
    try:
        n = int(parts[1].strip())
    except Exception:
        return DEFAULT_N
    if n <= 0:
        return DEFAULT_N
    return min(n, MAX_N)


def _fmt(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, str):
        v = value.strip()
        return v if v else "—"
    return str(value)


def _get_time(record: dict) -> str:
    ts = record.get("ts")
    if ts:
        return _fmt(ts)
    return _fmt(record.get("time"))


@router.message(Command("audit_last"))
async def cmd_audit_last(message: Message) -> None:
    if not message.from_user:
        return

    user_id = message.from_user.id
    if user_id not in ADMIN_USER_IDS:
        await message.answer("⛔ Доступ запрещён.", parse_mode=None)
        return

    n = _parse_n(message.text)

    events: list[dict] = []
    try:
        with open(AUDIT_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if isinstance(rec, dict):
                    events.append(rec)
    except FileNotFoundError:
        await message.answer("Пока нет событий.", parse_mode=None)
        return
    except Exception:
        await message.answer("Пока нет событий.", parse_mode=None)
        return

    if not events:
        await message.answer("Пока нет событий.", parse_mode=None)
        return

    tail = events[-n:]
    lines: list[str] = []
    for rec in tail:
        time_val = _get_time(rec)
        event_val = _fmt(rec.get("event"))
        request_id = _fmt(rec.get("request_id"))
        card_id = _fmt(rec.get("card_id"))
        user_id_val = _fmt(rec.get("user_id"))
        error_val = _fmt(rec.get("error"))
        lines.append(
            f"{time_val} | {event_val} | {request_id} | {card_id} | {user_id_val} | {error_val}"
        )

    await message.answer("\n".join(lines), parse_mode=None)

    @router.message(Command("chatid"))
    async def cmd_chatid(message: Message) -> None:
        await message.answer(str(message.chat.id), parse_mode=None)