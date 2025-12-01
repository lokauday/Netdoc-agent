import streamlit as st
import bcrypt
from database import SessionLocal, User, Organization


# ============================================================
#  SESSION HELPERS
# ============================================================

def init_session():
    """Ensure all required session keys exist."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "org_id" not in st.session_state:
        st.session_state.org_id = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False


def login_required():
    """Simple middleware to protect pages."""
    init_session()
    if not st.session_state.logged_in:
        st.error("🚫 You must log in first.")
        st.stop()


def admin_required():
    """Middleware for admin-only pages."""
    login_required()
    if not st.session_state.is_admin:
        st.error("🚫 Admin access required.")
        st.stop()


# ============================================================
#  PASSWORD HELPERS
# ============================================================

def hash_password(password: str) -> str:
    """Return bcrypt hashed password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Check bcrypt password."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except:
        return False


# ============================================================
#  LOGIN LOGIC
# ============================================================

def attempt_login(email: str, password: str):
    """Validate login and initialize session."""

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return False, "User not found"

    if not verify_password(password, user.password_hash):
        return False, "Incorrect password"

    # Store session
    st.session_state.logged_in = True
    st.session_state.user_id = user.id
    st.session_state.org_id = user.org_id
    st.session_state.is_admin = user.is_admin

    db.close()
    return True, "Login successful"


# ============================================================
#  SIGNUP LOGIC
# ============================================================

def attempt_signup(org_name: str, email: str, password: str):
    """
    Create:
      - new Organization
      - new User (admin = True for first user)
    """

    db = SessionLocal()

    # Check duplicate user
    if db.query(User).filter(User.email == email).first():
        return False, "Email already exists"

    # Create org
    org = Organization(org_name=org_name)
    db.add(org)
    db.commit()
    db.refresh(org)

    # Create admin user for that org
    hashed = hash_password(password)

    user = User(
        email=email,
        password_hash=hashed,
        org_id=org.id,
        is_admin=True,
        role="admin",
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    return True, "Account created!"


# ============================================================
#  LOGOUT
# ============================================================

def logout():
    """Reset session state."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.org_id = None
    st.session_state.is_admin = False
