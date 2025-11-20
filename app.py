import os
import json
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config
from docx import Document
from docx.shared import Inches

# -------------------------------------------------------------
# LOAD API KEY
# -------------------------------------------------------------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# -------------------------------------------------------------
# AI UTILITIES
# -------------------------------------------------------------
def ai_generate_topology(text):
    prompt = f"""
You are a network topology generator.

Given the following multiple device configs:  
{text}

Return ONLY ASCII topology. Example:

[SW1 Gi1/0/1] ---- [CORE Gi0/1]
       |
[VLAN 10]

Return ONLY ASCII topology. No explanation.
"""
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return res.choices[0].message.content.strip()


def ai_security_audit(text):
    prompt = f"""
You are a senior network security auditor.

Perform a detailed security audit for all configs below:

{text}

Check:
- Password strength
- Enable secret
- Insecure protocols
- STP security
- DHCP snooping
- VLAN hopping
- BPDU Guard
- Port security
- Unused interfaces
- SSH vs Telnet
- SNMP security
- Outdated IOS
- Misconfigured trunks

Return a clean bullet list of findings + recommended fixes.
"""
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return res.choices[0].message.content


# -------------------------------------------------------------
# DOCX EXPORT
# -------------------------------------------------------------
def export_docx(json_data, topology, audit):
    doc = Document()

    # OPTIONAL LOGO (must be inside your repo)
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        doc.add_picture(logo_path, width=Inches(2))

    doc.add_heading("NetDoc AI – Network Documentation Report", level=1)

    doc.add_heading("1. Device Summary", level=2)
    doc.add_paragraph(json.dumps(json_data["device_summary"], indent=2))

    doc.add_heading("2. VLANs", level=2)
    doc.add_paragraph(json.dumps(json_data["vlans"], indent=2))

    doc.add_heading("3. Interfaces", level=2)
    doc.add_paragraph(json.dumps(json_data["interfaces"], indent=2))

    doc.add_heading("4. Neighbors", level=2)
    doc.add_paragraph(json.dumps(json_data["neighbors"], indent=2))

    doc.add_heading("5. Routing Summary", level=2)
    doc.add_paragraph(json.dumps(json_data["routing_summary"], indent=2))

    doc.add_heading("6. Topology", level=2)
    doc.add_paragraph(topology)

    doc.add_heading("7. Security Audit", level=2)
    doc.add_paragraph(audit)

    file_path = "Network_Report.docx"
    doc.save(file_path)
    return file_path


# -------------------------------------------------------------
# HTML EXPORT
# -------------------------------------------------------------
def export_html(json_data, topology, audit):
    html = f"""
    <html>
    <head>
        <title>NetDoc AI Report</title>
        <style>
            body {{ font-family: Arial; padding:20px; }}
            pre {{ background:#f0f0f0; padding:10px; }}
        </style>
    </head>
    <body>
        <h1>NetDoc AI – Network Documentation Report</h1>

        <h2>Device Summary</h2>
        <pre>{json.dumps(json_data["device_summary"], indent=2)}</pre>

        <h2>VLANs</h2>
        <pre>{json.dumps(json_data["vlans"], indent=2)}</pre>

        <h2>Interfaces</h2>
        <pre>{json.dumps(json_data["interfaces"], indent=2)}</pre>

        <h2>Neighbors</h2>
        <pre>{json.dumps(json_data["neighbors"], indent=2)}</pre>

        <h2>Routing Summary</h2>
        <pre>{json.dumps(json_data["routing_summary"], indent=2)}</pre>

        <h2>Topology</h2>
        <pre>{topology}</pre>

        <h2>Security Audit</h2>
        <pre>{audit}</pre>
    </body>
    </html>
    """
    with open("Network_Report.html", "w", encoding="utf-8") as f:
        f.write(html)

    return "Network_Report.html"


# -------------------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------------------
st.set_page_config(page_title="NetDoc AI", layout="wide")

st.title("⚡ NetDoc AI — Enterprise Network Documentation Generator")
st.write("Upload Cisco configs to generate full documentation + audit.")


uploaded_files = st.file_uploader(
    "Upload your .txt / .cfg / .log files",
    type=["txt", "cfg", "log"],
    accept_multiple_files=True
)


if st.button("Generate Documentation") and uploaded_files:

    combined = ""
    for f in uploaded_files:
        combined += f"\n\n# FILE: {f.name}\n"
        combined += f.read().decode("utf-8")

    with st.spinner("Parsing device configs..."):
        result = parse_config(combined)

    with st.spinner("Generating topology diagram..."):
        topology = ai_generate_topology(combined)

    with st.spinner("Running security audit..."):
        audit = ai_security_audit(combined)

    st.success("Done!")

    st.subheader("📌 Parsed JSON")
    st.json(result)

    st.subheader("📌 Topology (AI-Generated)")
    st.code(topology)

    st.subheader("📌 Security Audit (AI-Generated)")
    st.write(audit)

    # ---- EXPORT DOCX ----
    docx_file = export_docx(result, topology, audit)
    with open(docx_file, "rb") as f:
        st.download_button(
            "📥 Download DOCX Report",
            data=f,
            file_name="Network_Documentation_Report.docx"
        )

    # ---- EXPORT HTML ----
    html_file = export_html(result, topology, audit)
    with open(html_file, "rb") as f:
        st.download_button(
            "🌐 Download HTML Report",
            data=f,
            file_name="Network_Documentation_Report.html"
        )
