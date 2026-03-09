from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def bizbot_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Что умеет бот", callback_data="bizbot:what")],
            [InlineKeyboardButton(text="Для каких бизнесов", callback_data="bizbot:for_whom")],
            [InlineKeyboardButton(text="Оставить заявку", callback_data="bizbot:lead_start")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="bizbot:to_menu")],
        ]
    )


def bizbot_info_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оставить заявку", callback_data="bizbot:lead_start")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="bizbot:open")],
        ]
    )


def bizbot_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="bizbot:cancel")]
        ]
    )


def bizbot_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить", callback_data="bizbot:confirm")],
            [InlineKeyboardButton(text="✏️ Заполнить заново", callback_data="bizbot:restart")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="bizbot:cancel")],
        ]
    )


def bizbot_done_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В меню", callback_data="bizbot:to_menu")]
        ]
    )
def bizbot_admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📞 Связаться", callback_data="bizlead:contact"),
                InlineKeyboardButton(text="🧠 В работу", callback_data="bizlead:work"),
                InlineKeyboardButton(text="📁 Архив", callback_data="bizlead:archive"),
            ]
        ]
    )