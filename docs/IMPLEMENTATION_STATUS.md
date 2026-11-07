# BTA 2.0 implementation and capability register

Baseline: Final Master Specification approved 2026-11-07. Update **only after verified tests**.

| Capability | Honest status after Step 5 | Required next acceptance proof |
|---|---|---|
| GitHub BTA-2.0 repository and Streamlit Home | **User reports operational**; not independently tested by package author | Verify current app URL and deployed revision |
| Approved logo asset in repository | **Included in Step 5 kit**; upload not verified | Confirm image path in new repo |
| Exact approved master specification | **Included in Step 5 kit**; upload not verified | Confirm GitHub markdown is identical |
| Canonical game, evidence, selection contracts | **Offline contracts included**; tests needed after upload | Run contract suite in repo environment |
| NFL five-script screening guard | **Offline code included**; no sourced assessments | Test with dated verified source packs |
| CFB five-script definitions | **Declared**, no research engine yet | Implement tested CFB moneyline stress analysis |
| NBA five-script definitions | **UNRESOLVED** (original exact list not recovered) | Reconcile source methodology |
| NBA authentic schedules/stats/injuries | **NOT CONNECTED** | Live test from deployed host |
| NFL authentic schedules/stats/injuries | **NOT CONNECTED** | Live test from deployed host |
| CFB authentic schedules/stats/injuries | **NOT CONNECTED** | Live test from deployed host |
| Verified sportsbook lines and prices | **NOT CONNECTED** | Compliant timestamped offer provider or user-entered warning |
| BTA grade certification | **NOT IMPLEMENTED** | All applicable 40-section gates, source verification, independent audit |
| Validated numerical probabilities | **NOT IMPLEMENTED** | Chronological out-of-time calibration by market |
| My Slip durable tickets | **NOT IMPLEMENTED** | Persistence, 30-leg reload, permissions, history tests |
| Invite-only accounts/backup/recovery | **NOT IMPLEMENTED** | Magic-link delivery, RLS, encrypted backup+restore test |
| Durable jobs, adaptive AI, live alerts | **NOT IMPLEMENTED** | Production-environment scheduler, quota, failover and feed tests |

## Original methodology gaps preserved explicitly

The original verbatim BTA sections 1-18 and the exact list of 15 supplementary adversity scenarios were not supplied in the approved handoff. The functional crosswalk does **not** establish verbatim equivalence. Full NBA five-script definitions also require source reconciliation.

## Protection rules

- Never add paid providers or unexpectedly billable services.
- Never claim synthetic fixtures are real events.
- Never calculate or display a betting probability until a valid market-specific model exists.
- Never call a player officially active/out based solely on media reporting.
- Never grant certification on incomplete evidence.
- Never auto-edit a user's selections.
- Existing `BTA-NBA-engine` remains untouched.
