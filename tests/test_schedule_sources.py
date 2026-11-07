"""Strictly synthetic parser tests. Not proof of real feeds or live freshness."""
import unittest
from datetime import datetime, timezone
from data_sources.contracts import FeedStatus
from data_sources.schedules import (
    NBA_URL, NFL_URL, CFB_URL, _iso, _nfl_start, parse_nba, parse_nfl, parse_cfb,
    nba_schedule, nfl_schedule, cfb_schedule, season_for_football
)
from domain.contracts import GameStatus, Sport

NOW = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)


def nba_fixture():
    return {"leagueSchedule": {"seasonYear": "2026-27", "gameDates": [{"games": [{
        "gameId": "0022600001", "gameDateTimeUTC": "2026-11-09T00:00:00Z", "gameStatus": 1,
        "homeTeam": {"teamId": 11, "teamName": "Example Home"},
        "awayTeam": {"teamId": 12, "teamName": "Example Away"}
    }]}]}}


def nfl_fixture():
    return "game_id,season,gameday,gametime,away_team,away_score,home_team,home_score\n2026_10_A_B,2026,2026-11-08,13:00,A,,B,\n"


def cfb_fixture():
    return [{"id": 1234567, "season": 2026, "homeId": 1, "awayId": 2,
             "homeTeam": "Example College Home", "awayTeam": "Example College Away",
             "startDate": "2026-11-08T20:00:00Z", "startTimeTBD": False, "completed": False}]


class ParseContracts(unittest.TestCase):
    def test_nba_provenance(self):
        payload = parse_nba(nba_fixture())
        self.assertEqual(len(payload.games), 1)
        game = payload.games[0]
        self.assertEqual(game.game.sport, Sport.NBA)
        self.assertEqual(game.game.game_id, "NBA:0022600001")
        self.assertEqual(game.game.status, GameStatus.SCHEDULED)
        self.assertEqual(game.source_url, NBA_URL)

    def test_nba_duplicates_ignored(self):
        f = nba_fixture()
        f["leagueSchedule"]["gameDates"][0]["games"].append(f["leagueSchedule"]["gameDates"][0]["games"][0].copy())
        p = parse_nba(f)
        self.assertEqual(len(p.games), 1)
        self.assertEqual(p.rows_skipped, 1)

    def test_nba_no_missing_team_or_time_fabrication(self):
        f = nba_fixture()
        f["leagueSchedule"]["gameDates"][0]["games"][0]["gameDateTimeUTC"] = None
        with self.assertRaises(ValueError):
            parse_nba(f)

    def test_nba_wrong_schema_rejected(self):
        with self.assertRaises(ValueError):
            parse_nba({"leagueSchedule": {"seasonYear":"2026-27"}})

    def test_nba_postponement(self):
        f = nba_fixture()
        f["leagueSchedule"]["gameDates"][0]["games"][0]["gameStatusText"] = "Postponed"
        self.assertEqual(parse_nba(f).games[0].game.status, GameStatus.POSTPONED)

    def test_nfl_eastern_time_conversion_after_dst(self):
        p = parse_nfl(nfl_fixture(), season=2026, now=NOW)
        self.assertEqual(p.games[0].game.scheduled_start.hour, 18)
        self.assertEqual(p.games[0].game.scheduled_start.date().isoformat(), "2026-11-08")
        self.assertEqual(p.games[0].game.status, GameStatus.SCHEDULED)

    def test_nfl_no_missing_time_fabrication(self):
        csv = nfl_fixture().replace("13:00", "")
        with self.assertRaises(ValueError):
            parse_nfl(csv, season=2026, now=NOW)

    def test_nfl_no_fake_live_game_status(self):
        csv = nfl_fixture().replace("2026-11-08", "2026-11-01")
        p = parse_nfl(csv, season=2026, now=NOW)
        self.assertEqual(p.games[0].game.status, GameStatus.UNKNOWN)

    def test_nfl_different_season_is_unavailable(self):
        with self.assertRaises(ValueError):
            parse_nfl(nfl_fixture(), season=2025, now=NOW)

    def test_cfb_id_and_timezone(self):
        p = parse_cfb(cfb_fixture(), year=2026, now=NOW)
        self.assertEqual(p.games[0].game.game_id, "CFB:1234567")
        self.assertEqual(p.games[0].game.scheduled_start.utcoffset().total_seconds(), 0)
        self.assertEqual(p.games[0].game.status, GameStatus.SCHEDULED)

    def test_cfb_unknown_kickoff_excluded(self):
        data = cfb_fixture()
        data[0]["startTimeTBD"] = True
        with self.assertRaises(ValueError):
            parse_cfb(data, year=2026, now=NOW)

    def test_cfb_no_made_up_live_status(self):
        data = cfb_fixture()
        data[0]["startDate"] = "2026-11-01T00:00:00Z"
        self.assertEqual(parse_cfb(data, year=2026, now=NOW).games[0].game.status, GameStatus.UNKNOWN)

    def test_cfb_empty_list_supported(self):
        self.assertEqual(parse_cfb([], year=2026, now=NOW).games, ())

    def test_cfb_wrong_schema_rejected(self):
        with self.assertRaises(ValueError):
            parse_cfb({"games": []}, year=2026, now=NOW)

    def test_naive_datetime_rejected(self):
        with self.assertRaises(ValueError):
            _iso("2026-11-08T13:00:00")

    def test_nfl_season_boundary(self):
        self.assertEqual(season_for_football(datetime(2027, 1, 3, tzinfo=timezone.utc)), 2026)
        self.assertEqual(season_for_football(NOW), 2026)


