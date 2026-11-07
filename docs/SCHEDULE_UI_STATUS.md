# Step 9: Streamlit schedule UI gate

**Authoritative basis:** BTA 2.0 Final Master Specification, particularly the five-navigation design, source freshness, strict no-fabrication rule, and source-feasibility acceptance gates.

## Verified by offline tests

- Upcoming games are filtered from source-observed, structurally validated schedule records only.
- Expired games, cancelled, postponed, final, and unknown-status games are not marketed as upcoming.
- UTC-to-Eastern/Central kickoff conversion uses real timezone rules, including daylight-saving transitions.
- Source names, retrieval age and unverified upstream update status are visible.
- No real fixture was supplied as a test result; test games are synthetic and never displayed in production.

## Not yet validated

- Network access **from Streamlit Community Cloud**, which is different from Codespaces.
- Latest source update timestamps; adapters return DELAYED even on successful HTTP requests.
- All leagues' completeness, source terms, and independent schedule reconciliation.
- Cross-user public cache safe usage bounds, permanent storage, autonomous scheduling, source quotas.
- Live status, player info, injuries, odds, probability calibration, BTA grades, My Slip, auth, and backups.

## Security and resource rules

- `CFBD_API_KEY` is read server-side from an environment variable, not browser input or GitHub source.
- Put the token in Streamlit Community Cloud **App settings → Secrets** as a root-level TOML entry; never paste it in a public chat, code commit, log, or screenshot. See official Streamlit secrets docs.
- The shared Streamlit cache contains **public schedule information only**; it is **not** durable automation or private member storage.
- Cache TTL is 1800 seconds, which reduces but does not guarantee zero redundant API calls.
- This stage does not add a new BTA navigation destination; preview is for development only.
