"""Real-data smoke check. No fabricated fixtures, no sportsbook markets.

Usage:
    python -m scripts.check_schedules --sport nba nfl
    CFBD_API_KEY=... python -m scripts.check_schedules --sport nba nfl cfb
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from data_sources.contracts import FeedStatus
from data_sources.schedules import nba_schedule, nfl_schedule, cfb_schedule, season_for_football


def main() -> int:
    parser = argparse.ArgumentParser(description="Test public sports schedule adapters")
    parser.add_argument("--sport", nargs="+", choices=["nba", "nfl", "cfb"], default=["nba", "nfl", "cfb"])
    parser.add_argument("--days", type=int, default=21)
    args = parser.parse_args()
    if args.days < 1 or args.days > 120:
        parser.error("--days must be 1..120")
    now = datetime.now(timezone.utc)
    fall_year = season_for_football(now)
    funcs = {"nba": lambda: nba_schedule(), "nfl": lambda: nfl_schedule(season=fall_year),
             "cfb": lambda: cfb_schedule(year=fall_year)}
    fail = False
    for sport in list(dict.fromkeys(args.sport)):
        result = funcs[sport]()
        print(f"\n{sport.upper()} — {result.status.value} — {result.provider}")
        print("Checked at (UTC):", result.retrieved_at.isoformat() if result.retrieved_at else "not available")
        print("Upstream updated at:", result.provider_updated_at.isoformat() if result.provider_updated_at else "unknown")
        if result.limitation:
            print("Coverage limitation:", result.limitation)
        if result.status == FeedStatus.UNAVAILABLE or not result.value:
            fail = True
            continue
        print("Total schedule rows:", len(result.value.games), "| Rows skipped:", result.value.rows_skipped)
        print("Notes:", result.value.coverage_note)
        upcoming = [item for item in result.value.games if now <= item.game.scheduled_start < now + timedelta(days=args.days)]
        print(f"Upcoming in {args.days} days:", len(upcoming))
        for item in upcoming[:8]:
            print(" ", item.game.scheduled_start.strftime("%Y-%m-%d %H:%M UTC"),
                  f"{item.away_label} at {item.home_label}", item.game.game_id, item.game.status.value)
        if not upcoming:
            print("No matching upcoming games in window (not an error by itself).")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
