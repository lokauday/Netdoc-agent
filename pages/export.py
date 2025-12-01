import streamlit as st
from auth import login_required
from export_engine import export_all_formats
from combined_report import build_combined_pdf

def export_page():
    login_required()
    st.title("📦 Export Reports")

    parsed = st.session_state.get("parsed")
    audit = st.session_state.get("audit")
    ai_docs = st.session_state.get("ai_docs")
    topology = st.session_state.get("topology")

    if not parsed:
        st.warning("Upload a config first.")
        return

    st.subheader("Standard Exports")

    pdf, docx, html = export_all_formats(parsed)

    st.download_button("📄 Download PDF", pdf, file_name="report.pdf")
    st.download_button("📝 Download DOCX", docx, file_name="report.docx")
    st.download_button("🌐 Download HTML", html, file_name="report.html")

    st.write("---")
    st.subheader("Enterprise Combined Report (AI + Audit + Topology)")

    if st.button("🔵 Generate Combined Enterprise PDF"):
        if not audit or not ai_docs or not topology:
            st.error("Missing pieces! Run Audit, AI Docs, and Topology first.")
            return

        pdf_bytes = build_combined_pdf(
            parsed, audit, ai_docs, topology,
            org_name=st.session_state.get("org_name", "Unknown Org"),
            user_email=st.session_state.get("email", "unknown@domain.com")
        )

        st.download_button(
            "📄 Download Enterprise PDF Report",
            data=pdf_bytes,
            file_name="NetDoc_Enterprise_Report.pdf"
        )
