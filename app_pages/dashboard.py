import streamlit as st
from auth_engine import current_user, logout


def goto(page):
    st.session_state.page = page
    st.rerun()


def dashboard_page():
    user = current_user()
    if not user:
        goto("login")

    st.sidebar.title("📌 Navigation")

    if st.sidebar.button("Dashboard"):
        goto("dashboard")
    if st.sidebar.button("Upload & Audit"):
        goto("audit")
    if st.sidebar.button("Topology Map"):
        goto("topology")
    if st.session_state.get("is_admin"):
        if st.sidebar.button("Admin Panel"):
            goto("admin")
    if st.sidebar.button("Logout"):
        logout()
        goto("login")

    st.title(f"⚡ Welcome, {user.email}")
    st.caption(f"Organization: {user.organization.org_name}")
    st.markdown("Use the sidebar to navigate through NetDoc AI.")
