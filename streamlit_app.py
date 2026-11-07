
import streamlit as st

st.set_page_config(
    page_title="BTA 2.0 | Belt To Ass",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp {
    background-color: #101115;
    color: #FFFFFF;
}
h1, h2, h3 {
    color: #FFFFFF;
}
[data-testid="stAppViewContainer"] {
    padding-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.title("BTA 2.0")
st.caption("BELT TO ASS | Autonomous Sports Research")

sections = [
    "Home",
    "NBA",
    "NFL",
    "College Football",
    "My Slip",
]

page = st.selectbox("Navigate", sections)

st.divider()

if page == "Home":
    st.subheader("BTA Research Hub")
    st.info(
        "Welcome to the new BTA 2.0 application. "
        "Research engines and data connections are "
        "not yet activated."
    )
elif page == "My Slip":
    st.subheader("My Slip")
    st.info("Saved slips and analysis are coming next.")
else:
    st.subheader(f"{page} Research")
    st.info(
        "This sport's research engine is under development. "
        "No verified predictions are available yet."
    )
