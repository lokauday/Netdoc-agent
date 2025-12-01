# ===============================================================
#  NetDoc AI — ADMIN ENGINE (Admin Panel / User Management)
# ===============================================================

import streamlit as st
from database import SessionLocal, User, Upload, AuditReport
from auth_engine import require_admin


# ---------------------------------------------------------------
# Get all users
# ---------------------------------------------------------------
def get_all_users():
    db = SessionLocal()
    users = db.query(User).order_by(User.created_at.desc()).all()
    db.close()
    return users


# ---------------------------------------------------------------
# Delete user
# ---------------------------------------------------------------
def delete_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        db.delete(user)
        db.commit()

    db.close()


# ---------------------------------------------------------------
# Toggle admin status
# ---------------------------------------------------------------
def toggle_admin(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        user.is_admin = 0 if user.is_admin else 1
        db.commit()

    db.close()


# ---------------------------------------------------------------
# Admin Page UI
# ---------------------------------------------------------------
def admin_page():
    require_admin()   # Protect access

    st.title("🔐 Admin Panel")
    st.subheader("Manage Users, Uploads & Audit Reports")

    st.divider()

    # ===========================================================
    #  USER MANAGEMENT SECTION
    # ===========================================================
    st.header("👥 User Accounts")

    users = get_all_users()

    for user in users:
        col1, col2, col3, col4 = st.columns([4, 2, 2, 2])

        with col1:
            st.write(f"**{user.email}**")
            st.caption(f"User ID: {user.id}")

        with col2:
            st.write("Admin" if user.is_admin else "User")

        with col3:
            if st.button(
                "Toggle Admin",
                key=f"toggle_admin_{user.id}",
                use_container_width=True
            ):
                toggle_admin(user.id)
                st.rerun()

        with col4:
            if st.button(
                "Delete",
                key=f"delete_user_{user.id}",
                use_container_width=True
            ):
                delete_user(user.id)
                st.rerun()

    st.divider()

    # ===========================================================
    #  UPLOADS SECTION
    # ===========================================================
    st.header("📄 Uploaded Config Files")

    db = SessionLocal()
    uploads = db.query(Upload).order_by(Upload.created_at.desc()).all()

    for item in uploads:
        with st.expander(f"📌 {item.filename} — User {item.user_id}"):
            st.code(item.content)

    st.divider()

    # ===========================================================
    #  AUDIT REPORTS SECTION
    # ===========================================================
    st.header("📊 Audit Reports")

    audits = db.query(AuditReport).order_by(AuditReport.created_at.desc()).all()
    db.close()

    for audit in audits:
        with st.expander(f"📝 Report ID {audit.id} — User {audit.user_id}"):
            st.json(audit.audit_json)

    st.success("Admin panel loaded successfully.")
