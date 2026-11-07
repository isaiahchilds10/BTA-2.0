# BTA 2.0 — Step 9: real schedule interface preview

**Repository:** `isaiahchilds10/BTA-2.0`. **Keep old `BTA-NBA-engine` untouched.**

## FIRST: finish Step 8 source gate

The phrase "it's working" is not a transcript of provider results. Before merging Step 8, check the real smoke-check output:

- `python -m unittest discover -s tests -v` returns `OK`.
- `python -m scripts.check_schedules --sport nba nfl` returns usable provider data for both, NOT `UNAVAILABLE` (a successful unit test alone is insufficient).
- Review actual game counts, UTC kickoffs, source/status limitations and an independent authoritative source check.
- Do not claim real-time status or comprehensive coverage. `DELAYED` means upstream original update timestamp is unverified.

If Step 8 is not yet merged, commit the Step 8 branch and open a reviewed PR into main first. Merge only after the known gates pass; otherwise keep Step 8 a development branch and investigate the failed source.

## Step 9 on a NEW branch, after Step 8 code exists

1. Create a new GitHub branch from `main`: `phase1-schedule-ui` (if Step 8 wasn't merged, branch from `phase1-schedules` as an experimental preview, and do not merge into main).
2. Extract Step 9 ZIP and upload the **contents** to repository root. Files are ADDITIONS only: `ui/`, `tests/test_schedule_ui.py`, `docs/SCHEDULE_UI_STATUS.md`, `schedule_preview.py`, `README_STEP_9.md`.
3. No `streamlit_app.py` or `requirements.txt` is overwritten. Do NOT put files in `pages/` because this would add a sixth destination.
4. In Codespaces terminal (root of repository) run:

   ```bash
   python -m unittest discover -s tests -v
   ```

   With Step 5 and Step 8 as previously supplied, the offline expected count is **49 tests**, with `OK`.
5. Run the *isolated development preview*:

   ```bash
   streamlit run schedule_preview.py --server.address 0.0.0.0
   ```

   Codespaces should offer to open or forward port 8501. This runs a separate **preview process**, not the deployed Community Cloud app. Use Ctrl+C in terminal when finished.
6. Select Home, NBA, NFL and College Football in the preview selectbox. Confirm source status, real fixture names/times, visible retrieval timestamps, and missing-data messages. The Home preview omits My Slip because no real slip engine exists yet; it does **not** modify production navigation.
7. If no CFBD free key is configured, College Football will correctly display `UNAVAILABLE` (not invented games). You can request one at https://collegefootballdata.com/key. **Do not share the token.** For Streamlit Community Cloud, add a root-level TOML secret `CFBD_API_KEY = "..."` in **App settings → Secrets** after source/terms verification; tokens should not be committed. No key is needed for NBA/NFL preview.
8. Only after preview checks should the UI module be wired into the actual `streamlit_app.py`. We have not inspected that file, so **do not overwrite it with a generic template**. The existing five navigation destinations must remain intact. Share only the *non-secret* app entrypoint code if help is needed with exact placement.

## Integration hooks for the existing BTA navigation (NOT automatic)

At the appropriate sections inside your EXISTING Streamlit application:

```python
from domain.contracts import Sport
from ui.schedule_sections import render_home_schedules, render_sport_schedule

# Home destination content:
render_home_schedules()

# NBA destination content:
render_sport_schedule(Sport.NBA)

# NFL destination content:
render_sport_schedule(Sport.NFL)

# College Football destination content:
render_sport_schedule(Sport.COLLEGE_FOOTBALL)
```

**Never paste all four calls unconditionally.** Each call belongs only inside its own existing destination handler. `My Slip` remains unchanged. App entrypoint wiring must be tailored to the actual code and smoke-tested locally, then host-tested after merging.

## Limitations

No grades, recommendations, player markets, live probabilities, BTA Finds qualification, My Slip, persistent jobs or account protections are added here. This is the next UI/data feasibility step—not completion of the custom 40-section BTA methodology.
