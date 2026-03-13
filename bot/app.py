from aiogram import Dispatcher

from bot.handlers.start import router as start_router
from bot.handlers.menu import router as menu_router
from bot.handlers.on_duty_pharmacies import router as on_duty_pharmacies_router
from bot.handlers.planned_outages import router as planned_outages_router
from bot.handlers.city_today import router as city_today_router
def build_dispatcher() -> Dispatcher:

    dp = Dispatcher()

    dp.include_router(start_router)
    print("[WIRING] start_router included")

    dp.include_router(menu_router)
    print("[WIRING] menu_router included")

    dp.include_router(on_duty_pharmacies_router)
    print("[WIRING] on_duty_pharmacies_router included")

    dp.include_router(planned_outages_router)
    print("[WIRING] planned_outages_router included")
    dp.include_router(city_today_router)
    print("[WIRING] city_today_router included")
    return dp