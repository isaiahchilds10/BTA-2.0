"""Canonical BTA 2.0 domain contracts; independent of legacy versions."""

from .contracts import (
    ClaimState,
    Evidence,
    Game,
    GameStatus,
    MarketVerification,
    Selection,
    SourceKind,
    Sport,
)

__all__ = [
    "ClaimState", "Evidence", "Game", "GameStatus", "MarketVerification",
    "Selection", "SourceKind", "Sport",
]
