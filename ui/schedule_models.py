"""Pure, testable schedule filtering and formatting for BTA 2.0.

Only source-observed data is accepted. In particular a retrieved schedule is
not a live score and does not establish player status, odds, or BTA grades.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from data_sources.contracts import FeedStatus, SourceResult
from data_sources.schedules import ScheduleGame, SchedulePayload
from domain.contracts import GameStatus, Sport

ET = ZoneInfo("America/New_York")
CT = ZoneInfo("America/Chicago")

SPORT_LABELS = {
    Sport.NBA: "NBA",
    Sport.NFL: "NFL",
    Sport.COLLEGE_FOOTBALL: "College Football",
}


def upcoming_games(
    source: SourceResult[SchedulePayload], *, now: datetime, days: int = 14,
    limit: int = 20,
) -> tuple[ScheduleGame, ...]:
    """Only source-identified *scheduled future* games, never inferred fixtures.

    Postponed/cancelled/final/unknown status cannot be displayed as upcoming.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone aware")
    if days < 1 or days > 90:
        raise ValueError("days must be between 1 and 90")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    if source.status == FeedStatus.UNAVAILABLE or source.value is None:
        return ()
    ending = now.astimezone(timezone.utc) + timedelta(days=days)
    eligible = [
        g for g in source.value.games
        if g.game.status == GameStatus.SCHEDULED
        and now <= g.game.scheduled_start < ending
    ]
    return tuple(sorted(eligible, key=lambda g: (g.game.scheduled_start, g.game.game_id))[:limit])


def readable_kickoff(start: datetime, tz: str = "America/New_York") -> str:
    if start.tzinfo is None or start.utcoffset() is None:
        raise ValueError("kickoff must be timezone aware")
    if tz not in ("America/New_York", "America/Chicago", "UTC"):
        raise ValueError("unsupported timezone")
    local = start.astimezone(ZoneInfo(tz))
    # %Z prints EST/EDT, CST/CDT, or UTC so DST isn't hidden.
    return f"{local:%a, %b} {local.day} · {local:%I:%M %p %Z}".replace("· 0", "· ")


def source_caption(source: SourceResult[SchedulePayload]) -> str:
    checked = (source.retrieved_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
               if source.retrieved_at else "unknown")
    provider_updated = (source.provider_updated_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                        if source.provider_updated_at else "unverified")
    return f"Source: {source.provider} | Retrieved: {checked} | Upstream updated: {provider_updated}"
