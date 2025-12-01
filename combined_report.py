# ============================================================
#  COMBINED PDF REPORT ENGINE — NetDoc AI Enterprise
#  Security Audit + AI Docs + Topology + Parsed JSON
# ============================================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import json
import datetime
import html


# Load global font
FONT_PATH = "NotoSans-Regular.ttf"

try:
    pdfmetrics.registerFont(TTFont("Noto", FONT_PATH))
    BASE_FONT = "Noto"
except:
    BASE_FONT = "Helvetica"


# ------------------------------------------------------------
#  MAKE SECTION
# ------------------------------------------------------------
def section(title, content, style, elements):
    elements.append(Paragraph(f"<b>{title}</b>", style))
    elements.append(Spacer(1, 8))

    if isinstance(content, dict):
        content = json.dumps(content, indent=4)

    safe = html.escape(str(content)).replace("\n", "<br>")
    elements.append(Paragraph(safe, style))
    elements.append(Spacer(1, 16))


# ------------------------------------------------------------
#  MAIN COMBINED PDF BUILDER
# ------------------------------------------------------------
def build_combined_pdf(parsed, audit, ai_docs, topology, org_name, user_email):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title="NetDoc AI Enterprise Report"
    )

    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = BASE_FONT
    style.fontSize = 11

    elements = []

    # --------------------------------------------------------
    #  COVER PAGE
    # --------------------------------------------------------
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    cover = f"""
    <b><font size=16>NetDoc AI — Enterprise Report</font></b><br><br>
    <b>Organization:</b> {org_name}<br>
    <b>User:</b> {user_email}<br>
    <b>Generated:</b> {now}<br>
    <b>Device:</b> {parsed.get("hostname", "Unknown")}<br>
    """

    elements.append(Paragraph(cover, style))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<i>Automated by NetDoc AI</i>", style))
    elements.append(PageBreak())

    # --------------------------------------------------------
    #  SECTION 1 — Parsed Configuration
    # --------------------------------------------------------
    section("1. Parsed Configuration", parsed, style, elements)
    elements.append(PageBreak())

    # --------------------------------------------------------
    #  SECTION 2 — Security Audit Findings
    # --------------------------------------------------------
    section("2. Security Audit Findings", audit, style, elements)
    elements.append(PageBreak())

    # --------------------------------------------------------
    #  SECTION 3 — AI Summary",   
    # --------------------------------------------------------
    section("3. AI Summary", ai_docs.get("summary"), style, elements)

    # --------------------------------------------------------
    #  SECTION 4 — AI Explanation
    # --------------------------------------------------------
    section("4. AI Explanation", ai_docs.get("explanation"), style, elements)

    # --------------------------------------------------------
    #  SECTION 5 — AI Best Practices
    # --------------------------------------------------------
    section("5. AI Best Practices", ai_docs.get("best_practices"), style, elements)

    # --------------------------------------------------------
    #  SECTION 6 — AI Recommendations
    # --------------------------------------------------------
    section("6. AI Recommendations", ai_docs.get("recommendations"), style, elements)
    elements.append(PageBreak())

    # --------------------------------------------------------
    #  SECTION 7 — Topology Diagram (Mermaid)
    # --------------------------------------------------------
    elements.append(Paragraph("<b>7. Network Topology Diagram</b>", style))
    elements.append(Spacer(1, 12))

    safe_topo = html.escape(topology).replace("\n", "<br>")
    elements.append(Paragraph(f"<pre>{safe_topo}</pre>", style))

    # --------------------------------------------------------
    #  BUILD PDF
    # --------------------------------------------------------
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
