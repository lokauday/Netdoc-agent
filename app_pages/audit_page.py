import streamlit as st
from auth_engine import current_user
from utils.parser import parse_config
from main import run_security_audit, generate_topology_mermaid, export_all_formats


def goto(page):
    st.session_state.page = page
    st.rerun()


def audit_page():
    user = current_user()
    if not user:
        goto("login")

    st.sidebar.title("📌 Navigation")
    if st.sidebar.button("Dashboard"):
        goto("dashboard")
    if st.sidebar.button("Topology Map"):
        goto("topology")
    if st.sidebar.button("Logout"):
        goto("login")

    st.title("🔎 Security Audit")

    uploaded = st.file_uploader("Upload Configuration File", type=["txt", "cfg", "conf"])

    if uploaded:
        config_text = uploaded.read().decode()

        parsed = parse_config(config_text)
        audit = run_security_audit(parsed["raw"])
        topo = generate_topology_mermaid(parsed["raw"])
        exports = export_all_formats(audit, topo)

        st.subheader("Audit Result")
        st.json(audit)

        st.subheader("Topology")
        st.markdown(f"```mermaid\n{topo}\n```")

        st.subheader("Download Reports")
        st.download_button("JSON", exports["json"], file_name="audit.json")
        st.download_button("Markdown", exports["markdown"], file_name="audit.md")
        st.download_button("Text", exports["txt"], file_name="audit.txt")
        st.download_button("HTML", exports["html"], file_name="audit.html")

    if st.button("Back"):
        goto("dashboard")
