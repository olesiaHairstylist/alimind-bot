# bot/handlers/migr_request.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
SERVICE_ID = "MIGR_001"


# ---------- TEXTS ----------
CONSENT_TEXT = (
    "📄 Перед запросом официального разбора\n\n"
    "Пожалуйста, ознакомьтесь с форматом услуги:\n\n"
    "✅ Что вы получите\n"
    "• Документированный разбор требований для ВНЖ\n"
    "• Ответ только по официальным источникам (гос-сайты, официальные PDF/инструкции)\n"
    "• Чёткую фиксацию: что официально требуется / что официально не указано / где есть расхождения\n\n"

    "📄 Перед запросом официального разбора\n\n"
    "Здесь вы можете получить структурированный разбор требований\n"
    "для оформления ВНЖ и смежных миграционных процедур.\n\n"
    "🔍 Как формируется разбор\n"
    "• используется только информация из официальных источников\n"
    "  (гос-сайты, инструкции, официальные PDF-документы)\n"
    "• требования приводятся в понятный и логичный вид\n"
    "• отдельно фиксируется:\n"
    "  — что официально требуется\n"
    "  — что официально не указано\n"
    "  — где есть расхождения\n\n"
    "📘 В результате вы получаете\n"
    "Понятный документ, который помогает разобраться в процедуре\n"
    "и подготовиться к взаимодействию с государственным учреждением.\n\n"
    "Оплата производится за анализ и ясность,\n"
    "а не за исход процедуры."
)


PAYMENT_TEXT = (
    "💳 Оплата официального разбора\n\n"
    "Вы оформляете один официальный разбор требований для ВНЖ\n"
    "в формате документированного ответа.\n\n"
    "✅ Что входит\n"
    "• Структурированный документ по вашей ситуации\n"
    "• Только официальные источники (ссылки, версии, даты)\n"
    "• Фиксация: требуется / не указано / расхождения\n\n"

    "ℹ️ Обратите внимание\n\n"
    "Предоставляемая нами информация не является юридической услугой.\n\n"
    "Информация формируется на основе официальных источников\n"
    "(гос-сайты, официальные инструкции и документы).\n\n"
    "Мы можем помочь вам собрать и упорядочить перечень документов,\n"
    "которые требуются государственными учреждениями.\n\n"
    "Решение по вашему вопросу принимается государственным органом.\n"
    "За результат рассмотрения заявления мы ответственности не несём."
)


IN_PROGRESS_TEXT = (
    "📄 Разбор в работе\n\n"
    "Ваш запрос принят.\n"
    "Мы готовим официальный документированный разбор по вашей ситуации.\n\n"
    "Что сейчас происходит:\n"
    "• анализируются только официальные источники (гос-сайты, инструкции, PDF)\n"
    "• проверяются требования и возможные расхождения\n"
    "• фиксируется, что официально указано, а что — нет\n\n"
    "Спасибо за ожидание."
)


# ---------- FSM ----------
class MigrRequestFSM(StatesGroup):
    consent = State()
    payment = State()

    q_country_city = State()
    q_vnz_type = State()
    q_status = State()
    q_docs_have = State()
    q_goal = State()
    q_notes = State()

    confirm = State()


# ---------- Keyboards ----------
def kb_consent() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я понимаю формат и хочу продолжить", callback_data="mig:consent:ok")],
        [InlineKeyboardButton(text="↩️ Вернуться назад", callback_data=f"oc:open:{SERVICE_ID}")],
    ])


def kb_payment() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить официальный разбор", callback_data="mig:pay:ok")],  # STUB
        [InlineKeyboardButton(text="↩️ Назад", callback_data="mig:pay:back")],
    ])


def kb_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Отправить данные", callback_data="mig:confirm:send")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="mig:confirm:back")],
    ])


def _summary(data: dict) -> str:
    return (
        "✅ Проверьте данные перед отправкой\n\n"
        f"1) Страна и город: {data.get('country_city', '—')}\n"
        f"2) Тип ВНЖ: {data.get('vnz_type', '—')}\n"
        f"3) Текущий статус: {data.get('status', '—')}\n"
        f"4) Документы на руках: {data.get('docs_have', '—')}\n"
        f"5) Цель оформления: {data.get('goal', '—')}\n"
        f"6) Дополнительно: {data.get('notes', '—')}\n"
    )


async def _ensure_state(state: FSMContext, expected: State) -> bool:
    cur = await state.get_state()
    return cur == expected.state


# ---------- Entry point ----------
@router.callback_query(F.data == "mig:req")
async def mig_req_start(query: CallbackQuery, state: FSMContext) -> None:
    if not query.message:
        await query.answer()
        return

    await state.clear()
    await state.set_state(MigrRequestFSM.consent)

    await query.message.answer(CONSENT_TEXT, reply_markup=kb_consent(), parse_mode=None)
    await query.answer()


