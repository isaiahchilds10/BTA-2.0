"""Pure offline test fixtures. No fabricated games enter production UI."""
import unittest
from datetime import datetime, timedelta, timezone
from data_sources.contracts import FeedStatus, SourceResult
from data_sources.schedules import ScheduleGame, SchedulePayload
from domain.contracts import Game, GameStatus, Sport
from ui.schedule_models import upcoming_games, readable_kickoff, source_caption

NOW = datetime(2026, 11, 7, 21, 0, tzinfo=timezone.utc)


def item(days=1, status=GameStatus.SCHEDULED, gid="NBA:111"):
    game = Game(gid, Sport.NBA, "2026-27", "NBA:1", "NBA:2", NOW + timedelta(days=days), status)
    return ScheduleGame(game, "Home", "Away", "https://cdn.nba.com/fixture", "NBA CDN")


def source(items, status=FeedStatus.DELAYED):
    if status == FeedStatus.UNAVAILABLE:
        return SourceResult(status=status, provider="test", limitation="no data")
    return SourceResult(status=status, provider="NBA CDN", retrieved_at=NOW,
                        value=SchedulePayload(tuple(items), 0, "test data"),
                        limitation="upstream update unknown")


class ScheduleUiDataTests(unittest.TestCase):
    def test_only_scheduled_future_games(self):
        s = source([item(1, GameStatus.SCHEDULED, "NBA:1"), item(-1, GameStatus.SCHEDULED, "NBA:2"),
                    item(2, GameStatus.UNKNOWN, "NBA:3"), item(3, GameStatus.CANCELLED, "NBA:4"),
                    item(4, GameStatus.FINAL, "NBA:5"), item(5, GameStatus.POSTPONED, "NBA:6")])
        self.assertEqual([x.game.game_id for x in upcoming_games(s, now=NOW)], ["NBA:1"])

    def test_sort_by_game_time(self):
        s = source([item(3, gid="NBA:3"), item(1, gid="NBA:1"), item(2, gid="NBA:2")])
        self.assertEqual([x.game.game_id for x in upcoming_games(s, now=NOW)], ["NBA:1", "NBA:2", "NBA:3"])

    def test_respects_time_window(self):
        s = source([item(1, gid="NBA:1"), item(14, gid="NBA:14")])
        self.assertEqual(len(upcoming_games(s, now=NOW, days=7)), 1)

    def test_result_limit(self):
        s = source([item(1, gid="NBA:1"), item(2, gid="NBA:2")])
        self.assertEqual(len(upcoming_games(s, now=NOW, limit=1)), 1)

    def test_unavailable_does_not_manufacture_games(self):
        self.assertEqual(upcoming_games(source([], FeedStatus.UNAVAILABLE), now=NOW), ())

    def test_empty_feed(self):
        self.assertEqual(upcoming_games(source([]), now=NOW), ())

    def test_naive_now_rejected(self):
        with self.assertRaises(ValueError):
            upcoming_games(source([]), now=datetime(2026, 11, 7))

    def test_bad_window_rejected(self):
        with self.assertRaises(ValueError):
            upcoming_games(source([]), now=NOW, days=0)

    def test_time_format_observes_dst(self):
        text = readable_kickoff(datetime(2026, 11, 8, 18, tzinfo=timezone.utc))
        self.assertIn("1:00 PM EST", text)

    def test_central_timezone(self):
        text = readable_kickoff(datetime(2026, 11, 8, 18, tzinfo=timezone.utc), "America/Chicago")
        self.assertIn("12:00 PM CST", text)

    def test_unverified_upstream_exposed(self):
        self.assertIn("unverified", source_caption(source([item()])))

    def test_not_real_feed(self):
        self.assertEqual(source([item()]).status, FeedStatus.DELAYED)


if __name__ == "__main__":
    unittest.main()
