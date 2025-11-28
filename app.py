import os
import json
import streamlit as st
from main import run_security_audit, generate_topology_mermaid, export_all_formats
from utils.parser import parse_config

# -----------------------------------------------------------
# PAGE CONFIG — DATADOG DARK MODE
# -----------------------------------------------------------
st.set_page_config(
    page_title="NetDoc AI — Enterprise",
    page_icon="⚡",
    layout="wide"
)

# -----------------------------------------------------------
# GLOBAL CSS — SUPER CLEAN ENTERPRISE
# -----------------------------------------------------------
st.markdown("""
<style>

body {
    background-color: #1a1d21 !important;
    color: #e2e2e2 !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #141619 !important;
    border-right: 1px solid #2a2d33;
}

.sidebar-title {
    font-size: 22px;
    font-weight: 700;
    color: #5b9bff;
    margin-bottom: 10px;
}

/* MAIN HEADER */
.header {
    background-color: #1e2126;
    padding: 22px 30px;
    border-radius: 10px;
    border: 1px solid #2a2e35;
    margin-bottom: 25px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.4);
}

.header-title {
    font-size: 32px;
    color: #5b9bff;
    font-weight: 800;
}

.header-sub {
    font-size: 15px;
    color: #c3c3c3;
    margin-top: -5px;
}

/* CARD */
.card {
    background-color: #24272b;
    padding: 22px;
    border-radius: 12px;
    border: 1px solid #30343a;
    margin-bottom: 24px;
}

.card h3 {
    font-size: 22px;
    color: #8ab4ff;
    margin-bottom: 12px;
}

/* MERMAID */
.mermaid {
    background-color: #1f2125 !important;
    padding: 18px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'>📂 Navigation</div>", unsafe_allow_html=True)
    page = st.radio(
        "",
        ["Upload", "Documentation", "Security Audit", "Topology", "Exports", "About"]
    )

# -----------------------------------------------------------
# TOP HEADER BAR
# -----------------------------------------------------------
st.markdown("""
<div class="header">
    <div class="header-title">⚡ NetDoc AI — Enterprise Edition</div>
    <div class="header-sub">AI-powered network documentation with dark-mode Datadog-grade UI.</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# PAGE: UPLOAD
# -----------------------------------------------------------
if page == "Upload":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📁 Upload Configuration Files")

    uploaded_files = st.file_uploader(
        "Choose config files:",
        type=["txt", "log", "cfg"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Process Files"):
        all_text = ""
        for f in uploaded_files:
            all_text += f"\n\n# FILE: {f.name}\n"
            all_text += f.read().decode("utf-8")

        with st.spinner("Analyzing configurations..."):
            result = parse_config(all_text)

        st.session_state["report"] = result
        st.session_state["md"] = json.dumps(result, indent=2)

        st.success("✔ Successfully analyzed device configurations!")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------
# PAGE: DOCUMENTATION
# -----------------------------------------------------------
elif page == "Documentation":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📄 Generated Documentation")

    if "report" in st.session_state:
        st.json(st.session_state["report"])
    else:
        st.info("Upload configuration files first.")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------
# PAGE: SECURITY AUDIT
# -----------------------------------------------------------
elif page == "Security Audit":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🛡 Network Security Audit")

    if "report" not in st.session_state:
        st.info("Upload configuration files first.")
    else:
        audit = run_security_audit(st.session_state["report"])
        st.json(audit)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------
# PAGE: TOPOLOGY
# -----------------------------------------------------------
elif page == "Topology":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🌐 Network Topology Diagram")

    if "report" not in st.session_state:
        st.info("Upload configuration files first.")
    else:
        mermaid = generate_topology_mermaid(st.session_state["report"])
        st.markdown(f"```mermaid\n{mermaid}\n```")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------
# PAGE: EXPORTS
# -----------------------------------------------------------
elif page == "Exports":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📤 Export Report")

    if "md" not in st.session_state:
        st.info("Generate documentation first.")
    else:
        pdf, docx, html = export_all_formats(st.session_state["report"])

        st.download_button("📄 Download PDF", pdf, file_name="NetDoc_Report.pdf")
        st.download_button("📝 Download DOCX", docx, file_name="NetDoc_Report.docx")
        st.download_button("🌐 Download HTML", html, file_name="NetDoc_Report.html")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------
# PAGE: ABOUT
# -----------------------------------------------------------
elif page == "About":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### ℹ️ About NetDoc AI")

    st.write("Premium Datadog-style dark UI. Automated network documentation, audit, and topology engine.")
    st.image("logo.png", width=240)

    st.markdown("</div>", unsafe_allow_html=True)
