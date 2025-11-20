import os
import json
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config
from fpdf import FPDF
import textwrap

# ----------- LOAD API KEY ----------- #
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ----------- PDF GENERATOR (SAFE VERSION) ----------- #
def generate_pdf(markdown_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Use core font to avoid missing font errors
    pdf.set_font("Arial", size=10)

    # Split text into safe wrapped lines
    for line in markdown_text.split("\n"):

        # Replace tab + weird chars
        safe_line = line.replace("\t", "    ")

        # Wrap lines at 85 chars (prevents FPDFException)
        wrapped_lines = textwrap.wrap(safe_line, width=85)

        # If empty, just new line
        if not wrapped_lines:
            pdf.ln(5)
        else:
            for wrap in wrapped_lines:
                pdf.multi_cell(0, 5, wrap)

    # Output PDF as bytes (UTF-8 safe)
    try:
        return pdf.output(dest="S").encode("latin-1", errors="ignore")
    except:
        return pdf.output(dest="S").encode("utf-8", errors="ignore")


# ----------- STREAMLIT UI ----------- #

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
        combined += f.read().decode("utf-8", errors="ignore")

    with st.spinner("Analyzing configuration..."):
        result = parse_config(combined)

    st.success("Report generated successfully!")
    st.json(result)

    # Convert dict → readable Markdown string
    md_report = json.dumps(result, indent=2)

    # Generate PDF safely
    pdf_bytes = generate_pdf(md_report)

    st.download_button(
        "📥 Download PDF Report",
        data=pdf_bytes,
        file_name="Network_Documentation_Report.pdf",
        mime="application/pdf"
    )
