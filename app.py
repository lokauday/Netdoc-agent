import json
from io import BytesIO

import streamlit as st
import markdown as md_lib
from docx import Document

from main import build_prompt, call_openai, build_markdown_report

st.set_page_config(
    page_title="Network Documentation AI Agent",
    layout="wide",
)

st.title("⚡ Network Documentation AI Agent")
st.write(
    "Upload Cisco CLI outputs (`show run`, `show vlan brief`, "
    "`show ip interface brief`, `show cdp neighbors`, `show version`) "
    "and generate clean documentation."
)

# File uploader – support multiple files (multi-device)
uploaded_files = st.file_uploader(
    "Upload one or more config/CLI files",
    accept_multiple_files=True,
    type=["txt", "log", "cfg"],
    help="You can upload multiple files (one per device) – they will be combined for analysis.",
)

# Helper: build combined text from uploaded files
def combine_files(files) -> str:
    all_text = ""
    for f in files:
        content = f.read().decode("utf-8", errors="ignore")
        all_text += f"\n\n# FILE: {f.name}\n"
        all_text += content
    return all_text.strip()

# Helper: convert markdown → HTML
def markdown_to_html(md_text: str) -> str:
    return md_lib.markdown(md_text)

# Helper: convert markdown → DOCX (simple)
def markdown_to_docx_bytes(md_text: str) -> BytesIO:
    doc = Document()
    for line in md_text.splitlines():
        # Simple handling: headings vs normal text
        if line.startswith("# "):
            doc.add_heading(line[2:].strip(), level=1)
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=2)
        elif line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=3)
        else:
            doc.add_paragraph(line)
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

if uploaded_files:
    st.info(f"{len(uploaded_files)} file(s) uploaded. Click the button below to generate documentation.")

    if st.button("🚀 Generate Documentation"):
        with st.spinner("Calling AI and building report..."):
            combined = combine_files(uploaded_files)
            prompt = build_prompt(combined)
            json_text = call_openai(prompt)

            # Try to parse JSON
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError:
                st.error("The AI response was not valid JSON. Here is the raw output for debugging:")
                st.code(json_text, language="json")
            else:
                # Build markdown report
                md_report = build_markdown_report(data)

                st.success("✅ Documentation generated!")

                # Show report in the UI
                st.subheader("📄 Generated Report (Preview)")
                st.markdown(md_report)

                # Build export formats
                html_report = markdown_to_html(md_report)
                docx_bytes = markdown_to_docx_bytes(md_report)

                st.subheader("⬇️ Download Report")

                # Markdown
                st.download_button(
                    "Download as Markdown (.md)",
                    data=md_report,
                    file_name="network_report.md",
                    mime="text/markdown",
                )

                # HTML
                st.download_button(
                    "Download as HTML (.html)",
                    data=html_report,
                    file_name="network_report.html",
                    mime="text/html",
                )

                # DOCX
                st.download_button(
                    "Download as Word (.docx)",
                    data=docx_bytes,
                    file_name="network_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

                st.caption(
                    "💡 For PDF: open the HTML or DOCX in your browser/Word and use **Print → Save as PDF**."
                )
else:
    st.warning("Please upload at least one config/CLI file to begin.")
