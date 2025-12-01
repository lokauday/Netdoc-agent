import streamlit as st
from auth import (
    attempt_login, attempt_signup,
    login_required, admin_required, logout,
)
from database import SessionLocal, User, Organization


# ============================================================
#  LOGIN PAGE
# ============================================================

def login_page():
    st.title("🔐 Login to NetDoc AI")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        ok, msg = attempt_login(email, password)
        if ok:
            st.success("Logged in successfully!")
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error(msg)

    st.write("---")
    st.write("Don't have an account?")
    if st.button("Create an account"):
        st.session_state.page = "signup"
        st.rerun()


# ============================================================
#  SIGNUP PAGE
# ============================================================

def signup_page():
    st.title("🆕 Create an Account")

    org_name = st.text_input("Organization Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up", use_container_width=True):
        ok, msg = attempt_signup(org_name, email, password)
        if ok:
            st.success(msg)
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error(msg)

    st.write("---")
    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


# ============================================================
#  DASHBOARD PAGE
# ============================================================

def dashboard_page():
    login_required()

    st.title("📊 NetDoc AI Dashboard")

    st.success(f"Welcome, user {st.session_state.user_id}!")

    st.write("Your organization:", st.session_state.org_id)

    st.write("---")
    st.subheader("Navigation")

    if st.button("Upload Config"):
        st.session_state.page = "upload"
        st.rerun()

    if st.button("View Reports"):
        st.session_state.page = "reports"
        st.rerun()

    if st.session_state.is_admin:
        if st.button("Admin Console"):
            st.session_state.page = "admin"
            st.rerun()

    if st.button("Logout"):
        logout()
        st.session_state.page = "login"
        st.rerun()


# ============================================================
#  ADMIN CONSOLE
# ============================================================

def admin_console():
    admin_required()

    st.title("🛠 Admin Console")

    db = SessionLocal()

    org = db.query(Organization).filter(Organization.id == st.session_state.org_id).first()
    users = db.query(User).filter(User.org_id == st.session_state.org_id).all()

    st.subheader("Organization Info")
    st.info(f"Org Name: {org.org_name}\nOrg ID: {org.id}")

    st.write("---")
    st.subheader("Users")

    for u in users:
        st.write(f"👤 **{u.email}** — role: {u.role} — admin: {u.is_admin}")

    db.close()

    st.write("---")
    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
