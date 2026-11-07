"""Offline contract tests. Test fixtures do NOT represent real sports observations."""

import unittest
from datetime import datetime, timezone
from decimal import Decimal

from data_sources.contracts import FeedStatus, SourceResult
from domain.contracts import (
    ClaimState, Evidence, Game, MarketVerification, Selection,
    SelectionSide, SourceKind, Sport,
)

UTC = timezone.utc


class TestSourceGuardrails(unittest.TestCase):
    def test_game_must_have_timezone_and_distinct_teams(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            Game("fixture-1", Sport.NFL, "TEST", "a", "b", datetime(2026, 1, 1))
        with self.assertRaisesRegex(ValueError, "different"):
            Game("fixture-1", Sport.NFL, "TEST", "a", "a", datetime(2026, 1, 1, tzinfo=UTC))

    def test_reporting_cannot_be_official_confirmation(self):
        with self.assertRaisesRegex(ValueError, "OFFICIALLY_CONFIRMED"):
            Evidence(
                "test-evidence-1", "fixture-1", "test claim", "Test reporter",
                "https://example.com/report", SourceKind.CREDIBLE_REPORTING,
                ClaimState.OFFICIALLY_CONFIRMED,
                retrieved_at=datetime(2026, 1, 1, tzinfo=UTC),
            )

    def test_selection_defaults_to_unverified_line(self):
        selection = Selection(
            "test-leg-1", "fixture-1", Sport.NBA, "POINTS", SelectionSide.OVER,
            Decimal("20.5"), "FULL_GAME",
        )
        self.assertEqual(selection.market_verification, MarketVerification.USER_ENTERED_MARKET_NOT_VERIFIED)
        self.assertEqual(selection.line, Decimal("20.5"))
        self.assertIsNone(selection.offer_source_url)

    def test_verified_offer_needs_source_and_time(self):
        with self.assertRaisesRegex(ValueError, "VERIFIED_OFFER requires"):
            Selection(
                "test-leg-1", "fixture-1", Sport.NBA, "POINTS",
                SelectionSide.OVER, Decimal("20.5"), "FULL_GAME",
                market_verification=MarketVerification.VERIFIED_OFFER,
            )

    def test_current_feed_requires_real_value_and_timestamps(self):
        with self.assertRaisesRegex(ValueError, "CURRENT requires"):
            SourceResult(status=FeedStatus.CURRENT, provider="test-provider")
        result = SourceResult(status=FeedStatus.UNAVAILABLE, provider="test-provider")
        self.assertIsNone(result.value)

    def test_delayed_feed_requires_last_known_data(self):
        with self.assertRaisesRegex(ValueError, "DELAYED requires"):
            SourceResult(status=FeedStatus.DELAYED, provider="test-provider")

    def test_unavailable_feed_cannot_carry_data(self):
        with self.assertRaisesRegex(ValueError, "UNAVAILABLE"):
            SourceResult(status=FeedStatus.UNAVAILABLE, provider="test-provider", value="not real")


if __name__ == "__main__":
    unittest.main()
