import html
import os

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from bot.keyboards.bizbot import bizbot_admin_kb
from bot.states.bizbot import BizBotLead
from bot.keyboards.bizbot import (
    bizbot_main_kb,
    bizbot_info_kb,
    bizbot_cancel_kb,
    bizbot_confirm_kb,
    bizbot_done_kb,
)
from bot.handlers.start import _send_start
load_dotenv()

router = Router()

ADMIN_CHAT_ID = (os.getenv("ADMIN_CHAT_ID") or "").strip()

BIZBOT_MAIN_TEXT = (
    "<b>Разработка Telegram-ботов для бизнеса</b>\n\n"
    "Мы создаём Telegram-ботов под реальные задачи бизнеса:\n"
    "• приём заявок\n"
    "• запись клиентов\n"
    "• ответы на частые вопросы\n"
    "• каталог услуг\n"
    "• передача обращений владельцу\n\n"
    "Подходит для локального бизнеса, студий, сервисов, секций, "
    "магазинов и специалистов.\n\n"
    "Ниже можно посмотреть, что умеет бот, и оставить заявку."
)

BIZBOT_WHAT_TEXT = (
    "<b>Что умеет бот</b>\n\n"
    "Telegram-бот может помочь бизнесу:\n\n"
    "• принимать заявки 24/7\n"
    "• отвечать на частые вопросы\n"
    "• показывать услуги и цены\n"
    "• собирать контакты клиентов\n"
    "• записывать на услугу\n"
    "• передавать заявки владельцу\n"
    "• упрощать повторяющиеся действия\n\n"
    "Бот не заменяет бизнес.\n"
    "Он снимает рутину и упрощает общение с клиентом."
)

BIZBOT_FOR_WHOM_TEXT = (
    "<b>Для каких бизнесов подходит</b>\n\n"
    "Подходит для:\n\n"
    "• салонов красоты\n"
    "• спортивных клубов и секций\n"
    "• мастеров услуг\n"
    "• доставки\n"
    "• магазинов\n"
    "• локальных сервисов\n"
    "• консультационных проектов\n"
    "• агентств и небольших компаний\n\n"
    "Если задача повторяется каждый день, её часто можно упростить через бота."
)


def _escape(text: str) -> str:
    return html.escape((text or "").strip())


def _get_admin_chat_id() -> int:
    if not ADMIN_CHAT_ID:
        raise RuntimeError("ADMIN_CHAT_ID is missing in .env")
    return int(ADMIN_CHAT_ID)


async def _edit(callback: CallbackQuery, text: str, reply_markup=None) -> None:
    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(F.data == "bizbot:open")
async def bizbot_open(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await _edit(callback, BIZBOT_MAIN_TEXT, bizbot_main_kb())


@router.callback_query(F.data == "bizbot:what")
async def bizbot_what(callback: CallbackQuery) -> None:
    await _edit(callback, BIZBOT_WHAT_TEXT, bizbot_info_kb())


@router.callback_query(F.data == "bizbot:for_whom")
async def bizbot_for_whom(callback: CallbackQuery) -> None:
    await _edit(callback, BIZBOT_FOR_WHOM_TEXT, bizbot_info_kb())


@router.callback_query(F.data == "bizbot:lead_start")
async def bizbot_lead_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BizBotLead.business_name)

    if callback.message:
        await callback.message.edit_text(
            "<b>Шаг 1 из 4</b>\n\nКак называется ваш бизнес или проект?",
            reply_markup=bizbot_cancel_kb(),
            parse_mode="HTML",
        )
    await callback.answer()


