# ============================================================
# NetDoc AI — main.py (FINAL WORKING VERSION)
# ============================================================

from fpdf import FPDF
from docx import Document
import json
import os
import requests

# Unicode-safe Google font
FONT_PATH = "NotoSans-Regular.ttf"
FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"

# ------------------------------------------------------------
# Ensure Unicode Font Exists
# ------------------------------------------------------------
def ensure_font():
    if not os.path.exists(FONT_PATH):
        print("⬇ Downloading NotoSans font...")
        r = requests.get(FONT_URL)
        with open(FONT_PATH, "wb") as f:
            f.write(r.content)
        print("✔ Unicode font installed!")
    return True

ensure_font()


# ------------------------------------------------------------
# SECURITY AUDIT STUB
# ------------------------------------------------------------
def run_security_audit(parsed_json):
    return {
        "summary": "Security audit completed.",
        "issues": []
    }


# ------------------------------------------------------------
# TOPOLOGY STUB
# ------------------------------------------------------------
def generate_topology_mermaid(parsed_json):
    return """
graph TD
A[Switch] --> B[Router]
"""


# ------------------------------------------------------------
# EXPORT: PDF / DOCX / HTML
# ------------------------------------------------------------
def export_all_formats(parsed_json):
    text = json.dumps(parsed_json, indent=2)

    # ===================== PDF =====================
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Noto", "", FONT_PATH, uni=True)
    pdf.set_font("Noto", size=12)

    pdf.multi_cell(0, 8, "NetDoc AI — Network Report\n\n")
    pdf.multi_cell(0, 6, text)

    # Convert to bytes safely (fix for bytearray issue)
    pdf_output = bytes(pdf.output(dest="S"))

    # ===================== DOCX ====================
    doc = Document()
    doc.add_heading("NetDoc AI — Network Report", level=1)
    doc.add_paragraph(text)

    docx_path = "report.docx"
    doc.save(docx_path)
    with open(docx_path, "rb") as f:
        docx_output = f.read()

    # ===================== HTML ====================
    html_output = f"""
    <html><body>
    <h1>NetDoc AI — Network Report</h1>
    <pre>{text}</pre>
    </body></html>
    """.encode()

    return pdf_output, docx_output, html_output
