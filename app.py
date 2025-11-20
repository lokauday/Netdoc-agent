import os
import json
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from docx import Document

# ------------------------- API KEY -------------------------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ------------------------- PAGE CONFIG -------------------------
st.set_page_config(page_title="NetDoc AI", layout="wide")

# ------------------------- LOGO -------------------------
st.image("logo.png", width=180)
st.title("⚡ NetDoc AI — Autonomous Network Documentation Engine")

# ------------------------- FILE UPLOAD -------------------------
uploaded_files = st.file_uploader(
    "Upload one or more Cisco config files",
    type=["txt", "cfg", "log"],
    accept_multiple_files=True
)


# ================================================================
# AI HELPERS
# ================================================================

def ai_generate(prompt):
    """Send prompt to OpenAI and return text"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content


# ========================= AI PROMPTS ==========================

def generate_security_audit(config_text):
    prompt = f"""
You are a senior network security engineer.

Analyze the following Cisco configuration and produce a CLEAN, HUMAN-READABLE security audit:

- Weak passwords
- VLAN leaks
- STP issues
- Missing ACLs
- Outdated IOS versions
- CDP/LDP exposure
- EtherChannel issues
- DHCP problems

Config:
{config_text}

Return a formatted markdown report.
"""
    return ai_generate(prompt)


def generate_topology(config_text):
    prompt = f"""
You are a network topology engine.

From the configuration below, generate a CLEAN, minimal ASCII topology.

Only show:
- Device names
- Interfaces
- Connections

Config:
{config_text}

Return ONLY ASCII topology text.
"""
    return ai_generate(prompt)


# ================================================================
# EXPORT TO PDF (ReportLab)
# ================================================================

def export_pdf(markdown_text):
    buffer = "temp.pdf"
    styles = getSampleStyleSheet()
    story = [Paragraph(line.replace("  ", "&nbsp;"), styles['Normal'])
             for line in markdown_text.split("\n")]

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    doc.build(story)

    with open(buffer, "rb") as f:
        return f.read()


# ================================================================
# EXPORT TO DOCX
# ================================================================

def export_docx(markdown_text):
    doc = Document()
    for line in markdown_text.split("\n"):
        doc.add_paragraph(line)
    temp = "report.docx"
    doc.save(temp)
    return open(temp, "rb").read()


# ================================================================
# UI WORKFLOW
# ================================================================

if uploaded_files and st.button("Generate Report"):
    combined = ""

    for f in uploaded_files:
        combined += f"\n\n# FILE: {f.name}\n"
        combined += f.read().decode("utf-8")

    with st.spinner("Analyzing configuration…"):
        parsed = parse_config(combined)

    with st.spinner("Running security audit…"):
        audit_md = generate_security_audit(combined)

    with st.spinner("Generating topology…"):
        topology_md = generate_topology(combined)

    # Save for export tab
    st.session_state["parsed"] = parsed
    st.session_state["audit"] = audit_md
    st.session_state["topology"] = topology_md


# ================================================================
# TABS
# ================================================================

if "parsed" in st.session_state:

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📘 Overview", "🛡 Security Audit", "🌐 Topology", "📤 Export"])

    with tab1:
        st.subheader("📘 Device Documentation")
        st.json(st.session_state["parsed"])

    with tab2:
        st.subheader("🛡 Security Audit Report")
        st.markdown(st.session_state["audit"])

    with tab3:
        st.subheader("🌐 Network Topology Map")
        st.code(st.session_state["topology"])

    with tab4:
        st.subheader("📤 Export Options")

        full_export = (
            "# NetDoc AI Report\n\n"
            "## Overview\n"
            + json.dumps(st.session_state["parsed"], indent=2)
            + "\n\n## Security Audit\n"
            + st.session_state["audit"]
            + "\n\n## Topology\n"
            + st.session_state["topology"]
        )

        # PDF
        pdf_bytes = export_pdf(full_export)
        st.download_button("📄 Download PDF", pdf_bytes,
                           "NetDoc_Report.pdf", mime="application/pdf")

        # DOCX
        docx_bytes = export_docx(full_export)
        st.download_button("📝 Download DOCX", docx_bytes,
                           "NetDoc_Report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # HTML
        st.download_button("🌐 Download HTML",
                           full_export,
                           "NetDoc_Report.html",
                           mime="text/html")


else:
    st.info("Upload configuration files and click **Generate Report**.")
