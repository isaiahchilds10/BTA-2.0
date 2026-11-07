# BTA 2.0 — Step 5: Safe foundation package

**Purpose:** Add the **approved original logo**, **exact approved specification**, independent Python data contracts and offline policy tests to the already-deployed BTA 2.0 repository.

**Source:** Final Master Specification and Final Spec Handoff ZIP (November 7, 2026).

**Repo:** `isaiahchilds10/BTA-2.0` — only this **new** project is in scope.

**Existing files intentionally excluded:** `streamlit_app.py`, `requirements.txt`.

## Browser upload (desktop recommended)

1. Download `BTA_2_0_STEP_5_FOUNDATION.zip` and **extract** it. GitHub does not automatically unpack ZIP archives. If you upload the ZIP itself as one file, these modules will not become available.
2. Open `https://github.com/isaiahchilds10/BTA-2.0` and verify the repo title is **BTA-2.0**, NOT `BTA-NBA-engine`.
3. Create a new branch named `phase0-foundation` from `main`, or select the GitHub **Create a new branch** option when proposing uploaded files.
4. On the new branch, choose **Add file → Upload files** and drag the *contents* of the extracted ZIP into the upload area. Keep the internal paths and directories exactly as packaged. GitHub's browser supports folder drag-drop. On a phone, file pickers may be unable to select folders: use desktop mode or a computer rather than flattening paths.
5. Commit message: `Add BTA 2.0 specification, logo and safe domain foundation`.
6. Open a pull request into `main`, verify the 'Files changed' list adds the exact new files and doesn't delete/change `streamlit_app.py` or `requirements.txt`. Merge only after tests pass.

## Offline test

Open a GitHub Codespace from the branch, or run in a local terminal from repository root:

```bash
python -m unittest discover -s tests -v
```

These tests do NOT validate sports feeds, grading accuracy, predictive calibration or Streamlit deployment. They only validate foundational programming rules.

## Optional logo placement (separate follow-up change)

When you are ready to put the approved logo on the running Home page, edit the existing `streamlit_app.py` (do not replace it) and add this **after** any `st.set_page_config(...)` and before your first content title:

```python
st.logo("assets/bta_belt_branding_logo.png")
```

It uses the unchanged, approved asset. Note that `st.logo` scales to a small height. For a larger banner, use `st.image("assets/bta_belt_branding_logo.png", width=220)` instead, in the desired visible page section. Do not paste either call before `import streamlit as st`.

## Next real milestone

Connect and verify authentic schedules and game identity mapping for NBA, NFL and college football, all with explicit `CURRENT` / `DELAYED` / `UNAVAILABLE` states. No fake games, odds, injuries, model percentages, or grades.
