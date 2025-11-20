import os
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config
from fpdf import FPDF
import textwrap

# ----------- LOAD API KEY FROM SECRETS OR LOCAL ENV -----------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ----------- Helpers to turn dict -> lines and split long words -----------
def dict_to_lines(data, indent=0):
    """Convert nested dict/list structures into a list of lines."""
    lines = []
    indent_str = " " * (indent * 2)
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{indent_str}{key}:")
                lines.extend(dict_to_lines(value, indent + 1))
            else:
                lines.append(f"{indent_str}{key}: {value}")
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            lines.append(f"{indent_str}-")
            lines.extend(dict_to_lines(item, indent + 1))
    else:
        lines.append(f"{indent_str}{data}")
    return lines

def split_long_words(text, length=40):
    """Insert spaces into long continuous words."""
    result = []
    for word in text.split(" "):
        if len(word) > length:
            # break the word into chunks of 'length' characters
            chunks = [word[i:i+length] for i in range(0, len(word), length)]
            result.append(" ".join(chunks))
        else:
            result.append(word)
    return " ".join(result)

def generate_pdf(data):
    """Create a PDF from the nested dict/list structure."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Courier", size=10)

    lines = dict_to_lines(data)
    for line in lines:
        # Break long words and then wrap
        safe_line = split_long_words(line, length=40)
        wrapped_lines = textwrap.wrap(safe_line, width=50, break_long_words=False)
        for seg in wrapped_lines:
            pdf.multi_cell(0, 6, seg)
    # Return bytes
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

    # Generate PDF
    pdf_bytes = generate_pdf(result)
    st.download_button(
        "📥 Download PDF Report",
        data=pdf_bytes,
        file_name="Network_Documentation_Report.pdf",
        mime="application/pdf"
    )
