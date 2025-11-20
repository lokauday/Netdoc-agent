import os
import json
import textwrap
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config
from fpdf import FPDF

# ----------- LOAD API KEY FROM SECRETS OR LOCAL ENV -----------
# Priority: Streamlit secrets if deployed, otherwise .env in local dev.
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ----------- PDF GENERATOR (FPDF – Works on Streamlit Cloud) -----------
def generate_pdf(report_dict: dict) -> bytes:
    """
    Convert a nested dictionary into a PDF.
    The function prettifies the JSON, wraps long lines to a safe width,
    and breaks extremely long tokens into smaller pieces so that FPDF can render them.
    """
    # Prettify the dict to JSON string with indentation and newlines
    json_text = json.dumps(report_dict, indent=2)

    # Create the PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Courier", size=10)  # monospaced font improves alignment

    # Process each line in the prettified JSON
    for line in json_text.splitlines():
        # Break any single token that is too long (no spaces) into chunks of 50 characters
        tokens = []
        for token in line.split(" "):
            if len(token) > 50:
                tokens.extend([token[i:i+50] for i in range(0, len(token), 50)])
            else:
                tokens.append(token)
        safe_line = " ".join(tokens)

        # Wrap the line to about 90 characters; adjust width for page margins
        wrapped_lines = textwrap.wrap(safe_line, width=90) or [""]
        for wrapped in wrapped_lines:
            pdf.multi_cell(0, 5, wrapped)

    # Return PDF bytes
    return pdf.output(dest="S").encode("latin-1")

# ---------------- STREAMLIT UI ----------------

st.set_page_config(page_title="NetDoc AI", layout="wide")
st.title("⚡ Network Documentation AI Agent")
st.write("Upload your switch/router configs and generate automated documentation.")

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

    with st.spinner("Analyzing configuration…"):
        result = parse_config(combined)

    st.success("Report generated successfully!")
    st.json(result)

    # Convert report dictionary into a PDF using the robust generator
    pdf_bytes = generate_pdf(result)

    # Allow user to download the report
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name="Network_Documentation_Report.pdf",
        mime="application/pdf"
    )
