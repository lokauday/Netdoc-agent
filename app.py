# ===============================================================
#  NetDoc AI — Streamlit Frontend Router (Main App)
# ===============================================================

import streamlit as st
from auth_engine import login_user, signup_user, logout, current_user
from admin_engine import admin_page
from database import init_db

# Import external page modules
from app_pages.dashboard import dashboard_page
from app_pages.audit_page import audit_page
from app_pages.topology_page import topology_page


# ---------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------
st.set_page_config(
    page_title="NetDoc AI",
    page_icon="⚡",
    layout="wide",
)


# ---------------------------------------------------------------
# LOAD GLOBAL CSS
# ---------------------------------------------------------------
def load_css():
    try:
        with open("static/global.css", "r") as f:
            css = f"<style>{f.read()}</style>"
            st.markdown(css, unsafe_allow_html=True)
    except:
        pass


load_css()


# ---------------------------------------------------------------
# INITIALIZE DATABASE
# ---------------------------------------------------------------
init_db()


# =====================================================================
#  SIMPLE PAGE NAVIGATION SYSTEM
# =====================================================================
if "page" not in st.session_state:
    st.session_state.page = "login"


def goto(page_name: str):
    st.session_state.page = page_name
    st.rerun()


# =====================================================================
#  LOGIN PAGE
# =====================================================================
def login_page():
    st.title("🔐 NetDoc AI — Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        ok, msg = login_user(email, password)
        st.info(msg)
        if ok:
            goto("dashboard")

    st.write("Don't have an account?")
    if st.button("Create Account"):
        goto("signup")


# =====================================================================
#  SIGNUP PAGE
# =====================================================================
def signup_page():
    st.title("📝 Create an Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        ok, msg = signup_user(email, password)
        st.info(msg)
        if ok:
            goto("login")

    if st.button("Back to Login"):
        goto("login")


# =====================================================================
#  ROUTER — DIRECTS TO EXTERNAL PAGES
# =====================================================================

page = st.session_state.page

if page == "login":
    login_page()

elif page == "signup":
    signup_page()

elif page == "dashboard":
    dashboard_page()        # from app_pages/dashboard.py

elif page == "audit":
    audit_page()            # from app_pages/audit_page.py

elif page == "topology":
    topology_page()         # from app_pages/topology_page.py

elif page == "admin":
    admin_page()            # from admin_engine.py
