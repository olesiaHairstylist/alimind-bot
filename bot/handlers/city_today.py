from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.handlers.start import build_main_menu_kb
from bot.city_events.storage import (
    PHARMACIES_FILE,
    OUTAGES_FILE,
    load_today_payload,
)
from bot.city_events.render import render_pharmacies, render_outages

router = Router()

CITY_TODAY_CB = "city_today"
CITY_TODAY_PHARM_CB = "city_today:pharmacies"
CITY_TODAY_OUTAGES_CB = "city_today:outages"
CITY_TODAY_WATER_CB = "city_today:water"
CITY_TODAY_BACK_CB = "city_today:back"
CITY_TODAY_MAIN_MENU_CB = "city_today:main_menu"


def _city_today_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💊 Дежурные аптеки", callback_data=CITY_TODAY_PHARM_CB)
    b.button(text="⚡ Отключения электричества", callback_data=CITY_TODAY_OUTAGES_CB)
    b.button(text="🚰 Отключения воды", callback_data=CITY_TODAY_WATER_CB)
    b.button(text="⬅️ Назад в меню", callback_data=CITY_TODAY_MAIN_MENU_CB)
    b.adjust(1)
    return b.as_markup()


def _city_today_back_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ К событиям города", callback_data=CITY_TODAY_BACK_CB)
    b.button(text="🏠 В главное меню", callback_data=CITY_TODAY_MAIN_MENU_CB)

    b.adjust(1)
    return b.as_markup()


def _render_city_today_menu_text() -> str:
    return (
        "🌆 События города\n\n"
        "Выберите раздел:"
    )


@router.message(Command("city_today"))
async def city_today_cmd(message: Message) -> None:
    await message.answer(
        _render_city_today_menu_text(),
        reply_markup=_city_today_menu_kb(),
        parse_mode=None,
    )


@router.callback_query(lambda c: c.data == CITY_TODAY_CB)
async def city_today_open_cb(call: CallbackQuery) -> None:
    await call.answer()

    try:
        await call.message.edit_text(
            _render_city_today_menu_text(),
            reply_markup=_city_today_menu_kb(),
            parse_mode=None,
        )
    except Exception:
        await call.message.answer(
            _render_city_today_menu_text(),
            reply_markup=_city_today_menu_kb(),
            parse_mode=None,
        )


@router.callback_query(lambda c: c.data == CITY_TODAY_BACK_CB)
async def city_today_back_cb(call: CallbackQuery) -> None:
    await call.answer()

    try:
        await call.message.edit_text(
            _render_city_today_menu_text(),
            reply_markup=_city_today_menu_kb(),
            parse_mode=None,
        )
    except Exception:
        await call.message.answer(
            _render_city_today_menu_text(),
            reply_markup=_city_today_menu_kb(),
            parse_mode=None,
        )


@router.callback_query(lambda c: c.data == CITY_TODAY_MAIN_MENU_CB)
async def city_today_main_menu_cb(call: CallbackQuery) -> None:
    await call.answer()

    try:
        await call.message.edit_text(
            "Выберите раздел:\nℹ️ Если нужна справка — напишите /help",
            reply_markup=build_main_menu_kb(),
            parse_mode=None,
        )
    except Exception:
        await call.message.answer(
            "Выберите раздел:\nℹ️ Если нужна справка — напишите /help",
            reply_markup=build_main_menu_kb(),
            parse_mode=None,
        )


@router.callback_query(lambda c: c.data == CITY_TODAY_PHARM_CB)
async def city_today_pharmacies_cb(call: CallbackQuery) -> None:
    payload = load_today_payload(PHARMACIES_FILE)
    text = render_pharmacies(payload["items"], payload["updated_at"])

    await call.answer()

    try:
        await call.message.edit_text(
            text,
            reply_markup=_city_today_back_kb(),
            parse_mode=None,
        )
    except Exception:
        await call.message.answer(
            text,
            reply_markup=_city_today_back_kb(),
            parse_mode=None,
        )


@router.callback_query(lambda c: c.data == CITY_TODAY_OUTAGES_CB)
async def city_today_outages_cb(call: CallbackQuery) -> None:
    payload = load_today_payload(OUTAGES_FILE)
    text = render_outages(payload["items"], payload["updated_at"])

    await call.answer()

    try:
        await call.message.edit_text(
            text,
            reply_markup=_city_today_back_kb(),
            parse_mode=None,
        )
    except Exception:
        await call.message.answer(
            text,
            reply_markup=_city_today_back_kb(),
            parse_mode=None,
        )
@router.callback_query(lambda c: c.data == CITY_TODAY_WATER_CB)
async def city_today_water_cb(call: CallbackQuery):

    text = (
        "🚰 Отключения воды\n\n"
        "На сегодня данных нет.\n"
        "Информация публикуется по мере поступления "
        "от официальных служб."
    )

    await call.answer()

    try:
        await call.message.edit_text(
            text,
            reply_markup=_city_today_back_kb(),
            parse_mode=None,
        )
    except Exception:
        await call.message.answer(
            text,
            reply_markup=_city_today_back_kb(),
            parse_mode=None,
        )