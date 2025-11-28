# ============================================================
#   NetDoc AI — Enterprise Edition
#   FULL APP.PY (ALL BLOCKS MERGED)
# ============================================================

import streamlit as st
import json
import os
import time
import bcrypt
import pandas as pd
from datetime import datetime

from database import (
    SessionLocal, User, Organization,
    Billing, ActivityLog, APIKey, UploadedConfig, AuditReport
)

from utils.parser import parse_config
from main import run_security_audit, generate_topology_mermaid, export_all_formats

# ============================================================
# SESSION INITIALIZATION
# ============================================================

def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "org" not in st.session_state:
        st.session_state.org = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "page" not in st.session_state:
        st.session_state.page = "Login"
    if "report" not in st.session_state:
        st.session_state.report = None

init_session()

# ============================================================
# PASSWORD UTILITIES
# ============================================================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ============================================================
# AUTO-BOOTSTRAP DEFAULT ADMIN
# ============================================================

def bootstrap_admin():
    """
    Automatically create default admin:
    Email: lokauday456@gmail.com
    Pass:  Bittu369$
    """
    db = SessionLocal()

    ADMIN_EMAIL = "lokauday456@gmail.com"
    ADMIN_HASH = "$2b$12$OfgfE0WXG.F6CTa2gMrCsedQy6VbexmJ8nP2UQwiv9a8lxKeut77K"

    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()

    if admin is None:
        org = Organization(org_name="NetDoc AI Enterprise")
        db.add(org)
        db.commit()
        db.refresh(org)

        admin = User(
            org_id=org.id,
            email=ADMIN_EMAIL,
            password_hash=ADMIN_HASH,
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("🔥 Admin user created successfully.")
    else:
        print("✔ Admin already exists")

    db.close()

bootstrap_admin()

# ============================================================
# AUTH GUARDS
# ============================================================

def require_login():
    if st.session_state.user is None:
        st.warning("Please login first.")
        st.stop()

def require_admin():
    if not st.session_state.is_admin:
        st.error("Admin access required.")
        st.stop()

# ============================================================
# GLOBAL DARK THEME CSS
# ============================================================

st.markdown("""
<style>
body { background-color:#1a1d21 !important; color:#e2e2e2 !important; }
section[data-testid="stSidebar"] { background:#141619 !important; border-right:1px solid #2a2d33; }
.card { background:#24272b; padding:22px; border-radius:12px; border:1px solid #30343a; margin-bottom:24px; }
.metric-card { background:#24272b; padding:18px; border-radius:12px; border:1px solid #2f3239; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():
    st.title("🔐 Login to NetDoc AI")

    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()

        if user and verify_password(pw, user.password_hash):

            st.session_state.user = user
            st.session_state.org = db.query(Organization).filter(Organization.id == user.org_id).first()
            st.session_state.is_admin = user.is_admin

            st.session_state.page = "Home"
            st.success("Login successful!")
            st.rerun()

        else:
            st.error("Invalid email or password.")

        db.close()

# ============================================================
# SIGNUP (ADMIN ONLY)
# ============================================================

def signup_page():
    require_admin()

    st.title("➕ Create New User")

    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    is_admin_bool = st.checkbox("Make admin")

    if st.button("Create User"):
        db = SessionLocal()
        exists = db.query(User).filter(User.email == email).first()

        if exists:
            st.error("User already exists.")
        else:
            user = User(
                org_id=st.session_state.org.id,
                email=email,
                password_hash=hash_password(pw),
                is_admin=is_admin_bool
            )
            db.add(user)
            db.commit()
            st.success("User created.")
        db.close()

# ============================================================
# LOGOUT
# ============================================================

def logout():
    st.session_state.user = None
    st.session_state.org = None
    st.session_state.is_admin = False
    st.session_state.page = "Login"
    st.rerun()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def navbar():
    if st.session_state.user is None:
        return

    with st.sidebar:
        st.markdown("### 📂 Navigation")

        menu = [
            "Home", "Dashboard", "Upload",
            "Documentation", "Security Audit", "Topology",
            "Exports", "Billing", "System Health"
        ]

        if st.session_state.is_admin:
            menu.append("Admin Console")

        menu.append("Logout")

        choice = st.radio("", menu)
        st.session_state.page = choice

# ============================================================
# HOME PAGE (LANDING)
# ============================================================

def home_page():
    require_login()
    st.markdown("""
    <div class="card" style="text-align:center; padding:50px;">
        <h1 style="color:#5b9bff;">⚡ NetDoc AI — Enterprise Edition</h1>
        <p>AI-powered documentation, audits, topology & exports.</p>
        <img src="logo.png" style="width:180px; margin-top:30px;">
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# DASHBOARD
# ============================================================

import random

def dashboard_page():
    require_login()

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📊 Network Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Active Devices", random.randint(5, 20))
    col2.metric("Total VLANs", random.randint(10, 50))
    col3.metric("Uptime %", f"{random.randint(95,100)}%")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# UPLOAD + PARSE CONFIGS
# ============================================================

def upload_page():
    require_login()

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📁 Upload Configuration Files")

    files = st.file_uploader("Upload .txt / .cfg / .log", type=["txt","cfg","log"], accept_multiple_files=True)

    if files and st.button("Process Files"):
        full = ""

        for f in files:
            full += f"\n\n# FILE: {f.name}\n"
            full += f.read().decode("utf-8")

        parsed = parse_config(full)

        # Save to DB
        db = SessionLocal()
        rec = UploadedConfig(
            org_id=st.session_state.org.id,
            file_name="Bundle Upload",
            content=full,
            parsed_json=parsed
        )
        db.add(rec)
        db.commit()
        db.close()

        st.session_state.report = parsed
        st.success("Uploaded & parsed successfully!")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# DOCUMENTATION PAGE
# ============================================================

def documentation_page():
    require_login()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📄 Documentation Output")

    if st.session_state.report:
        st.json(st.session_state.report)
    else:
        st.info("Upload configuration files first.")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SECURITY AUDIT PAGE
# ============================================================

def audit_page():
    require_login()

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🛡 Security Audit")

    if st.session_state.report:
        with st.spinner("Running audit..."):
            audit = run_security_audit(st.session_state.report)

        db = SessionLocal()
        rec = AuditReport(
            org_id=st.session_state.org.id,
            title="Security Audit",
            result=audit
        )
        db.add(rec)
        db.commit()
        db.close()

        st.json(audit)
    else:
        st.info("Upload configs first.")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# TOPOLOGY PAGE
# ============================================================

def topology_page():
    require_login()

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🌐 Topology Diagram")

    if st.session_state.report:
        topo = generate_topology_mermaid(st.session_state.report)
        st.markdown(f"```mermaid\n{topo}\n```")
    else:
        st.info("Upload configs first.")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# EXPORTS PAGE
# ============================================================

def export_page():
    require_login()

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📤 Export Suite")

    if st.session_state.report is None:
        st.info("Generate documentation first.")
        return

    pdf, docx, html = export_all_formats(st.session_state.report)

    st.download_button("📄 Download PDF", pdf, file_name="NetDoc_Report.pdf")
    st.download_button("📝 Download DOCX", docx, file_name="NetDoc_Report.docx")
    st.download_button("🌐 Download HTML", html, file_name="NetDoc_Report.html")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# BILLING PAGE
# ============================================================

def billing_page():
    require_login()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 💳 Billing & Subscription")

    st.code("Enterprise Plan (Admin Managed)")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.write("### Free\nBasic Upload")
    col2.write("### Pro — $19/mo\nAudit + Topology + Exports")
    col3.write("### Enterprise\nSSO + Branding")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SYSTEM HEALTH PAGE
# ============================================================

import subprocess

def system_health_page():
    require_login()

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🩺 System Health")

    col1, col2, col3 = st.columns(3)

    # Ping
    try:
        out = subprocess.run(["ping","-n","1","8.8.8.8"], stdout=subprocess.PIPE, text=True).stdout
        ok = "TTL=" in out
        col1.metric("Internet", "Online" if ok else "Offline")
    except:
        col1.metric("Internet", "Error")

    # Latency
    try:
        lat = [x for x in out.split("\n") if "time=" in x]
        latency = lat[0].split("time=")[1] if lat else "N/A"
        col2.metric("Latency", latency)
    except:
        col2.metric("Latency","N/A")

    # DB
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        col3.metric("Database","Connected")
    except:
        col3.metric("Database","Error")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# ADMIN — USER MANAGEMENT
# ============================================================

def admin_user_management():
    require_admin()
    st.subheader("👥 User Management")

    db = SessionLocal()
    users = db.query(User).filter(User.org_id == st.session_state.org.id).all()

    for u in users:
        col1, col2, col3 = st.columns([4,2,2])
        col1.write(f"📧 {u.email}")
        col2.write("Admin" if u.is_admin else "User")
        if col3.button(f"Delete {u.id}", key=f"del_{u.id}"):
            db.delete(u)
            db.commit()
            st.warning(f"Deleted {u.email}")
            st.rerun()

    db.close()

# ============================================================
# ADMIN — API KEYS
# ============================================================

def admin_api_keys():
    require_admin()
    st.subheader("🔑 API Keys")

    db = SessionLocal()

    label = st.text_input("Label")

    if st.button("Generate New API Key"):
        raw = os.urandom(32).hex()
        hashed = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()

        entry = APIKey(org_id=st.session_state.org.id, label=label, key_hash=hashed)
        db.add(entry)
        db.commit()

        st.success("API Key Created!")
        st.code(raw)

    st.markdown("---")

    keys = db.query(APIKey).filter(APIKey.org_id == st.session_state.org.id).all()
    for k in keys:
        st.write(f"🔹 {k.label} — {k.created_at}")
        if st.button(f"Delete Key {k.id}", key=f"keydel_{k.id}"):
            db.delete(k)
            db.commit()
            st.rerun()

    db.close()

# ============================================================
# ADMIN — ACTIVITY LOGS
# ============================================================

def admin_activity_logs():
    require_admin()
    st.subheader("📜 Activity Logs")

    db = SessionLocal()
    logs = (
        db.query(ActivityLog)
        .filter(ActivityLog.org_id == st.session_state.org.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(50)
        .all()
    )

    for l in logs:
        st.write(f"🕒 {l.created_at} — {l.event}")
        st.json(l.metadata)

    db.close()

# ============================================================
# ADMIN CONSOLE
# ============================================================

def admin_console_page():
    require_admin()
    st.title("👑 Admin Console")

    t1, t2, t3 = st.tabs(["Users", "API Keys", "Activity Logs"])

    with t1:
        admin_user_management()
    with t2:
        admin_api_keys()
    with t3:
        admin_activity_logs()

# ============================================================
# ROUTER
# ============================================================

def router():
    navbar()

    p = st.session_state.page

    if p == "Login":
        login_page()
    elif p == "Home":
        home_page()
    elif p == "Dashboard":
        dashboard_page()
    elif p == "Upload":
        upload_page()
    elif p == "Documentation":
        documentation_page()
    elif p == "Security Audit":
        audit_page()
    elif p == "Topology":
        topology_page()
    elif p == "Exports":
        export_page()
    elif p == "Billing":
        billing_page()
    elif p == "System Health":
        system_health_page()
    elif p == "Admin Console":
        admin_console_page()
    elif p == "Logout":
        logout()
    else:
        st.error("Page not found.")

# ============================================================
# MAIN ENTRY
# ============================================================

if __name__ == "__main__":
    router()
