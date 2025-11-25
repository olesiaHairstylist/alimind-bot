# main.py
# Entry point for AliMind Bot

from bot.dispatcher import dp, bot
from aiogram import executor


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
