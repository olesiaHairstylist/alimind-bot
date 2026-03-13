from __future__ import annotations

from bot.city_events.pharmacies.updater import update_pharmacies_today
from bot.city_events.outages.updater import update_outages_today


def run_city_events_update() -> None:
    print("[CITY_EVENTS] update started")

    try:
        update_pharmacies_today()
        print("[CITY_EVENTS] pharmacies updated")
    except Exception as e:
        print(f"[CITY_EVENTS] pharmacies update failed: {e}")

    try:
        update_outages_today()
        print("[CITY_EVENTS] outages updated")
    except Exception as e:
        print(f"[CITY_EVENTS] outages update failed: {e}")

    print("[CITY_EVENTS] update finished")