"""Optional Streamlit schedule panels for the five existing BTA navigation areas.

Imported only by Streamlit app/preview. No new navigation destinations are added.
No API credentials are displayed, persisted in reports, or passed to users.
"""
from __future__ import annotations

from datetime import datetime, timezone
import streamlit as st

from data_sources.contracts import FeedStatus, SourceResult
from data_sources.schedules import (
    SchedulePayload, nba_schedule, nfl_schedule, cfb_schedule, season_for_football,
)
from domain.contracts import Sport
from ui.schedule_models import SPORT_LABELS, readable_kickoff, source_caption, upcoming_games


@st.cache_data(ttl=1800, max_entries=9, show_spinner="Checking published game schedules…")
def _cached_schedule(sport_value: str, season: int) -> SourceResult[SchedulePayload]:
    """Cross-session PUBLIC schedule cache (30-minute max age while process runs).

    Streamlit cache is not durable storage and is not a background job. The CFBD
    token is read by the source adapter from the server environment, not passed
    through cache arguments, pages, or URLs. Never store member-private slips here.
    """
    sport = Sport(sport_value)
    if sport == Sport.NBA:
        return nba_schedule()
    if sport == Sport.NFL:
        return nfl_schedule(season=season)
    if sport == Sport.COLLEGE_FOOTBALL:
        return cfb_schedule(year=season)
    raise ValueError("unsupported sport")


def _get_schedule(sport: Sport, now: datetime) -> SourceResult[SchedulePayload]:
    return _cached_schedule(sport.value, season_for_football(now))


def _render_provider_status(result: SourceResult[SchedulePayload]) -> None:
    if result.status == FeedStatus.UNAVAILABLE:
        # Adapters sanitize exceptions and do not print sensitive headers.
        st.warning("Schedule unavailable from this source right now. No games have been invented.")
        if result.limitation:
            st.caption(result.limitation)
    else:
        st.caption(source_caption(result))
        if result.status == FeedStatus.DELAYED:
            st.info("Schedule retrieved, but upstream update time is not verified. This is **not a live-status feed**.")
        if result.value:
            st.caption(result.value.coverage_note)
            if result.value.rows_skipped:
                st.caption(f"Provider rows skipped by validation: {result.value.rows_skipped}")


def render_sport_schedule(
    sport: Sport, *, days: int = 14, tz: str = "America/New_York", limit: int = 20,
) -> None:
    """Call inside the app's *existing* NBA / NFL / College Football screen."""
    now = datetime.now(timezone.utc)
    st.subheader(f"{SPORT_LABELS[sport]} · Upcoming Schedule")
    st.caption("Game listings only. Injury reports, odds, BTA grading and live outcomes are not yet active.")
    result = _get_schedule(sport, now)
    _render_provider_status(result)
    games = upcoming_games(result, now=now, days=days, limit=limit)
    if result.status != FeedStatus.UNAVAILABLE and not games:
        st.info(f"No verified upcoming scheduled games found for the next {days} days in this feed.")
    for entry in games:
        with st.container(border=True):
            st.markdown(f"**{entry.away_label} at {entry.home_label}**")
            st.caption(f"{readable_kickoff(entry.game.scheduled_start, tz)} | {entry.game.game_id} | Source-reported: scheduled")
    st.caption("A provider-reported schedule does not establish current in-game status or betting market availability.")


def render_home_schedules(*, days: int = 7, tz: str = "America/New_York") -> None:
    """Optional compact schedule preview on existing Home destination."""
    st.subheader("Upcoming Games")
    st.caption("Automatic schedule preview across NBA, NFL and College Football; no picks or ratings yet.")
    now = datetime.now(timezone.utc)
    for sport in Sport:
        result = _get_schedule(sport, now)
        st.markdown(f"**{SPORT_LABELS[sport]}**")
        if result.status == FeedStatus.UNAVAILABLE:
            st.caption(f"Unavailable — {result.limitation or 'provider did not return usable data'}")
            continue
        games = upcoming_games(result, now=now, days=days, limit=3)
        if not games:
            st.caption("No confirmed upcoming scheduled games in selected window.")
        for g in games:
            st.write(f"{g.away_label} at {g.home_label} · {readable_kickoff(g.game.scheduled_start, tz)}")
        st.caption(source_caption(result) + " | Not verified real-time")
