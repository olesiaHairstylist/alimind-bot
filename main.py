import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from bot.core.loader import preload_catalog, DATA_PATH
from bot.core.registry import registry
from bot.core.search import search_by_name_or_description

from bot.handlers.start import router as start_router
from bot.handlers.menu import router as menu_router
from bot.handlers.search import router as search_router
from bot.handlers.help import router as help_router
from bot.handlers.favorites import router as favorites_router
from bot.handlers.recents import router as recents_router
from bot.handlers.emergency_contacts import router as emergency_contacts_router

from bot.handlers.planned_outages import router as planned_outages_router
from bot.handlers.migr_001_static import router as migr_001_static_router
from bot.handlers.on_duty_pharmacies import router as on_duty_pharmacies_router
from bot.handlers.partner_connect import router as partner_connect_router
from bot.handlers.partner_request import router as partner_request_router
from bot.handlers.request_audit import router as request_audit_router
from bot.handlers.fallback import router as fallback_router

from bot.handlers.admin_connect import router as admin_connect_router

from bot.handlers.admin_status import router as admin_status_router
from bot.handlers.admin_funnel import router as admin_funnel_router
from bot.handlers.admin_help import router as admin_help_router
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from bot.city_events.update import update_events_today
from bot.handlers.city_events import router as city_events_router
from bot.handlers.bizbot import router as bizbot_router
from bot.handlers.partner_apply import router as partner_apply_router



load_dotenv()



# formatter: пробуем HTML-safe, если нет — откатываемся на старый
try:
    from bot.core.formatter import format_object_card_html as _format_card
except Exception:
    from bot.core.formatter import format_object_card as _format_card


def _get_token() -> str:
    token = (
        os.getenv("BOT_TOKEN")
        or os.getenv("TELEGRAM_BOT_TOKEN")
        or os.getenv("TELEGRAM_TOKEN")
        or ""
    ).strip()
    if not token:
        raise RuntimeError(
            "BOT TOKEN is missing. Put BOT_TOKEN=... into .env (or TELEGRAM_BOT_TOKEN)."
        )
    return token


class TraceMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message) and event.text:
            st = None
            state = data.get("state")
            if state:
                try:
                    st = await state.get_state()
                except Exception:
                    st = "<?>"
            print(f"[TRACE] text={event.text!r} state={st} -> {handler.__module__}.{handler.__name__}")
        return await handler(event, data)


async def main() -> None:
    load_dotenv()

    token = _get_token()
    bot = Bot(token=token)

    # ✅ dp создаём РОВНО 1 раз
    dp = Dispatcher(storage=MemoryStorage())

    # ✅ TRACE: подключаем ДО polling
    dp.message.middleware(TraceMiddleware())


    # ===== REVISOR-GATE: WIRING (каждый router ровно 1 раз; fallback последний) =====
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(search_router)
    dp.include_router(help_router)
    dp.include_router(favorites_router)
    dp.include_router(recents_router)
    dp.include_router(partner_connect_router)
    dp.include_router(partner_request_router)
    dp.include_router(emergency_contacts_router)
    dp.include_router(request_audit_router)

    dp.include_router(migr_001_static_router)
    dp.include_router(planned_outages_router)
    dp.include_router(on_duty_pharmacies_router)
    dp.include_router(admin_connect_router)

    dp.include_router(admin_status_router)
    dp.include_router(admin_funnel_router)
    dp.include_router(admin_help_router)
    dp.include_router(city_events_router)
    dp.include_router(bizbot_router)
    dp.include_router(partner_apply_router)
    dp.include_router(fallback_router)  # строго последним

    # ===== BOOT + SMOKE =====
    me = await bot.get_me()
    print(f"[ME] id={me.id} username=@{me.username}")
    print("[BOOT OK] main.py started")

    await bot.set_my_commands(
        [
            BotCommand(command="admin_help", description="Админ-справка"),
        ],
        scope=BotCommandScopeDefault()
    )

    preload_catalog()
    print(f"[CATALOG] path: {DATA_PATH}")
    print(f"[CATALOG] Loaded objects: {len(registry)}")

    try:
        first = next(iter(registry.values()))
        preview = _format_card(first)
        print("[CARD PREVIEW] OK")
        print(preview[:200].replace("\n", " ") + ("..." if len(preview) > 200 else ""))
    except StopIteration:
        print("[CARD PREVIEW] SKIP (registry empty)")
    except Exception as e:
        print(f"[CARD PREVIEW] FAIL: {e}")

    try:
        hits = search_by_name_or_description("alanya")
        print(f"[SEARCH] hits: {len(hits)}")
    except Exception as e:
        print(f"[SEARCH] FAIL: {e}")

    # ===== TRANSPORT FIX: webhook -> polling =====
    info = await bot.get_webhook_info()
    print(f"[WEBHOOK] url={info.url!r} pending={info.pending_update_count} last_error={info.last_error_message!r}")

    await bot.delete_webhook(drop_pending_updates=True)
    print("[WEBHOOK] deleted (drop_pending_updates=True)")
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Istanbul"))

    # каждый день, 06:05 утра (пример). Время выберите любое “тихое”.
    scheduler.add_job(update_events_today, CronTrigger(hour=6, minute=5))

    scheduler.start()

    # сразу обновить при старте (без UI, просто заполнить файлы)
    await update_events_today()

    # ✅ polling запускаем РОВНО 1 раз
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
