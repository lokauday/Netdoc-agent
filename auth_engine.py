# ===============================================================
#  NetDoc AI — AUTH ENGINE (Login, Signup, Admin Auth)
# ===============================================================

import bcrypt
import streamlit as st
from database import SessionLocal, User, Organization


# ---------------------------------------------------------------
# Create password hash
# ---------------------------------------------------------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


# ---------------------------------------------------------------
# Verify password
# ---------------------------------------------------------------
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ---------------------------------------------------------------
# Sign Up User
# ---------------------------------------------------------------
def signup_user(email: str, password: str):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        db.close()
        return False, "User already exists."

    # default org
    org = db.query(Organization).first()

    new_user = User(
        email=email,
        password_hash=hash_password(password),
        org_id=org.id,
        is_admin=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    return True, "Account created successfully."


# ---------------------------------------------------------------
# Login User
# ---------------------------------------------------------------
def login_user(email: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        db.close()
        return False, "User not found."

    if not verify_password(password, user.password_hash):
        db.close()
        return False, "Incorrect password."

    db.close()

    # Store session
    st.session_state["user_id"] = user.id
    st.session_state["email"] = user.email
    st.session_state["is_admin"] = bool(user.is_admin)
    st.session_state["logged_in"] = True

    return True, "Login successful."


# ---------------------------------------------------------------
# Logout User
# ---------------------------------------------------------------
def logout():
    for key in ["user_id", "email", "is_admin", "logged_in"]:
        if key in st.session_state:
            del st.session_state[key]


# ---------------------------------------------------------------
# Get current logged-in user object
# ---------------------------------------------------------------
def current_user():
    if "user_id" not in st.session_state:
        return None

    db = SessionLocal()
    user = db.query(User).filter(User.id == st.session_state["user_id"]).first()
    db.close()
    return user


# ---------------------------------------------------------------
# Admin-only access guard
# ---------------------------------------------------------------
def require_admin():
    if "is_admin" not in st.session_state or not st.session_state["is_admin"]:
        st.error("❌ Admin access required")
        st.stop()