@router.message(StateFilter(BizBotLead.business_name))
async def bizbot_business_name(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Введите название бизнеса или проекта.")
        return

    await state.update_data(business_name=text)
    await state.set_state(BizBotLead.business_type)

    await message.answer(
        "<b>Шаг 2 из 4</b>\n\nЧем вы занимаетесь? Коротко опишите ваш бизнес.",
        reply_markup=bizbot_cancel_kb(),
        parse_mode="HTML",
    )


@router.message(StateFilter(BizBotLead.business_type))
async def bizbot_business_type(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Коротко опишите, чем занимается ваш бизнес.")
        return

    await state.update_data(business_type=text)
    await state.set_state(BizBotLead.bot_task)

    await message.answer(
        "<b>Шаг 3 из 4</b>\n\n"
        "Что вы хотите, чтобы бот делал?\n\n"
        "Например: принимать заявки, записывать клиентов, отвечать на вопросы, "
        "показывать услуги, передавать обращения владельцу.",
        reply_markup=bizbot_cancel_kb(),
        parse_mode="HTML",
    )


@router.message(StateFilter(BizBotLead.bot_task))
async def bizbot_bot_task(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Опишите задачу бота.")
        return

    await state.update_data(bot_task=text)
    await state.set_state(BizBotLead.contact)

    await message.answer(
        "<b>Шаг 4 из 4</b>\n\nОставьте контакт для связи: Telegram, телефон или WhatsApp.",
        reply_markup=bizbot_cancel_kb(),
        parse_mode="HTML",
    )


@router.message(StateFilter(BizBotLead.contact))
async def bizbot_contact(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Оставьте контакт для связи.")
        return

    await state.update_data(contact=text)
    data = await state.get_data()
    await state.set_state(BizBotLead.confirm)

    summary = (
        "<b>Проверьте заявку</b>\n\n"
        f"<b>Бизнес / проект:</b> {_escape(data.get('business_name', ''))}\n"
        f"<b>Чем занимается:</b> {_escape(data.get('business_type', ''))}\n"
        f"<b>Задача бота:</b> {_escape(data.get('bot_task', ''))}\n"
        f"<b>Контакт:</b> {_escape(text)}"
    )

    await message.answer(
        summary,
        reply_markup=bizbot_confirm_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "bizbot:restart")
async def bizbot_restart(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BizBotLead.business_name)

    if callback.message:
        await callback.message.edit_text(
            "<b>Шаг 1 из 4</b>\n\nЗаполняем заново.\n\nКак называется ваш бизнес или проект?",
            reply_markup=bizbot_cancel_kb(),
            parse_mode="HTML",
        )
    await callback.answer("Заполняем заново")


@router.callback_query(F.data == "bizbot:cancel")
async def bizbot_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    if callback.message:
        await callback.message.edit_text(
            "Заявка отменена.",
            reply_markup=bizbot_done_kb(),
            parse_mode="HTML",
        )
    await callback.answer("Отменено")


@router.callback_query(F.data == "bizbot:confirm", StateFilter(BizBotLead.confirm))
async def bizbot_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    admin_text = (
        "<b>🤖 Новая заявка: Bot for Business</b>\n\n"
        f"<b>Название:</b> {_escape(data.get('business_name', ''))}\n"
        f"<b>Сфера:</b> {_escape(data.get('business_type', ''))}\n"
        f"<b>Задача:</b> {_escape(data.get('bot_task', ''))}\n"
        f"<b>Контакт:</b> {_escape(data.get('contact', ''))}\n\n"
        "<b>📍 Источник:</b> AliMind / Bot for Business"
    )

    try:
        await callback.bot.send_message(
            chat_id=_get_admin_chat_id(),
            text=admin_text,
            parse_mode="HTML",
            reply_markup=bizbot_admin_kb(),
        )

        await state.clear()

        if callback.message:
            await callback.message.edit_text(
                "Спасибо. Заявка отправлена.\n"
                "Мы посмотрим запрос и свяжемся с вами по указанному контакту.",
                reply_markup=bizbot_done_kb(),
                parse_mode="HTML",
            )

        await callback.answer("Заявка отправлена")

    except Exception as e:
        await callback.answer("Ошибка отправки", show_alert=True)
        if callback.message:
            await callback.message.answer(
                f"Не удалось отправить заявку.\nОшибка: <code>{html.escape(str(e))}</code>",
                parse_mode="HTML",
            )


@router.callback_query(F.data == "bizbot:to_menu")
async def bizbot_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await _send_start(callback.message)
    await callback.answer()
@router.callback_query(F.data == "bizlead:contact")
async def bizlead_contact(query: CallbackQuery):
    await query.answer("Контакт указан в заявке.", show_alert=False)


@router.callback_query(F.data == "bizlead:work")
async def bizlead_work(query: CallbackQuery):
    if not query.message:
        await query.answer()
        return

    base_text = query.message.html_text or query.message.text or ""
    if "Статус: 🧠 В работе" not in base_text:
        new_text = base_text + "\n\n<b>Статус:</b> 🧠 В работе"
    else:
        new_text = base_text

    await query.message.edit_text(
        new_text,
        reply_markup=bizbot_admin_kb(),
        parse_mode="HTML",
    )
    await query.answer("Заявка взята в работу")


@router.callback_query(F.data == "bizlead:archive")
async def bizlead_archive(query: CallbackQuery):
    if not query.message:
        await query.answer()
        return

    base_text = query.message.html_text or query.message.text or ""
    if "Статус: 📁 Архив" not in base_text:
        new_text = base_text + "\n\n<b>Статус:</b> 📁 Архив"
    else:
        new_text = base_text

    await query.message.edit_text(
        new_text,
        reply_markup=bizbot_admin_kb(),
        parse_mode="HTML",
    )
    await query.answer("Заявка отправлена в архив")