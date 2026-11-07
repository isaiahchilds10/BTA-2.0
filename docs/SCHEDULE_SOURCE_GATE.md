# Three-sport schedule source gate — not yet approved for production

Sources checked against published documentation on 2026-11-07. This document records *candidates*, not proven deployment access.

| Sport | Candidate | Coverage tested offline | Remaining acceptance gate |
|---|---|---|---|
| NBA | NBA public CDN scheduleLeagueV2.json | JSON parser, ID integrity, UTC time, status guards | Fetch from Streamlit Community Cloud; verify current season, source age, game count, duplicates, terms/license |
| NFL | nflverse nfldata `games.csv` | Eastern-to-UTC kickoff, identity, no fake LIVE state | Fetch from host; reconcile against official schedule; review nflverse attribution/license; distinguish corrections/delay |
| College Football | CFBD `/games?year=...&seasonType=regular&classification=fbs` | FBS parser, verified kickoff, IDs, no-key behavior | User supplies key privately; host connectivity; quota accounting/cache; independently check game count, opponent matches, legal terms |

## Requirements retained

- Same five user-facing destinations; do not add a public diagnostics tab.
- No game, time, injury, odds, or stats generated from fake fixtures in production. Synthetic samples exist **only** in unit tests.
- All provider IDs are namespaced (`NBA:`, `NFL:`, `CFB:`), and start times remain UTC timezone-aware.
- If status/timestamp cannot be established, return `DELAYED` or `UNAVAILABLE`, with explicit limitations.
- Source acquisition must eventually be independent of user navigation, with durable state; none of that is implemented here.
- This implementation milestone is a **feasibility stage**, not a BTA+ grade or three-sport research-engine acceptance.

## Primary and implementation references

- NBA CDN integration notes: `https://github.com/sportsdataverse/hoopR/blob/main/R/nba_stats_scoreboard.R`
- NFL dataset: `https://github.com/nflverse/nfldata/blob/master/data/games.csv`
- NFL data schedule note: `https://nflreadr.nflverse.com/articles/nflverse_data_schedule.html`
- CFBD docs: `https://api.collegefootballdata.com/api/games`
- CFBD free tier: `https://collegefootballdata.com/api-tiers`
- GitHub upload: `https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository`
