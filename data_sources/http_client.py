"""Minimal bounded HTTPS client for allowlisted BTA schedule providers.

No user-entered URLs; no redirects to other hosts; no auth/header logging.
The service running this code must still confirm licensing and rate limits.
"""
from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
import json

ALLOWED_HOSTS = frozenset({
    "cdn.nba.com", "raw.githubusercontent.com", "api.collegefootballdata.com"
})
MAX_BYTES = 8_000_000


class ProviderFetchError(Exception):
    """Controlled fetch failure (no tokens/headers/external response bodies)."""


class _SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise ProviderFetchError("Redirect outside approved HTTPS providers")
        # Restrict to same host. Tokens must not be passed across providers.
        if parsed.hostname != urlparse(req.full_url).hostname:
            raise ProviderFetchError("Cross-host redirect blocked")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_bytes(url: str, *, bearer_token: str | None = None, timeout: float = 10) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password:
        raise ProviderFetchError("Unapproved provider URL")
    headers = {"User-Agent": "BTA2-Research-Schedule-Feasibility/0.1", "Accept": "application/json, text/csv"}
    if bearer_token:
        if parsed.hostname != "api.collegefootballdata.com":
            raise ProviderFetchError("Bearer tokens only supported for approved CFBD host")
        headers["Authorization"] = "Bearer " + bearer_token
    req = Request(url, headers=headers)
    try:
        with build_opener(_SafeRedirect()).open(req, timeout=timeout) as response:
            if response.status != 200:
                raise ProviderFetchError("HTTP " + str(response.status))
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ProviderFetchError("Provider payload exceeded size limit")
            return raw
    except HTTPError as exc:
        raise ProviderFetchError(f"HTTP {exc.code}") from None
    except URLError:
        raise ProviderFetchError("Provider could not be reached") from None
    except TimeoutError:
        raise ProviderFetchError("Provider request timed out") from None


def fetch_json(url: str, *, bearer_token: str | None = None) -> object:
    raw = fetch_bytes(url, bearer_token=bearer_token)
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProviderFetchError("Provider returned invalid JSON") from None
