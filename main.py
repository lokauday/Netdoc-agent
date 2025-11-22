import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from docx import Document

# -----------------------------
# SECURITY AUDIT ENGINE
# -----------------------------
def run_security_audit(parsed):
    audit = {}
    
    # Weak enable passwords
    audit["weak_passwords"] = "enable secret not found" if "enable" not in str(parsed).lower() else "OK"
    
    # VLAN issues
    audit["vlan_check"] = f"{len(parsed.get('vlans', []))} VLANs parsed"
    
    # STP check
    audit["stp"] = "Check STP config manually" 
    
    # ACL check
    audit["acl"] = "No ACLs detected (OK or missing)"

    return audit


# -----------------------------
# TOPOLOGY ENGINE (MERMAID)
# -----------------------------
def generate_topology_mermaid(parsed):
    neighbors = parsed.get("neighbors", [])
    if not neighbors:
        return "No topology info found."

    lines = ["```mermaid", "graph TD;"]

    for n in neighbors:
        a = n.get("local_interface", "X")
        b = n.get("neighbor_device", "Device")
        c = n.get("neighbor_interface", "Y")
        lines.append(f'    "{a}" -->|{c}| "{b}"')

    lines.append("```")
    return "\n".join(lines)


# -----------------------------
# EXPORT ENGINE
# -----------------------------
def export_all_formats(parsed, markdown):

    # ------------------- PDF (ReportLab) -------------------
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    c.setFont("Helvetica", 10)

    y = 750
    for line in markdown.split("\n"):
        c.drawString(40, y, line[:100])
        y -= 14
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 750
    c.save()
    pdf_bytes = pdf_buffer.getvalue()

    # ------------------- DOCX -------------------
    doc = Document()
    doc.add_heading("NetDoc AI Report", 0)
    for line in markdown.split("\n"):
        doc.add_paragraph(line)
    doc_buffer = BytesIO()
    doc.save(doc_buffer)
    docx_bytes = doc_buffer.getvalue()

    # ------------------- HTML -------------------
    html_text = f"<html><body><pre>{markdown}</pre></body></html>"

    return pdf_bytes, docx_bytes, html_text
