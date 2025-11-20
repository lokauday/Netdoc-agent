import os
import json
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config
import pdfkit

# -------------------- API KEY LOADING --------------------

api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# -------------------- PDF GENERATOR --------------------

def generate_pdf(markdown_text):
    html = f"""
    <html>
    <body style="font-family: Arial; padding:20px;">
    {markdown_text.replace('\n', '<br>')}
    </body>
    </html>
    """

    # wkhtmltopdf path (LOCAL ONLY — NOT USED IN CLOUD)
    path_wkhtmltopdf = r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    pdf_bytes = pdfkit.from_string(html, False, configuration=config)
    return pdf_bytes

# -------------------- STREAMLIT UI --------------------

st.set_page_config(page_title="NetDoc AI", layout="wide")

st.title("⚡ Network Documentation AI Agent")
st.write("Upload switch/router configs and generate instant documentation.")

uploaded_files = st.file_uploader(
    "Upload 1 or more config files",
    type=["txt", "log", "cfg"],
    accept_multiple_files=True
)

if st.button("Generate Documentation") and uploaded_files:
    combined = ""
    for f in uploaded_files:
        combined += f"\n\n# FILE: {f.name}\n"
        combined += f.read().decode("utf-8")

    with st.spinner("Analyzing configuration..."):
        data = parse_config(combined)

    st.success("Report generated!")

    # Show JSON results
    st.json(data)

    # -------------------- BUILD MARKDOWN REPORT --------------------
    md_report = "# Network Documentation Report\n\n"

    # Device Summary
    dev = data.get("device_summary", {})
    md_report += "## Device Summary\n"
    md_report += f"- Hostname: **{dev.get('hostname','')}**\n"
    md_report += f"- Model: {dev.get('model','')}\n"
    md_report += f"- Serial: {dev.get('serial','')}\n"
    md_report += f"- OS Version: {dev.get('os_version','')}\n\n"

    # VLANs
    md_report += "## VLANs\n"
    for v in data.get("vlans", []):
        md_report += f"- VLAN {v['vlan_id']} — {v['name']}\n"

    # ASCII topology
    md_report += "\n## Topology\n```\n"
    md_report += data.get("ascii_topology", "")
    md_report += "\n```\n"

    # -------------------- PDF DOWNLOAD BUTTON --------------------
    try:
        pdf_file = generate_pdf(md_report)
        st.download_button(
            "📥 Download PDF Report",
            data=pdf_file,
            file_name="Network_Documentation_Report.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"PDF generation failed: {e}")
        st.info("PDF generation only works on your local machine (wkhtmltopdf installed).")
