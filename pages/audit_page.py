import streamlit as st
from auth_engine import current_user
from utils.parser import parse_config
from main import run_security_audit, generate_topology_mermaid, export_all_formats
from exports.exporter import export_pdf, export_docx, export_zip


def audit_page():
    user = current_user()
    if not user:
        st.warning("You must be logged in.")
        st.stop()

    st.title("🔎 Configuration Security Audit")

    uploaded = st.file_uploader("Upload configuration file", type=["txt", "cfg", "conf"])

    if uploaded:
        config_text = uploaded.read().decode()

        parsed = parse_config(config_text)
        audit = run_security_audit(parsed["raw"])
        topology = generate_topology_mermaid(parsed["raw"])
        exports = export_all_formats(audit, topology)

        st.subheader("Audit Report")
        st.json(audit)

        st.subheader("Topology Diagram")
        st.markdown(f"```mermaid\n{topology}\n```")

        st.subheader("Download Reports")

        # Default exports
        st.download_button("JSON", exports["json"], file_name="audit.json")
        st.download_button("Markdown", exports["markdown"], file_name="audit.md")
        st.download_button("Text", exports["txt"], file_name="audit.txt")
        st.download_button("HTML", exports["html"], file_name="audit.html")

        # Advanced exports
        st.download_button("PDF", export_pdf(audit, topology), file_name="audit.pdf")
        st.download_button("DOCX", export_docx(audit, topology), file_name="audit.docx")
        st.download_button("ZIP Bundle", export_zip(audit, topology, parsed["raw"]), file_name="audit_bundle.zip")
