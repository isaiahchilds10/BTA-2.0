"""Isolated Step 9 preview. Does not replace production streamlit_app.py.

Run from repository root:
    streamlit run schedule_preview.py
"""
from __future__ import annotations

import streamlit as st
from domain.contracts import Sport
from ui.schedule_sections import render_home_schedules, render_sport_schedule

st.set_page_config(page_title="BTA 2.0 · Schedule Preview", layout="wide")
st.title("BTA 2.0 · Schedule Preview")
st.caption("Development-only preview. This is not the complete BTA app or a validated live feed.")

section = st.selectbox("Preview existing BTA destination", ["Home", "NBA", "NFL", "College Football"])
zone = st.selectbox("Display timezone", ["America/New_York", "America/Chicago", "UTC"], index=0)
days = st.selectbox("Upcoming window", [7, 14, 21, 30], index=1)
if section == "Home":
    render_home_schedules(days=days, tz=zone)
else:
    sport = {"NBA": Sport.NBA, "NFL": Sport.NFL, "College Football": Sport.COLLEGE_FOOTBALL}[section]
    render_sport_schedule(sport, days=days, tz=zone)
st.caption("This preview caches public schedules for up to 30 minutes. It is not a persistent background service.")
