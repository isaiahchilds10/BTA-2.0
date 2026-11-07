# BTA 2.0 — Step 8: real sports schedule feasibility adapters

**Only for new repository** `isaiahchilds10/BTA-2.0`. Preserve `BTA-NBA-engine` unchanged.

**What this package really does:** adds source adapters, parser validation, immutable game identity mapping, safe no-fabrication failures, three sport-specific source names, and a command-line smoke check. These adapters retrieve real schedules **when provider access works**, but do **not** implement full BTA analysis, live injury verification, probabilities, account privacy, or sportsbook odds.

**What this package does not overwrite:** the existing Streamlit entry point (`streamlit_app.py`), requirements file (`requirements.txt`), original BTA logo, master spec, and all Step 5 source contracts and tests. Upload as a NEW development branch before merging.

## Source candidates (verified documentation; not yet host-tested)

- **NBA:** `https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json`; current-season public CDN feed. May reject cloud IPs; upstream update time is not guaranteed from the payload. Official NBA-operated domain, but access and rights must be evaluated.
- **NFL:** `https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv`; community-maintained season schedule. Not an official NFL live status source. Actual game times are in US Eastern in this file; convert to UTC. Consider attribution and dataset licensing independently.
- **College Football:** `https://api.collegefootballdata.com/games` with `year`, `seasonType=regular`, `classification=fbs`, and Bearer `CFBD_API_KEY`. Free key currently advertises **1,000 calls/month** across CFBD/CBBD. This stage tests the regular season only. Free tier does not demonstrate reliable live play-by-play, and no live provider coverage is claimed.

**BTA freshness rule:** Because these schedule adapters do not establish the *original provider-updated-at timestamp*, a retrieved schedule returns `DELAYED`, not `CURRENT`. This does **not** mean the HTTP request was old; it means upstream recency is unverified. `UNAVAILABLE` means missing key, source failure, or unparseable data. No game is generated from an unavailable feed.

## Safest GitHub upload procedure

1. Make a new branch from `main` named **`phase1-schedules`**.
2. Drag **only the contents** of this extracted ZIP into the repository. GitHub should add new files under `data_sources/`, `scripts/`, `tests/`, `docs/` plus this README. It must not delete or modify your existing `streamlit_app.py`, `requirements.txt`, foundation files, or master spec.
3. Commit to the branch with message `Add three-sport schedule source adapters and smoke checks`.
4. In GitHub Codespaces on **that branch**, run:

```bash
python -m unittest discover -s tests -v
```

5. Smoke test candidate HTTP access **without an API key**:

```bash
python -m scripts.check_schedules --sport nba nfl
```

6. A complete smoke test with CFBD requires a free key. Get a free key at `https://collegefootballdata.com/key`, but **do not paste it into ChatGPT, source files, GitHub commits, screenshots, or terminal logs**. To test the key in a Codespace, use the built-in terminal without recording the secret, e.g.:

```bash
read -s CFBD_API_KEY
export CFBD_API_KEY
python -m scripts.check_schedules --sport cfb
unset CFBD_API_KEY
```

Typing a token at `read -s` does not echo it. Never type a token into a command line that becomes shell history. This terminal test calls the remote CFBD API and consumes free quota.

7. Read the printed providers, source timestamps, limitations, record counts, and sample upcoming games. `DELAYED` means the adapter has **not** proven original upstream freshness.
8. **Do not merge** until you review the results, validate terms/licensing for your use case, and confirm new code is isolated. The final specification requires a separate deployed-Streamlit-host test; this Codespaces smoke test is not that test.

### Known limitations / future gates

- This version intentionally does not add a sixth public navigation destination. Schedule results aren't yet wired into Home/NBA/NFL/CFB screens.
- NBA payload format can change and the NBA CDN may block a hosting provider. Confirm network access from Streamlit Community Cloud before shipping.
- NFL schedule is not an authoritative injury feed and does not establish in-game status; no guessing of live status.
- CollegeFootballData free quota, token issuance, endpoints, licensing, and limits must be rechecked. This stage checks one FBS regular-season schedule request; postseason/other classifications remain deferred.
- The Step 5 contracts require independent timestamp evidence for `CURRENT`; this package therefore never asserts it.
- Do not add user-facing picks, probabilities, grades or betting odds based on a schedule alone.
