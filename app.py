# ===============================================================
#  NetDoc AI — Streamlit Frontend Router (Main App)
# ===============================================================

import streamlit as st
from auth_engine import login_user, signup_user, logout, current_user
from admin_engine import admin_page
from main import run_security_audit, generate_topology_mermaid, export_all_formats
from utils.parser import parse_config
from database import init_db


# ---------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------
st.set_page_config(
    page_title="NetDoc AI",
    page_icon="⚡",
    layout="wide"
)

# Load CSS
def load_css():
    st.markdown(
        """
        <style>
        body { background-color: #1a1d21 !important; color: #fff; }
        .stButton>button { border-radius: 8px; padding: 0.6rem 1rem; font-weight: bold; }
        .stTextInput>div>div>input { color: #fff !important; }
        .stExpander { background-color: #2a2d32 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )


load_css()

# Initialize DB on boot
init_db()


# =====================================================================
#  NAVIGATION HANDLER
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
#  DASHBOARD PAGE
# =====================================================================
def dashboard_page():
    user = current_user()
    if not user:
        goto("login")

    st.title(f"⚡ Welcome, {user.email}")
    st.caption(f"Organization: {user.organization.org_name}")

    # Sidebar
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

    st.write("Use the sidebar to get started!")


# =====================================================================
#  AUDIT PAGE
# =====================================================================
def audit_page():
    user = current_user()
    if not user:
        goto("login")

    st.title("🔎 Security Audit")

    uploaded = st.file_uploader("Upload Configuration File", type=["txt", "cfg", "conf"])

    if uploaded:
        config_text = uploaded.read().decode()

        parsed = parse_config(config_text)
        audit = run_security_audit(parsed["raw"])
        topology = generate_topology_mermaid(parsed["raw"])
        exports = export_all_formats(audit, topology)

        st.subheader("Audit Result")
        st.json(audit)

        st.subheader("Topology")
        st.markdown(f"```mermaid\n{topology}\n```")

        # Export buttons
        st.subheader("Export")
        st.download_button("Download JSON", exports["json"], file_name="audit.json")
        st.download_button("Download Markdown", exports["markdown"], file_name="audit.md")
        st.download_button("Download TXT", exports["txt"], file_name="audit.txt")
        st.download_button("Download HTML", exports["html"], file_name="audit.html")

    if st.button("Back"):
        goto("dashboard")


# =====================================================================
#  TOPOLOGY PAGE
# =====================================================================
def topology_page():
    user = current_user()
    if not user:
        goto("login")

    st.title("🌐 Topology Generator")

    config = st.text_area("Paste Configuration", height=300)

    if st.button("Generate Topology"):
        parsed = parse_config(config)
        topo = generate_topology_mermaid(parsed["raw"])

        st.markdown(f"```mermaid\n{topo}\n```")

    if st.button("Back"):
        goto("dashboard")


# =====================================================================
#  ROUTER
# =====================================================================
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "dashboard":
    dashboard_page()
elif st.session_state.page == "audit":
    audit_page()
elif st.session_state.page == "topology":
    topology_page()
elif st.session_state.page == "admin":
    admin_page()
