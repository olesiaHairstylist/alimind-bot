# bot/app.py

from aiogram import Dispatcher

from bot.handlers.start import router as start_router
from bot.handlers.menu import router as menu_router

def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    dp.include_router(start_router)
    print("[WIRING] start_router included")

    dp.include_router(menu_router)
    print("[WIRING] menu_router included")

    return dp
