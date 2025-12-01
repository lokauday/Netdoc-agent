import streamlit as st
from auth import login_required
from security_engine import run_security_audit
from database import SessionLocal, AuditReport
import json

def audit_page():
    login_required()
    st.title("🛡 Security Audit Report")

    if "parsed" not in st.session_state:
        st.error("Please upload a configuration file first.")
        return

    parsed = st.session_state.parsed

    audit = run_security_audit(parsed)
    st.session_state.audit = audit

    st.json(audit)

    # Save audit result to DB
    db = SessionLocal()
    record = AuditReport(
        org_id=st.session_state.org_id,
        title="Security Audit",
        result_json=json.dumps(audit)
    )
    db.add(record)
    db.commit()
    db.close()
