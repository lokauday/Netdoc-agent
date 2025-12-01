import streamlit as st
from auth_engine import current_user
from utils.parser import parse_config
from main import generate_topology_mermaid


def goto(page):
    st.session_state.page = page
    st.rerun()


def topology_page():
    user = current_user()
    if not user:
        goto("login")

    st.sidebar.title("📌 Navigation")
    if st.sidebar.button("Dashboard"):
        goto("dashboard")
    if st.sidebar.button("Upload & Audit"):
        goto("audit")
    if st.sidebar.button("Logout"):
        goto("login")

    st.title("🌐 Topology Generator")

    config = st.text_area("Paste configuration", height=300)

    if st.button("Generate Topology"):
        parsed = parse_config(config)
        topo = generate_topology_mermaid(parsed["raw"])
        st.markdown(f"```mermaid\n{topo}\n```")

    if st.button("Back"):
        goto("dashboard")
