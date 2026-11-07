"""Separated football scenario families and limited player-prop screening.

Important: This is NOT the full 40-section BTA grading engine.
No selection may be certified TAIG or BTA+ based on this function.
NBA script definitions remain pending verbatim reconciliation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple


CFB_MONEYLINE_SCRIPTS: Tuple[str, ...] = (
    "NORMAL_EXPECTED_GAME",
    "UNDERDOG_FAST_10_OR_14_TO_ZERO_START",
    "FAVORITE_MINUS_TWO_TURNOVERS",
    "FAVORITE_PRIMARY_STRENGTH_NEUTRALIZED",
    "ONE_SCORE_FOURTH_QUARTER",
)

NFL_PLAYER_PROP_SCRIPTS: Tuple[str, ...] = (
    "FAVORITE_BLOWOUT",
    "UNDERDOG_BLOWOUT_OR_UPSET",
    "CLOSE_COMPETITIVE_GAME",
    "LOW_SCORING_GAME",
    "HIGH_SCORING_GAME",
)


class ScriptEffect(str, Enum):
    BETTER = "BETTER"
    SAME = "SAME"
    MIXED = "MIXED"
    WORSE = "WORSE"
    NOT_ASSESSED = "NOT_ASSESSED"


class ScreeningStatus(str, Enum):
    CUT = "CUT"
    SPECIAL_REVIEW = "SPECIAL_REVIEW"
    PRIORITY_CANDIDATE = "PRIORITY_CANDIDATE"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


@dataclass(frozen=True)
class ScriptVerdict:
    script_id: str
    effect: ScriptEffect
    reason: str = ""
    evidence_ids: Tuple[str, ...] = ()
    meaningful: bool = False

    def __post_init__(self) -> None:
        if not self.script_id:
            raise ValueError("script_id required")
        if self.effect == ScriptEffect.NOT_ASSESSED:
            if self.meaningful or self.evidence_ids:
                raise ValueError("Unassessed scripts cannot have evidence-based impact")
        elif not self.reason.strip() or not self.evidence_ids:
            raise ValueError("Every assessed script requires explanation and evidence IDs")
        if self.meaningful and self.effect != ScriptEffect.WORSE:
            raise ValueError("meaningful is a flag specifically for harmful WORSE effects")


def screen_nfl_player_prop(verdicts: Iterable[ScriptVerdict]) -> ScreeningStatus:
    """Apply only the NFL prop 2-WORSE hard rule, with strict missing-data handling.

    CUT: at least 2 meaningful worse verdicts even if another script is missing.
    PENDING: no hard CUT, but not all five scripts independently assessed.
    SPECIAL_REVIEW: exactly 1 meaningful WORSE, complete evidence.
    PRIORITY_CANDIDATE: zero meaningful WORSE, complete evidence.
    None of these statuses is a certified BTA grade.
    """
    items = list(verdicts)
    expected = set(NFL_PLAYER_PROP_SCRIPTS)
    seen = [item.script_id for item in items]
    if len(seen) != len(set(seen)):
        raise ValueError("Duplicate script verdicts not allowed")
    if not set(seen).issubset(expected):
        raise ValueError("An NFL prop script must use a documented NFL scenario")
    harmful = sum(item.effect == ScriptEffect.WORSE and item.meaningful for item in items)
    if harmful >= 2:
        return ScreeningStatus.CUT
    if set(seen) != expected or any(item.effect == ScriptEffect.NOT_ASSESSED for item in items):
        return ScreeningStatus.PENDING_VERIFICATION
    if harmful == 1:
        return ScreeningStatus.SPECIAL_REVIEW
    return ScreeningStatus.PRIORITY_CANDIDATE
