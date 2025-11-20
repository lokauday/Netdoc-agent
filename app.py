import os
import json
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config
from fpdf import FPDF
import textwrap

# ----------- LOAD API KEY FROM SECRETS OR LOCAL ENV -----------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ----------- PDF GENERATOR (FPDF – Works on Streamlit Cloud) -----------
def generate_pdf(json_data):
    """
    Convert parsed JSON data into a PDF. Long words are broken up and lines are
    wrapped safely so that FPDF never encounters a word that is wider than the page.
    """
    # Pretty-print JSON
    text = json.dumps(json_data, indent=2)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Courier", size=10)  # monospace helps readability

    for line in text.split("\n"):
        # break up any extremely long 'word' (sequence without spaces)
        safe_words = []
        for word in line.split(" "):
            if len(word) > 80:
                # split long words into segments of 80 characters
                segments = [word[i:i+80] for i in range(0, len(word), 80)]
                safe_words.append(" ".join(segments))
            else:
                safe_words.append(word)
        safe_line = " ".join(safe_words)

        # wrap lines so they fit the PDF page; allow breaking long words
        wrapped_lines = textwrap.wrap(
            safe_line,
            width=90,
            break_long_words=True,
            break_on_hyphens=False
        )
        if not wrapped_lines:
            pdf.ln(5)
        else:
            for wrap_line in wrapped_lines:
                pdf.multi_cell(0, 5, wrap_line)
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

    with st.spinner("Analyzing configuration..."):
        result = parse_config(combined)

    st.success("Report generated successfully!")
    st.json(result)

    # Generate the PDF from the parsed result and provide a download button
    pdf_bytes = generate_pdf(result)
    st.download_button(
        "📥 Download PDF Report",
        data=pdf_bytes,
        file_name="Network_Documentation_Report.pdf",
        mime="application/pdf"
    )
