import json
from io import BytesIO

import streamlit as st
import markdown as md
from docx import Document

from main import build_prompt, call_openai, build_markdown_report


st.set_page_config(
    page_title="NetDoc Agent",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Network Documentation AI Agent")
st.write("Upload Cisco configs (`show run`, `show vlan`, `show ip int brief`, `show cdp nei`, etc.) and generate a full documentation report.")


uploaded_files = st.file_uploader(
    "Upload one or more CLI output files",
    type=["txt", "log", "cfg"],
    accept_multiple_files=True,
    help="You can export 'show run' and other commands to text files and upload them here.",
)

generate_button = st.button("🚀 Generate Documentation")


if uploaded_files and generate_button:
    # Combine all files into one big text
    all_text = ""
    for f in uploaded_files:
        file_content = f.read().decode("utf-8", errors="ignore")
        all_text += f"\n\n# FILE: {f.name}\n"
        all_text += file_content

    with st.spinner("Calling AI and generating documentation..."):
        prompt = build_prompt(all_text)
        json_text = call_openai(prompt)
        data = json.loads(json_text)
        md_report = build_markdown_report(data)

    st.success("✅ Documentation generated!")

    # Show the markdown report in the app
    st.subheader("📄 Generated Report (Preview)")
    st.markdown(md_report)

    # Prepare downloads
    # 1) Markdown
    st.download_button(
        "⬇️ Download Markdown (.md)",
        data=md_report,
        file_name="network_documentation.md",
        mime="text/markdown",
    )

    # 2) HTML (convert markdown to HTML)
    html_report = md.markdown(md_report)

    st.download_button(
        "⬇️ Download HTML (.html)",
        data=html_report,
        file_name="network_documentation.html",
        mime="text/html",
    )

    # 3) DOCX (Word)
    docx_buffer = BytesIO()
    document = Document()
    for line in md_report.splitlines():
        document.add_paragraph(line)
    document.save(docx_buffer)
    docx_buffer.seek(0)

    st.download_button(
        "⬇️ Download Word (.docx)",
        data=docx_buffer,
        file_name="network_documentation.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    st.info("💡 To get a PDF, open the HTML or DOCX file and use **Print → Save as PDF** from your browser or Word.")
else:
    st.caption("Upload at least one config file and click **Generate Documentation**.")
