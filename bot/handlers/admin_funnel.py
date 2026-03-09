from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.handlers.admin_guard import admin_only  # ваша защита админа

AUDIT_PATH = Path("data/state/request_audit.jsonl")

router = Router()

def _read_audit():
    if not AUDIT_PATH.exists():
        return []
    rows = []
    for line in AUDIT_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows

def _pct(num: int, den: int) -> str:
    if den <= 0:
        return "—"
    return f"{(num * 100.0 / den):.1f}%"

@router.message(Command("admin_funnel"))
@admin_only
async def admin_funnel(message: Message):
    rows = _read_audit()
    c = Counter(r.get("event") for r in rows)

    preq = c.get("preq_click", 0)
    ok = c.get("confirm_ok", 0)
    fail = c.get("confirm_fail", 0)
    nc = c.get("not_connected", 0)

    responded = c.get("partner_replied", 0)
    in_work = c.get("partner_work", 0)
    declined = c.get("partner_declined", 0)

    delivery_attempts = ok + fail + nc  # или только ok+fail (если nc считать отдельно)

    lines = []
    lines.append("📈 Funnel (audit)")
    lines.append("")
    lines.append(f"preq_click: {preq}")
    lines.append(f"confirm_ok: {ok}")
    lines.append(f"confirm_fail: {fail}")
    lines.append(f"not_connected: {nc}")
    lines.append("")
    # Проценты
    lines.append(f"Delivery rate (ok / attempts): {_pct(ok, delivery_attempts)}")
    lines.append(f"Fail rate (fail / attempts): {_pct(fail, delivery_attempts)}")
    lines.append(f"Not-connected rate (nc / attempts): {_pct(nc, delivery_attempts)}")
    lines.append("")
    lines.append(f"Partner response rate (replied / ok): {_pct(responded, ok)}")
    lines.append(f"Partner in-work rate (work / ok): {_pct(in_work, ok)}")
    lines.append(f"Partner decline rate (declined / ok): {_pct(declined, ok)}")

    await message.answer("\n".join(lines), parse_mode=None)