# ---------- Consent ----------
@router.callback_query(F.data == "mig:consent:ok")
async def mig_consent_ok(query: CallbackQuery, state: FSMContext) -> None:
    if not query.message:
        await query.answer()
        return

    if not await _ensure_state(state, MigrRequestFSM.consent):
        await query.answer()
        return

    await state.set_state(MigrRequestFSM.payment)
    await query.message.answer(PAYMENT_TEXT, reply_markup=kb_payment(), parse_mode=None)
    await query.answer()


# ---------- Payment (stub) ----------
@router.callback_query(F.data == "mig:pay:back")
async def mig_pay_back(query: CallbackQuery, state: FSMContext) -> None:
    if not query.message:
        await query.answer()
        return

    if not await _ensure_state(state, MigrRequestFSM.payment):
        await query.answer()
        return

    await state.set_state(MigrRequestFSM.consent)
    await query.message.answer(CONSENT_TEXT, reply_markup=kb_consent(), parse_mode=None)
    await query.answer()


@router.callback_query(F.data == "mig:pay:ok")
async def mig_pay_ok_stub(query: CallbackQuery, state: FSMContext) -> None:
    if not query.message:
        await query.answer()
        return

    if not await _ensure_state(state, MigrRequestFSM.payment):
        await query.answer()
        return

    await state.set_state(MigrRequestFSM.q_country_city)
    await query.message.answer(
        "📝 Данные для официального разбора\n\n"
        "Ответьте на несколько вопросов. Если не знаете — так и напишите.\n\n"
        "1️⃣ Страна и город\n"
        "Где вы планируете оформлять ВНЖ?",
        parse_mode=None,
    )
    await query.answer("Ок. Давайте соберём данные.", show_alert=False)


# ---------- Questions ----------
@router.message()
async def migr_questions_router(message: Message, state: FSMContext) -> None:
    st = await state.get_state()
    txt = (message.text or "").strip()

    if st == MigrRequestFSM.q_country_city.state:
        await state.update_data(country_city=txt)
        await state.set_state(MigrRequestFSM.q_vnz_type)
        await message.answer(
            "2️⃣ Тип ВНЖ (если знаете)\n"
            "Какой вариант вас интересует?\n"
            "Например: семейный / по аренде / рабочий / не знаю",
            parse_mode=None,
        )
        return

    if st == MigrRequestFSM.q_vnz_type.state:
        await state.update_data(vnz_type=txt)
        await state.set_state(MigrRequestFSM.q_status)
        await message.answer(
            "3️⃣ Ваш текущий статус\n"
            "Кем вы сейчас находитесь в стране?\n"
            "Например: турист / есть ВНЖ / срок заканчивается / за пределами страны",
            parse_mode=None,
        )
        return

    if st == MigrRequestFSM.q_status.state:
        await state.update_data(status=txt)
        await state.set_state(MigrRequestFSM.q_docs_have)
        await message.answer(
            "4️⃣ Какие документы уже есть\n"
            "Перечислите, что у вас есть на руках.\n"
            "Например: паспорт, договор аренды, страховка и т.д.",
            parse_mode=None,
        )
        return

    if st == MigrRequestFSM.q_docs_have.state:
        await state.update_data(docs_have=txt)
        await state.set_state(MigrRequestFSM.q_goal)
        await message.answer(
            "5️⃣ Цель оформления\n"
            "Для чего вам ВНЖ?\n"
            "Например: проживание / семья / работа — кратко",
            parse_mode=None,
        )
        return

    if st == MigrRequestFSM.q_goal.state:
        await state.update_data(goal=txt)
        await state.set_state(MigrRequestFSM.q_notes)
        await message.answer(
            "6️⃣ Дополнительно (по желанию)\n"
            "Есть ли важные детали или ограничения?\n"
            "Например: сроки, отказ в прошлом, особенности.\n"
            "Если нет — напишите: нет",
            parse_mode=None,
        )
        return

    if st == MigrRequestFSM.q_notes.state:
        await state.update_data(notes=txt)
        await state.set_state(MigrRequestFSM.confirm)
        data = await state.get_data()
        await message.answer(_summary(data), reply_markup=kb_confirm(), parse_mode=None)
        return


# ---------- Confirm ----------
@router.callback_query(F.data == "mig:confirm:back")
async def mig_confirm_back(query: CallbackQuery, state: FSMContext) -> None:
    if not query.message:
        await query.answer()
        return

    if not await _ensure_state(state, MigrRequestFSM.confirm):
        await query.answer()
        return

    await state.set_state(MigrRequestFSM.q_notes)
    await query.message.answer(
        "6️⃣ Дополнительно (по желанию)\n"
        "Есть ли важные детали или ограничения?\n"
        "Например: сроки, отказ в прошлом, особенности.\n"
        "Если нет — напишите: нет",
        parse_mode=None,
    )
    await query.answer()


@router.callback_query(F.data == "mig:confirm:send")
async def mig_confirm_send(query: CallbackQuery, state: FSMContext) -> None:
    if not query.message:
        await query.answer()
        return

    if not await _ensure_state(state, MigrRequestFSM.confirm):
        await query.answer()
        return

    await query.message.answer(IN_PROGRESS_TEXT, parse_mode=None)
    await state.clear()
    await query.answer("Принято", show_alert=False)
