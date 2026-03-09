from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def partner_ack_kb(request_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏳ В работе", callback_data=f"pack:work:{request_id}"),
            InlineKeyboardButton(text="✅ Ответил клиенту", callback_data=f"pack:replied:{request_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Не могу принять", callback_data=f"pack:decline:{request_id}"),
        ]
    ])
