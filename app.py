import os
import json
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config
from main import run_security_audit, generate_topology_mermaid, export_all_formats

# -----------------------------
# LOAD API KEY
# -----------------------------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# -----------------------------
# PAGE CONFIG (DARK MODE)
# -----------------------------
st.set_page_config(
    page_title="NetDoc AI",
    layout="wide",
    page_icon="⚡"
)

# -----------------------------
# DATADOG DARK MODE CSS
# -----------------------------
st.markdown("""
<style>

body {
    background-color: #1a1d21 !important;
}

.reportview-container {
    background: #1a1d21 !important;
}

.block-container {
    background-color: #1a1d21 !important;
    padding-top: 2rem;
}

h1, h2, h3, h4, h5, h6, p, label, span {
    color: #e8e9eb !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #16181c !important;
    border-right: 1px solid #2e3238;
}

.sidebar-title {
    font-size: 22px;
    font-weight: 700;
    color: #5b9bff;
    margin-bottom: 10px;
}

/* Top Nav */
.navbar {
    width: 100%;
    padding: 14px 20px;
    background-color: #16181c;
    border-bottom: 1px solid #2e3238;
    color: #5b9bff;
    font-size: 24px;
    font-weight: bold;
}

/* Cards */
.card {
    background: #24272b;
    padding: 18px;
    border-radius: 10px;
    border: 1px solid #2e3238;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# TOP NAV BAR
# -----------------------------
st.markdown('<div class="navbar">⚡ NetDoc AI — Datadog Dark Mode</div>', unsafe_allow_html=True)

# -----------------------------
# SIDEBAR MENU
# -----------------------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'>📁 Navigation</div>", unsafe_allow_html=True)

    menu = st.radio(
        "",
        ["Upload", "Documentation", "Security Audit", "Topology", "Exports", "About"]
    )

# -----------------------------
# UPLOAD PAGE
# -----------------------------
if menu == "Upload":
    st.header("📁 Upload Configuration Files")

    uploaded_files = st.file_uploader(
        "Upload config files:",
        type=["txt", "cfg", "log"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Process Configs"):
        combined = ""

        for f in uploaded_files:
            combined += f"\n\n# FILE: {f.name}\n"
            combined += f.read().decode("utf-8")

        with st.spinner("Processing configs with AI..."):
            result = parse_config(combined)

        st.session_state["doc"] = result
        st.session_state["markdown"] = json.dumps(result, indent=2)

        st.success("Documentation generated!")

# -----------------------------
# DOCUMENTATION PAGE
# -----------------------------
elif menu == "Documentation":
    st.header("📄 Generated Documentation")

    if "doc" not in st.session_state:
        st.warning("Upload configs first.")
    else:
        st.json(st.session_state["doc"])

# -----------------------------
# SECURITY AUDIT PAGE
# -----------------------------
elif menu == "Security Audit":
    st.header("🛡 Security Audit")

    if "doc" not in st.session_state:
        st.warning("Upload configs first.")
    else:
        audit = run_security_audit(st.session_state["doc"])
        st.json(audit)

# -----------------------------
# TOPOLOGY PAGE
# -----------------------------
elif menu == "Topology":
    st.header("🌐 Network Topology (Mermaid Diagram)")

    if "doc" not in st.session_state:
        st.warning("Upload configs first.")
    else:
        diagram = generate_topology_mermaid(st.session_state["doc"])
        st.markdown(diagram)

# -----------------------------
# EXPORT PAGE
# -----------------------------
elif menu == "Exports":
    st.header("📤 Export Documentation")

    if "markdown" not in st.session_state:
        st.warning("Generate documentation first.")
    else:
        pdf_bytes, docx_bytes, html_text = export_all_formats(
            st.session_state["doc"],
            st.session_state["markdown"]
        )

        st.download_button("📄 Download PDF", pdf_bytes, file_name="NetDoc.pdf")
        st.download_button("📝 Download DOCX", docx_bytes, file_name="NetDoc.docx")
        st.download_button("🌐 Download HTML", html_text, file_name="NetDoc.html")

# -----------------------------
# ABOUT PAGE
# -----------------------------
elif menu == "About":
    st.header("ℹ️ About NetDoc AI")
    st.write("AI-powered network documentation engine with dark-mode UI.")
    st.image("logo.png", width=200)
