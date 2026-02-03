# bot/keyboards/main.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Госуслуги"), KeyboardButton(text="Медицина")],
            [KeyboardButton(text="Beauty"), KeyboardButton(text="Спорт")],
            [KeyboardButton(text="Трансфер")],
        ],
        resize_keyboard=True
    )