class AdapterContracts(unittest.TestCase):
    def test_nba_observed_without_upstream_timestamp_is_not_current(self):
        result = nba_schedule(fetch=lambda url: nba_fixture())
        self.assertEqual(result.status, FeedStatus.DELAYED)
        self.assertIsNone(result.provider_updated_at)
        self.assertEqual(len(result.value.games), 1)

    def test_nba_failed_source_is_unavailable(self):
        def failed(_):
            raise ValueError("Changed upstream JSON schema")
        result = nba_schedule(fetch=failed)
        self.assertEqual(result.status, FeedStatus.UNAVAILABLE)
        self.assertIsNone(result.value)

    def test_nfl_observed_without_upstream_timestamp_is_not_current(self):
        result = nfl_schedule(season=2026, fetch=lambda url: nfl_fixture().encode(), now=NOW)
        self.assertEqual(result.status, FeedStatus.DELAYED)
        self.assertIsNone(result.provider_updated_at)

    def test_cfb_without_key_does_not_fetch(self):
        def forbid(*args, **kw):
            raise AssertionError("Must not fetch without key")
        result = cfb_schedule(year=2026, api_key="", fetch=forbid)
        self.assertEqual(result.status, FeedStatus.UNAVAILABLE)
        self.assertIn("CFBD_API_KEY", result.limitation)

    def test_cfb_key_stays_out_of_result(self):
        def fake_fetch(url, *, bearer_token):
            self.assertEqual(bearer_token, "SECRET_NOT_FOR_LOGS")
            self.assertIn("classification=fbs", url)
            self.assertIn("seasonType=regular", url)
            return cfb_fixture()
        result = cfb_schedule(year=2026, api_key="SECRET_NOT_FOR_LOGS", fetch=fake_fetch, now=NOW)
        self.assertEqual(result.status, FeedStatus.DELAYED)
        self.assertNotIn("SECRET_NOT_FOR_LOGS", str(result))
        self.assertEqual(result.value.games[0].game.status, GameStatus.SCHEDULED)

    def test_cfb_unauthorized_gives_no_fake_schedule(self):
        from data_sources.http_client import ProviderFetchError
        def fake_fetch(url, *, bearer_token):
            raise ProviderFetchError("HTTP 401")
        result = cfb_schedule(year=2026, api_key="foo", fetch=fake_fetch, now=NOW)
        self.assertEqual(result.status, FeedStatus.UNAVAILABLE)
        self.assertIsNone(result.value)

if __name__ == "__main__":
    unittest.main()
