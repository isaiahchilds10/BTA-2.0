# Architecture contract — Step 5 foundation

This project is an independent BTA 2.0 rebuild. The five user-visible destinations remain Home, NBA, NFL, College Football and My Slip. Internal modules may grow without adding more public navigation destinations.

## What is actually implemented by this kit

1. `domain/`: immutable, typed game / evidence / selection contracts.
2. `data_sources/`: explicitly labeled source-result/freshness states (without source integrations).
3. `research/`: **only** isolated, conservative NFL player-prop five-script screening and two prescribed football scenario name lists. The code does not evaluate real games or apply the 40-section audit.
4. `tests/`: synthetic offline tests of safeguards; tests are not sports backtests.
5. `assets/`, `docs/`: original approved logo and verbatim markdown master specification.

## Next increments

- Build NBA, NFL and CFB schedule adapters in parallel after verifying free provider licenses, deploy-host connectivity, quota, timezone correctness and source timestamps.
- Normalized canonical ID joins, observed/unknown states and provenance must precede analysis.
- Add a durable persistence layer with server-side member isolation before enabling My Slip.
- Audit and certify with all applicable source-gated methodology and independent second pass; only validated models may show probabilities.
- Pre-register acceptance metrics, and ship the new integrated app only after core launch gates pass.

## Safe deployment guidance

- This package has **no replacement** `streamlit_app.py` or `requirements.txt`, so the existing working Home page is preserved.
- It adds no Python dependencies, no secrets and no network calls.
- Use a new development branch and pull request to avoid breaking the running deployment.
- Do **not** make the repository public to enable previews; secrets and member data must never be included in Git.
