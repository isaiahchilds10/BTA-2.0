"""Phase-0 immutable contracts. No sports data, grades, or odds are generated here.

Design source: BTA 2.0 Final Master Specification (2026-11-07),
sections 1, 4, 8, 13 and 19. This module deliberately DOES NOT compute BTA grades,
hitting probabilities, odds, injuries, or match outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from urllib.parse import urlparse


class Sport(str, Enum):
    NBA = "NBA"
    NFL = "NFL"
    COLLEGE_FOOTBALL = "COLLEGE_FOOTBALL"


class GameStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FINAL = "FINAL"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"


class SourceKind(str, Enum):
    OFFICIAL = "OFFICIAL"
    CREDIBLE_REPORTING = "CREDIBLE_REPORTING"
    OTHER = "OTHER"


class ClaimState(str, Enum):
    OFFICIALLY_CONFIRMED = "OFFICIALLY_CONFIRMED"
    CREDIBLY_REPORTED = "CREDIBLY_REPORTED"
    CONFLICTING = "CONFLICTING"
    UNCONFIRMED = "UNCONFIRMED"
    OUTDATED = "OUTDATED"
    UNKNOWN = "UNKNOWN"


class MarketVerification(str, Enum):
    VERIFIED_OFFER = "VERIFIED_OFFER"
    USER_ENTERED_MARKET_NOT_VERIFIED = "USER_ENTERED_MARKET_NOT_VERIFIED"
    UNKNOWN = "UNKNOWN"


class SelectionSide(str, Enum):
    OVER = "OVER"
    UNDER = "UNDER"
    YES = "YES"
    NO = "NO"
    HOME = "HOME"
    AWAY = "AWAY"


def _required(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")


def _aware(value: datetime, name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be a timezone-aware datetime")


def _https(url: str, name: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{name} must be a complete HTTPS URL")


@dataclass(frozen=True)
class Game:
    """Canonical game identity. Providers supply values; this class invents none."""

    game_id: str
    sport: Sport
    season: str
    home_team_id: str
    away_team_id: str
    scheduled_start: datetime
    status: GameStatus = GameStatus.UNKNOWN

    def __post_init__(self) -> None:
        for name in ("game_id", "season", "home_team_id", "away_team_id"):
            _required(getattr(self, name), name)
        if self.home_team_id == self.away_team_id:
            raise ValueError("Game teams must have different canonical IDs")
        _aware(self.scheduled_start, "scheduled_start")


@dataclass(frozen=True)
class Evidence:
    """Attribution and time provenance of one external claim.

    A report cannot be promoted to OFFICIALLY_CONFIRMED merely because
    a summarizer or model describes it as official.
    """

    evidence_id: str
    game_id: str
    claim: str
    source_name: str
    source_url: str
    source_kind: SourceKind
    claim_state: ClaimState
    retrieved_at: datetime
    published_at: Optional[datetime] = None
    player_id: Optional[str] = None

    def __post_init__(self) -> None:
        for name in ("evidence_id", "game_id", "claim", "source_name"):
            _required(getattr(self, name), name)
        _https(self.source_url, "source_url")
        _aware(self.retrieved_at, "retrieved_at")
        if self.published_at is not None:
            _aware(self.published_at, "published_at")
        if self.claim_state == ClaimState.OFFICIALLY_CONFIRMED and self.source_kind != SourceKind.OFFICIAL:
            raise ValueError("Reporting cannot by itself establish OFFICIALLY_CONFIRMED")


@dataclass(frozen=True)
class Selection:
    """Exact user selection; not evidence of an available sportsbook offer.

    Market type and settlement rules are untrusted until verified separately.
    `line` uses Decimal to preserve the exact user-supplied threshold.
    A verified offer requires an independently sourced quote and timestamp.
    """

    selection_id: str
    game_id: str
    sport: Sport
    market_name: str
    side: SelectionSide
    line: Decimal
    period: str
    market_verification: MarketVerification = MarketVerification.USER_ENTERED_MARKET_NOT_VERIFIED
    player_id: Optional[str] = None
    sportsbook_name: Optional[str] = None
    offer_source_url: Optional[str] = None
    offer_checked_at: Optional[datetime] = None
    settlement_terms: Optional[str] = None

    def __post_init__(self) -> None:
        for name in ("selection_id", "game_id", "market_name", "period"):
            _required(getattr(self, name), name)
        if not isinstance(self.line, Decimal) or not self.line.is_finite():
            raise ValueError("line must be a finite Decimal preserving exact precision")
        if self.market_verification == MarketVerification.VERIFIED_OFFER:
            if not self.offer_source_url or self.offer_checked_at is None:
                raise ValueError("VERIFIED_OFFER requires an offer source and observed time")
            _https(self.offer_source_url, "offer_source_url")
            _aware(self.offer_checked_at, "offer_checked_at")
        elif self.offer_checked_at is not None:
            _aware(self.offer_checked_at, "offer_checked_at")
        if self.offer_source_url is not None:
            _https(self.offer_source_url, "offer_source_url")
