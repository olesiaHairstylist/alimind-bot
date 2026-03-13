from __future__ import annotations

from bot.city_events.scheduler import run_city_events_update


def main() -> None:
    run_city_events_update()


if __name__ == "__main__":
    main()