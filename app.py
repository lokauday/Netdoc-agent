import os
import json
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config

# ----------------------------------------------------------
#               LOAD API KEY (Local + Streamlit Cloud)
# ----------------------------------------------------------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ----------------------------------------------------------
#               PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(
    page_title="NetDoc AI",
    layout="wide",
    page_icon="⚡"
)

# ----------------------------------------------------------
#               GLOBAL DARK MODE CSS (Datadog Style)
# ----------------------------------------------------------
st.markdown("""
<style>

/* GLOBAL */
body, .stApp {
    background-color: #1a1d21;
    color: #f5f7fa;
    font-family: 'Inter', sans-serif;
}

/* TOP NAV BAR */
.navbar {
    background: #24272b;
    padding: 14px 22px;
    border-bottom: 1px solid #33363b;
    font-size: 23px;
    font-weight: 600;
    color: #5b9bff; /* Neon blue */
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #1e2125;
    border-right: 1px solid #2b2f34;
}

.sidebar-title {
    font-size: 18px;
    font-weight: 700;
    color: #8a64ff; /* Neon purple */
    padding-bottom: 5px;
}

.sidebar-item {
    font-size: 16px;
    color: #dee3ea;
}

/* SECTION HEADERS */
.section-header {
    font-size: 22px;
    font-weight: 700;
    color: #5b9bff;
    padding-bottom: 8px;
}

/* DARK CARDS */
.section-card {
    background: #24272b;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.45);
    margin-top: 18px;
    border: 1px solid #353941;
}

/* JSON BLOCKS */
.stJson > div {
    background-color: #1f2226 !important;
    border-radius: 10px;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    color: #dee3ea !important;
}

/* BUTTONS */
.stButton>button {
    background-color: #5b9bff;
    color: white;
    border-radius: 7px;
    border: none;
    padding: 8px 18px;
    font-weight: 600;
}
.stButton>button:hover {
    background-color: #8a64ff;
}

/* SUCCESS / INFO / WARNING */
.stAlert {
    background-color: #24272b !important;
    border-left: 6px solid #5b9bff !important;
    color: #dee3ea !important;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
#               TOP NAVIGATION BAR
# ----------------------------------------------------------
st.markdown(
    '<div class="navbar">⚡ NetDoc AI — Autonomous Network Documentation Engine</div>',
    unsafe_allow_html=True
)

# ----------------------------------------------------------
#               SIDEBAR MENU
# ----------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'>📁 Menu</div>", unsafe_allow_html=True)

    choice = st.radio(
        "",
        [
            "Dashboard",
            "Upload Configs",
            "Documentation",
            "Audit",
            "Topology",
            "Exports",
            "About"
        ]
    )

# ----------------------------------------------------------
#                     PAGES
# ----------------------------------------------------------

# ----------- Dashboard -----------
if choice == "Dashboard":
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📊 Dashboard Overview</div>", unsafe_allow_html=True)
    st.write("Welcome to NetDoc AI — upload configs to begin.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------- Upload Configs -----------
elif choice == "Upload Configs":

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📁 Upload Device Configurations</div>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload one or more config files",
        type=["txt", "cfg", "log"],
        accept_multiple_files=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_files and st.button("Generate Report"):
        combined = ""
        for f in uploaded_files:
            combined += f"\n\n# FILE: {f.name}\n"
            combined += f.read().decode("utf-8")

        with st.spinner("Processing your configs..."):
            result = parse_config(combined)

        st.success("Report generated successfully!")

        st.session_state["report"] = result
        st.session_state["markdown"] = json.dumps(result, indent=2)

# ----------- Documentation -----------
elif choice == "Documentation":

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📄 Generated Documentation</div>", unsafe_allow_html=True)

    if "report" in st.session_state:
        st.json(st.session_state["report"])
    else:
        st.info("Upload configs to generate documentation.")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------- Audit -----------
elif choice == "Audit":

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🛡 Security Audit</div>", unsafe_allow_html=True)

    if "report" in st.session_state:
        st.warning("Security audit engine will activate in Step C-27.")
    else:
        st.info("Upload configs first.")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------- Topology -----------
elif choice == "Topology":

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🌐 Network Topology</div>", unsafe_allow_html=True)

    if "report" in st.session_state:
        st.info("Topology diagram generation coming in Step C-28.")
    else:
        st.info("Upload configs first.")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------- Exports -----------
elif choice == "Exports":

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📤 Export Options</div>", unsafe_allow_html=True)

    if "markdown" in st.session_state:
        st.success("Export engine (PDF / DOCX / HTML) will activate in Step C-29.")
    else:
        st.info("Generate documentation to enable export options.")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------- About -----------
elif choice == "About":
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>ℹ️ About NetDoc AI</div>", unsafe_allow_html=True)
    st.write("""
    **NetDoc AI** automatically generates:

    - Device documentation  
    - VLAN summaries  
    - Interfaces, routing, neighbors  
    - Security audits  
    - Topology diagrams  
    - PDF, DOCX, HTML exports  

    Built for Network Engineers, MSPs, SOC teams, and IT departments.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
