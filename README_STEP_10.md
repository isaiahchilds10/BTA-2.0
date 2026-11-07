# BTA 2.0 — Step 10: safely wire real schedules into the deployed five-screen app

**Source of truth:** BTA 2.0 final approved master specification (November 7, 2026). Keep `BTA-NBA-engine` unchanged. No invented fixtures, odds, grades or live forecasts.

## What this package is

This ZIP adds **only** `scripts/prepare_step10_integration.py`, `tests/test_step10_integration.py`, and `docs/STEP10_INTEGRATION.md`. It intentionally contains **no** `streamlit_app.py`, `requirements.txt` or replacement UI. Your actual entrypoint is the source of truth and must be modified cautiously.

## Preconditions

1. Step 9 preview has been tested on `phase1-schedule-ui`. If not merged, review its changes and merge Step 8 and Step 9 into `main` (in order) **only if** prior tests and source smoke checks pass. If feeds fail, display truthfully `UNAVAILABLE` and investigate rather than claiming they work.
2. From updated `main`, create branch **`phase1-app-schedule-integration`**. Do not work on the `BTA-NBA-engine` repository.
3. Extract this ZIP, drag its *contents* into GitHub's **Add file → Upload files**, commit to this new branch.
4. Open GitHub Codespaces on that branch and in the terminal at repository root run:

```bash
python -m unittest discover -s tests -v
```

With the previous three packages and this package the expected total is **64 tests**; check `OK`, and investigate any difference rather than relying on the number alone.

## Generate a safe preview copy of your real entrypoint

```bash
python -m scripts.prepare_step10_integration --prepare
```

This checks for the *original five-section selectbox* and only generates `streamlit_app_step10_candidate.py` in your Codespace; it **does not touch** `streamlit_app.py`. If it prints `STOP`, do not force it: your actual entrypoint differs from the known starter, and we need a tailored insertion.

Preview only (on the Codespace's forwarded port):

```bash
python -m streamlit run streamlit_app_step10_candidate.py --server.address 0.0.0.0
```

Confirm Home, NBA, NFL, College Football and My Slip all still exist; all schedule panels should show real-source data or truthful `UNAVAILABLE`, with source names and age; My Slip unchanged. This is a preview of your actual app structure, **not** a new sixth destination.

Stop the preview with `Ctrl+C` in terminal.

## Apply only after preview passes

```bash
python -m scripts.prepare_step10_integration --apply
python -m unittest discover -s tests -v
```

The installer stores a backup under `.git/bta_step10_backup/` and modifies only the entrypoint on **this new development branch**. Review:

```bash
git diff -- streamlit_app.py
```

Then test the actual entrypoint:

```bash
python -m streamlit run streamlit_app.py --server.address 0.0.0.0
```

If valid: commit only `streamlit_app.py`, the Step 10 scripts, tests and docs. **Do not commit** `streamlit_app_step10_candidate.py` (preview artifact). Open a PR into `main`, review, merge only after checks pass. Streamlit Community Cloud will then load the updated app from `main`; verify actual schedule panels from deployment host. Roll back by reverting PR if something fails.

## Source gate and known limitations

Schedule retrieval succeeds ≠ verified upstream freshness or live scores. These adapters mark `DELAYED` when original update timestamp is unknown, and `UNAVAILABLE` on missing/failing provider data. College football requires a separately obtained free `CFBD_API_KEY`, stored only in Streamlit Community Cloud **App settings → Secrets**, as a root-level TOML entry; never commit the key.

No My Slip persistence, injuries, betting markets, research scores, calibrated odds, live predictions, auth or backup system is implemented by this stage. Next: build each sport's real research data and market-specific source/evidence eligibility gates.
