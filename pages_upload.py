import streamlit as st
from auth import login_required
from database import SessionLocal, UploadedConfig
from utils.parser import parse_config
import json
from datetime import datetime


# ============================================================
#  UPLOAD PAGE
# ============================================================

def upload_page():
    login_required()
    st.title("📤 Upload Device Configurations")

    uploaded_files = st.file_uploader(
        "Upload router/switch configs",
        type=["txt", "cfg", "ios", "log"],
        accept_multiple_files=True
    )

    if st.button("Process Upload", use_container_width=True):
        if not uploaded_files:
            st.error("Please upload at least one file.")
            return

        db = SessionLocal()

        for f in uploaded_files:
            raw_text = f.read().decode(errors="ignore")

            parsed = parse_config(raw_text)
            parsed_json = json.dumps(parsed)

            record = UploadedConfig(
                org_id=st.session_state.org_id,
                file_name=f.name,
                content=raw_text,
                parsed_json=parsed_json
            )

            db.add(record)

        db.commit()
        db.close()

        st.success("Upload successful! Go to View Uploads.")

        st.session_state.page = "uploads"
        st.rerun()


# ============================================================
#  VIEW UPLOAD HISTORY
# ============================================================

def uploads_history_page():
    login_required()

    st.title("📚 Uploaded Configs")

    db = SessionLocal()
    rows = (
        db.query(UploadedConfig)
        .filter(UploadedConfig.org_id == st.session_state.org_id)
        .order_by(UploadedConfig.id.desc())
        .all()
    )
    db.close()

    if not rows:
        st.info("No uploads yet. Upload a config first.")
        return

    for r in rows:
        st.write("### 📄", r.file_name)
        st.caption(f"Uploaded: {r.id}")

        with st.expander("Show Raw Config"):
            st.code(r.content)

        with st.expander("Show Parsed JSON"):
            st.json(json.loads(r.parsed_json))


    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
