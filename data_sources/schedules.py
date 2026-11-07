"""Independent schedule candidates for NBA, NFL and college football.

Important: successful HTTP retrieval does not prove source freshness. The
Phase-1 test intentionally reports DELAYED when upstream update time is not
verified; it cannot certify live games, lines, outcomes or injury statuses.
No synthetic fixtures can enter a returned production schedule.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import StringIO
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
from typing import Callable
import csv
import os

from data_sources.contracts import FeedStatus, SourceResult
from data_sources.http_client import ProviderFetchError, fetch_bytes, fetch_json
from domain.contracts import Game, GameStatus, Sport

NBA_URL = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
NFL_URL = "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv"
CFB_URL = "https://api.collegefootballdata.com/games"
EASTERN = ZoneInfo("America/New_York")


@dataclass(frozen=True)
class ScheduleGame:
    game: Game
    home_label: str
    away_label: str
    source_url: str
    provider: str


@dataclass(frozen=True)
class SchedulePayload:
    games: tuple[ScheduleGame, ...]
    rows_skipped: int
    coverage_note: str


def _iso(raw: object) -> datetime:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("No source date/time")
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("No explicit timezone in source date/time")
    return dt.astimezone(timezone.utc)


def _id(value: object) -> str:
    if value is None or str(value).strip() == "":
        raise ValueError("Missing provider identity")
    return str(value)


def _text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Missing team name")
    return value.strip()


def _nba_status(row: dict) -> GameStatus:
    description = str(row.get("gameStatusText", "")).lower()
    if "postpon" in description:
        return GameStatus.POSTPONED
    if "cancel" in description:
        return GameStatus.CANCELLED
    value = row.get("gameStatus")
    # The CDN convention is 1 scheduled, 2 in progress, 3 final.
    return {1: GameStatus.SCHEDULED, 2: GameStatus.LIVE, 3: GameStatus.FINAL}.get(value, GameStatus.UNKNOWN)


def parse_nba(data: object) -> SchedulePayload:
    if not isinstance(data, dict) or not isinstance(data.get("leagueSchedule"), dict):
        raise ValueError("NBA schema missing leagueSchedule")
    league = data["leagueSchedule"]
    if not isinstance(league.get("gameDates"), list) or not league.get("seasonYear"):
        raise ValueError("NBA schedule is missing its season or gameDates")
    season = _text(league["seasonYear"])
    result, skipped, seen = [], 0, set()
    for day in league["gameDates"]:
        if not isinstance(day, dict) or not isinstance(day.get("games"), list):
            skipped += 1
            continue
        for row in day["games"]:
            try:
                if not isinstance(row, dict):
                    raise ValueError("Non-object NBA game")
                gid = _id(row["gameId"])
                home, away = row["homeTeam"], row["awayTeam"]
                h_id, a_id = _id(home["teamId"]), _id(away["teamId"])
                h_label = _text(home.get("teamName"))
                a_label = _text(away.get("teamName"))
                start = _iso(row["gameDateTimeUTC"])
                if gid in seen:
                    skipped += 1
                    continue
                game = Game("NBA:"+gid, Sport.NBA, season,
                            "NBA:"+h_id, "NBA:"+a_id, start, _nba_status(row))
                result.append(ScheduleGame(game, h_label, a_label, NBA_URL, "NBA CDN"))
                seen.add(gid)
            except (KeyError, TypeError, ValueError):
                skipped += 1
    if not result and skipped:
        raise ValueError("NBA games exist but none could be safely parsed")
    return SchedulePayload(tuple(sorted(result, key=lambda item: item.game.scheduled_start)), skipped,
                           "Official NBA CDN schedule; exact upstream updated-at time is not independently verified.")


def _nfl_start(row: dict) -> datetime:
    # nflverse documents gameday and gametime as ET. Never guess a missing time.
    day = _text(row.get("gameday"))
    hm = _text(row.get("gametime"))
    if len(hm.split(":")) != 2:
        raise ValueError("Unexpected kickoff time")
    return datetime.fromisoformat(day + "T" + hm).replace(tzinfo=EASTERN).astimezone(timezone.utc)


def parse_nfl(csv_text: str, *, season: int, now: datetime) -> SchedulePayload:
    if not isinstance(csv_text, str):
        raise ValueError("NFL CSV not text")
    reader = csv.DictReader(StringIO(csv_text))
    required = {"game_id", "season", "gameday", "gametime", "away_team", "home_team", "away_score", "home_score"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        raise ValueError("NFL CSV missing required columns")
    result, skipped, seen = [], 0, set()
    for row in reader:
        if row.get("season") != str(season):
            continue
        try:
            gid = _id(row["game_id"])
            home, away = _text(row["home_team"]), _text(row["away_team"])
            start = _nfl_start(row)
            if gid in seen:
                skipped += 1
                continue
            if row.get("home_score", "").strip() and row.get("away_score", "").strip() and start + timedelta(hours=6) < now:
                status = GameStatus.FINAL
            elif start > now:
                status = GameStatus.SCHEDULED
            else:
                status = GameStatus.UNKNOWN  # no verified live status from this CSV
            game = Game("NFL:"+gid, Sport.NFL, str(season),
                        "NFL:"+home, "NFL:"+away, start, status)
            result.append(ScheduleGame(game, home, away, NFL_URL, "nflverse / nfldata"))
            seen.add(gid)
        except (ValueError, KeyError, TypeError, AttributeError):
            skipped += 1
    if not result:
        raise ValueError("No parseable NFL games for requested season")
    return SchedulePayload(tuple(sorted(result, key=lambda item: item.game.scheduled_start)), skipped,
                           "Community-maintained NFL schedule; not an official real-time NFL status feed.")


def parse_cfb(data: object, *, year: int, now: datetime) -> SchedulePayload:
    if not isinstance(data, list):
        raise ValueError("CFBD /games did not return a list")
    result, skipped, seen = [], 0, set()
    for row in data:
        try:
            if not isinstance(row, dict) or row.get("season") != year:
                raise ValueError("Wrong season or malformed game")
            if row.get("startTimeTBD") is True:
                raise ValueError("Kickoff time not verified")
            gid = _id(row["id"])
            home, away = _text(row["homeTeam"]), _text(row["awayTeam"])
            start = _iso(row["startDate"])
            h_id, a_id = _id(row["homeId"]), _id(row["awayId"])
            if gid in seen:
                skipped += 1
                continue
            if row.get("completed") is True:
                status = GameStatus.FINAL
            elif start > now:
                status = GameStatus.SCHEDULED
            else:
                status = GameStatus.UNKNOWN
            game = Game("CFB:"+gid, Sport.COLLEGE_FOOTBALL, str(year),
                        "CFB:"+h_id, "CFB:"+a_id, start, status)
            result.append(ScheduleGame(game, home, away, CFB_URL, "CollegeFootballData"))
            seen.add(gid)
        except (KeyError, TypeError, ValueError):
            skipped += 1
    if data and not result:
        raise ValueError("CFBD returned games but no safely parseable records")
    return SchedulePayload(tuple(sorted(result, key=lambda item: item.game.scheduled_start)), skipped,
                           "CFBD FBS-classification regular season only; exact source update age and live status not verified.")


def _result(provider: str, value: SchedulePayload, retrieved_at: datetime) -> SourceResult[SchedulePayload]:
    # Source update time is NOT provided/verified. In the established BTA
    # SourceResult contract CURRENT requires an independently grounded timestamp.
    return SourceResult(status=FeedStatus.DELAYED, provider=provider,
                        retrieved_at=retrieved_at, provider_updated_at=None,
                        value=value,
                        limitation="Source update time unverified; retrieval succeeded but CURRENT is not certified.")


def _unavailable(provider: str, problem: str) -> SourceResult[SchedulePayload]:
    return SourceResult(status=FeedStatus.UNAVAILABLE, provider=provider, limitation=problem)


def nba_schedule(*, fetch: Callable[[str], object] = fetch_json) -> SourceResult[SchedulePayload]:
    try:
        payload = parse_nba(fetch(NBA_URL))
        return _result("NBA CDN", payload, datetime.now(timezone.utc))
    except (ProviderFetchError, ValueError, TypeError) as exc:
        return _unavailable("NBA CDN", str(exc))


def nfl_schedule(*, season: int, fetch: Callable[[str], bytes] = fetch_bytes,
                 now: datetime | None = None) -> SourceResult[SchedulePayload]:
    now = now or datetime.now(timezone.utc)
    try:
        payload = parse_nfl(fetch(NFL_URL).decode("utf-8-sig"), season=season, now=now)
        return _result("nflverse / nfldata", payload, datetime.now(timezone.utc))
    except (ProviderFetchError, ValueError, UnicodeDecodeError, TypeError) as exc:
        return _unavailable("nflverse / nfldata", str(exc))


def cfb_schedule(*, year: int, api_key: str | None = None,
                 fetch: Callable[..., object] = fetch_json,
                 now: datetime | None = None) -> SourceResult[SchedulePayload]:
    key = api_key if api_key is not None else os.environ.get("CFBD_API_KEY", "")
    if not key or not key.strip():
        return _unavailable("CollegeFootballData", "CFBD_API_KEY not configured (free key required).")
    now = now or datetime.now(timezone.utc)
    url = CFB_URL + "?" + urlencode({"year": year, "seasonType": "regular", "classification": "fbs"})
    try:
        payload = parse_cfb(fetch(url, bearer_token=key), year=year, now=now)
        return _result("CollegeFootballData", payload, datetime.now(timezone.utc))
    except (ProviderFetchError, ValueError, TypeError) as exc:
        return _unavailable("CollegeFootballData", str(exc))


def season_for_football(at: datetime) -> int:
    """Season calendar label; Jan-Feb belong to the preceding fall season."""
    return at.year - 1 if at.month < 3 else at.year
