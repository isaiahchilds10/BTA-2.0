# Step 10 implementation & acceptance record

**Objective:** wire the previously preview-only Step 9 source-backed schedule panels into BTA 2.0's real `streamlit_app.py` while retaining the approved navigation (Home, NBA, NFL, College Football, My Slip), original branding and independent new codebase.

## Change scope

- Add imports to the *existing* entrypoint (after `import streamlit as st`).
- Add `render_home_schedules` to the existing Home route.
- Add `render_sport_schedule` to each existing or shared NBA/NFL/College Football route.
- Do **not** change My Slip, branding, source adapters, URL, original repository, old app, or any authentication implementation.
- No more than the existing five routes: no `pages/` directory, no extra Streamlit app target.

## Two-stage safety

1. **Preview:** generate a proposed candidate from the *actual* entrypoint on a new branch. Fail closed on unexpected AST, nav labels, missing safe fallback, or prior integration.
2. **Apply:** require a byte-for-byte match to the current generated candidate, back up original in `.git`, and write only the active branch file. A PR/merge is still required to update production.

## Acceptance evidence to record

- [ ] Foundation+schedule+UI+integration offline tests pass.
- [ ] Existing `streamlit_app.py` diffs show *only* expected imports and route hookups.
- [ ] Codespaces preview displays all five exact navigation destinations.
- [ ] NBA and NFL show real schedule fixtures **or** visibly honest unavailability, with UTC-source/zone conversion and timestamps; no synthetic data.
- [ ] CFB clearly reports missing key if absent, or actual real games if a valid configured free key works.
- [ ] Existing My Slip and Home design survive unchanged except schedule section addition.
- [ ] Streamlit Cloud deployed host tested after PR merge, including refresh and source failures.
- [ ] No secret keys appear in GitHub code/commits, screenshots or shared logs.

## Deferred milestones (not delivered in Step 10)

40-section statistical/situational research implementation, evidence-gated grading, full five-script matrices, injury official/corroborated claims, exact sportsbook offers, actual slips, private accounts/auth, shared exposure, live monitoring, autonomous work queue, independently calibrated probabilities and postgame settlement.
