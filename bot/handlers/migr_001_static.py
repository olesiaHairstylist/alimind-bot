# bot/handlers/migr_001_static.py
from __future__ import annotations

from pathlib import Path

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

router = Router()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PATH_RU = PROJECT_ROOT / "data" / "migration" / "migr_001" / "ru.md"
PATH_TLDR = PROJECT_ROOT / "data" / "migration" / "migr_001" / "ru_tldr.md"
PATH_MISTAKES = PROJECT_ROOT / "data" / "migration" / "migr_001" / "common_mistakes_tapu_ru.md"

# “Образец бланка + пояснения” (короткая памятка/пример заполнения)
PATH_FORM_SAMPLE = PROJECT_ROOT / "data" / "migration" / "migr_001" / "form_sample_ru.md"

# “Разбор полей формы” (под скан)
PATH_FORM_EXPLAINED = PROJECT_ROOT / "data" / "migration" / "migr_001" / "form_explained_ru.md"

PATH_CHECKLIST = PROJECT_ROOT / "data" / "migration" / "migr_001" / "checklist_before_apply_ru.md"

# Скан (1 страница)
PATH_FORM_SCAN = PROJECT_ROOT / "data" / "migration" / "migr_001" / "form_scan_page1.png"


def _read_md(path: Path) -> str:
    if not path.exists():
        return f"❌ Файл не найден: {path}"
    text = path.read_text(encoding="utf-8").strip()
    return text or "❌ Файл пустой."


def kb_back_to_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ К действиям", callback_data="oc:open:MIGR_001")]
        ]
    )


def kb_checklist_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Официальный бланк (скан)", callback_data="migr:001:form:scan")],
            [InlineKeyboardButton(text="📝 Разбор полей формы", callback_data="migr:001:form:explained")],
            [InlineKeyboardButton(text="⬅️ К действиям", callback_data="oc:open:MIGR_001")],
        ]
    )


async def _send_long(query: CallbackQuery, text: str, *, final_kb: InlineKeyboardMarkup | None = None) -> None:
    """
    Отправляет длинный текст кусками, стараясь резать по переносам.
    В конце — '✅ Готово.' + клавиатура (если передали).
    """
    if not query.message:
        return

    MAX = 3500
    s = (text or "").strip()

    if not s:
        await query.message.answer("❌ Пустой текст.", parse_mode=None, reply_markup=final_kb or kb_back_to_actions())
        return

    while s:
        if len(s) <= MAX:
            await query.message.answer(s, parse_mode=None)
            break

        cut = s.rfind("\n\n", 0, MAX)
        if cut < 500:
            cut = s.rfind("\n", 0, MAX)
        if cut < 200:
            cut = MAX

        await query.message.answer(s[:cut].rstrip(), parse_mode=None)
        s = s[cut:].lstrip()

    await query.message.answer("✅ Готово.", parse_mode=None, reply_markup=final_kb or kb_back_to_actions())


# ---------- MIGR_001 main texts ----------

@router.callback_query(F.data == "migr:001:open")
async def migr_001_open(query: CallbackQuery) -> None:
    await _send_long(query, _read_md(PATH_RU))
    await query.answer()


@router.callback_query(F.data == "migr:001:tldr")
async def migr_001_tldr(query: CallbackQuery) -> None:
    await _send_long(query, _read_md(PATH_TLDR))
    await query.answer()


@router.callback_query(F.data == "migr:001:mistakes")
async def migr_001_mistakes(query: CallbackQuery) -> None:
    await _send_long(query, _read_md(PATH_MISTAKES))
    await query.answer()


@router.callback_query(F.data == "migr:001:form")
async def migr_001_form_sample(query: CallbackQuery) -> None:
    # “Образец бланка + пояснения” (ваш form_sample_ru.md)
    await _send_long(query, _read_md(PATH_FORM_SAMPLE))
    await query.answer()


@router.callback_query(F.data == "migr:001:checklist")
async def migr_001_checklist(query: CallbackQuery) -> None:
    await _send_long(query, _read_md(PATH_CHECKLIST), final_kb=kb_checklist_actions())
    await query.answer()


# ---------- Checklist extra buttons ----------

@router.callback_query(F.data == "migr:001:form:scan")
async def migr_001_form_scan(query: CallbackQuery) -> None:
    if not query.message:
        await query.answer()
        return

    if not PATH_FORM_SCAN.exists():
        await query.message.answer("⚠️ Скан формы временно недоступен.", parse_mode=None, reply_markup=kb_back_to_actions())
        await query.answer()
        return

    await query.message.answer_photo(
        photo=FSInputFile(str(PATH_FORM_SCAN)),
        caption="📄 Официальный бланк заявления (скан, 1 страница).",
        parse_mode=None,
        reply_markup=kb_back_to_actions(),
    )
    await query.answer()


@router.callback_query(F.data == "migr:001:form:explained")
async def migr_001_form_explained(query: CallbackQuery) -> None:
    await _send_long(query, _read_md(PATH_FORM_EXPLAINED), final_kb=kb_back_to_actions())
    await query.answer()
