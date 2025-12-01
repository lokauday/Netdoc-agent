import streamlit as st
from auth_engine import current_user


def dashboard_page():
    user = current_user()
    if not user:
        st.warning("You must be logged in.")
        st.stop()

    st.title(f"⚡ Welcome, {user.email}")
    st.caption(f"Organization: {user.organization.org_name}")

    st.write("Use the sidebar to navigate through NetDoc AI.")
