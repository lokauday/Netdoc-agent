import streamlit as st
from database import SessionLocal, Upload
from utils.parser import parse_config
from ai_engine import generate_ai_docs
from datetime import datetime


# ============================================================
# UPLOAD PAGE
# ============================================================
def upload_page():
    st.title("📤 Upload Network Configuration")

    uploaded_file = st.file_uploader("Upload a config file (.txt, .cfg)", type=["txt", "cfg"])

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")

        # Parse
        parsed = parse_config(content)
        st.session_state.parsed = parsed

        # Save upload
        db = SessionLocal()
        rec = Upload(
            user_email=st.session_state.email,
            filename=uploaded_file.name,
            content=content,
            uploaded_at=datetime.utcnow()
        )
        db.add(rec)
        db.commit()
        db.close()

        st.success("File uploaded and parsed!")

        if st.button("Run Security Audit"):
            st.session_state.page = "Security Audit"
            st.rerun()

        if st.button("Generate Topology"):
            st.session_state.page = "Topology"
            st.rerun()

        if st.button("Generate AI Docs"):
            docs = generate_ai_docs(parsed)
            st.session_state.ai_docs = docs
            st.session_state.page = "AI Documentation"
            st.rerun()


# ============================================================
# UPLOAD HISTORY PAGE
# ============================================================
def uploads_history_page():
    st.title("📁 Upload History")

    db = SessionLocal()
    uploads = db.query(Upload).filter_by(user_email=st.session_state.email).all()
    db.close()

    if not uploads:
        st.info("No uploads yet.")
        return

    for u in uploads:
        st.write(f"**📄 {u.filename}** — uploaded {u.uploaded_at}")
        if st.button(f"Load {u.filename}", key=u.id):
            st.session_state.parsed = parse_config(u.content)
            st.session_state.page = "Upload Config"
            st.rerun()
