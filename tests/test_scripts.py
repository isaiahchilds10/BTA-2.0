"""Offline script-policy tests; fixtures are imaginary and not predictions."""

import unittest

from research.scripts import (
    CFB_MONEYLINE_SCRIPTS, NFL_PLAYER_PROP_SCRIPTS, ScriptEffect,
    ScreeningStatus, ScriptVerdict, screen_nfl_player_prop,
)


def verdicts(worse=(), unassessed=()):
    results = []
    for script in NFL_PLAYER_PROP_SCRIPTS:
        if script in unassessed:
            results.append(ScriptVerdict(script, ScriptEffect.NOT_ASSESSED))
        else:
            is_worse = script in worse
            results.append(
                ScriptVerdict(
                    script_id=script,
                    effect=ScriptEffect.WORSE if is_worse else ScriptEffect.SAME,
                    reason="Synthetic policy test only",
                    evidence_ids=("synthetic-test-source",),
                    meaningful=is_worse,
                )
            )
    return results


class TestScriptRules(unittest.TestCase):
    def test_football_scripts_are_not_interchangeable(self):
        self.assertEqual(len(CFB_MONEYLINE_SCRIPTS), 5)
        self.assertEqual(len(NFL_PLAYER_PROP_SCRIPTS), 5)
        self.assertNotEqual(set(CFB_MONEYLINE_SCRIPTS), set(NFL_PLAYER_PROP_SCRIPTS))

    def test_two_meaningful_worse_means_cut(self):
        got = screen_nfl_player_prop(verdicts(worse=NFL_PLAYER_PROP_SCRIPTS[:2]))
        self.assertEqual(got, ScreeningStatus.CUT)

    def test_one_meaningful_worse_needs_review(self):
        got = screen_nfl_player_prop(verdicts(worse=NFL_PLAYER_PROP_SCRIPTS[:1]))
        self.assertEqual(got, ScreeningStatus.SPECIAL_REVIEW)

    def test_no_worse_is_not_certification(self):
        got = screen_nfl_player_prop(verdicts())
        self.assertEqual(got, ScreeningStatus.PRIORITY_CANDIDATE)
        self.assertNotIn("BTA+", got.value)

    def test_missing_script_blocks_priority(self):
        got = screen_nfl_player_prop(verdicts(unassessed=NFL_PLAYER_PROP_SCRIPTS[:1]))
        self.assertEqual(got, ScreeningStatus.PENDING_VERIFICATION)

    def test_duplicate_script_is_rejected(self):
        items = verdicts()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            screen_nfl_player_prop(items + [items[0]])

    def test_unsupported_scenario_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "documented NFL"):
            screen_nfl_player_prop([
                ScriptVerdict("FAVORITE_MINUS_TWO_TURNOVERS", ScriptEffect.SAME,
                              "Synthetic test", ("fixture",)),
            ])

    def test_assessed_requires_evidence(self):
        with self.assertRaisesRegex(ValueError, "evidence IDs"):
            ScriptVerdict(NFL_PLAYER_PROP_SCRIPTS[0], ScriptEffect.WORSE,
                          reason="Some reason", meaningful=True)


if __name__ == "__main__":
    unittest.main()
