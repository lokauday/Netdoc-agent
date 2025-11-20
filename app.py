import os
import json
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config
from fpdf import FPDF


# ---------- LOAD OPENAI KEY ----------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


# ---------- BUILD MARKDOWN REPORT ----------
def build_markdown_report(data):
    md = []

    md.append("# Network Documentation Report\n")

    # DEVICE SUMMARY
    dev = data.get("device_summary", {})
    md.append("## Device Summary")
    md.append(f"- Hostname: {dev.get('hostname')}")
    md.append(f"- Model: {dev.get('model')}")
    md.append(f"- Serial: {dev.get('serial')}")
    md.append(f"- OS Version: {dev.get('os_version')}\n")

    # VLANS
    md.append("## VLANs")
    for v in data.get("vlans", []):
        md.append(f"- VLAN {v.get('vlan_id')}: {v.get('name')} (Ports: {', '.join(v.get('ports', []))})")

    # INTERFACES
    md.append("\n## Interfaces")
    for i in data.get("interfaces", []):
        md.append(f"- {i.get('name')} | IP: {i.get('ip_address')} | VLAN: {i.get('vlan')} | Status: {i.get('status')}")

    # NEIGHBORS
    md.append("\n## Neighbors (CDP/LLDP)")
    for n in data.get("neighbors", []):
        md.append(f"- {n.get('local_interface')} → {n.get('neighbor_device')} ({n.get('neighbor_interface')})")

    # ROUTING
    r = data.get("routing_summary", {})
    md.append("\n## Routing Summary")
    md.append(f"- Protocols: {', '.join(r.get('dynamic_protocols', []))}")
    md.append(f"- Default Route: {r.get('default_route')}")
    md.append(f"- Total Routes: {r.get('total_routes')}")

    # TOPOLOGY
    top = data.get("ascii_topology", "")
    if top:
        md.append("\n## Topology\n")
        md.append("```\n" + top + "\n```")

    return "\n".join(md)


# ---------- SAFE PDF GENERATOR ----------
def generate_pdf(markdown_text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    safe_text = markdown_text.replace("\t", "    ")
    safe_lines = safe_text.split("\n")

    for line in safe_lines:
        # wrap long lines safely
        if len(line) == 0:
            pdf.ln(5)
        else:
            while len(line) > 80:
                pdf.multi_cell(0, 5, line[:80])
                line = line[80:]
            pdf.multi_cell(0, 5, line)

    return pdf.output(dest="S").encode("latin1")


# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="NetDoc AI", layout="wide")

st.title("⚡ Network Documentation AI Agent")
st.write("Upload your switch/router configs and generate automated documentation.")

uploaded_files = st.file_uploader(
    "Upload config files",
    type=["txt", "log", "cfg"],
    accept_multiple_files=True
)

if st.button("Generate Documentation") and uploaded_files:
    combined = ""
    for f in uploaded_files:
        combined += f"\n\n# FILE: {f.name}\n"
        combined += f.read().decode("utf-8")

    with st.spinner("Analyzing configuration..."):
        result = parse_config(combined)

    st.success("Report generated successfully!")
    st.json(result)

    md_report = build_markdown_report(result)

    pdf_bytes = generate_pdf(md_report)

    st.download_button(
        "📥 Download PDF Report",
        data=pdf_bytes,
        file_name="Network_Documentation_Report.pdf",
        mime="application/pdf"
    )
