# ===============================================================
#  NetDoc AI — Core Engine (Audit + Topology + Export)
# ===============================================================

import json
import re


# =====================================================================
#  SECURITY AUDIT ENGINE
# =====================================================================
def run_security_audit(config_text: str) -> dict:
    """
    Analyze network configuration text and generate a structured audit report.
    """

    issues = []
    warnings = []
    info = []

    # -------------------------------------------------------------
    # PASSWORD SECURITY CHECK
    # -------------------------------------------------------------
    if "username" in config_text and "password" in config_text:
        if "password 0" in config_text or "password " in config_text:
            issues.append("⚠️ Plain-text password detected. Use secret 5 or 9 hashing.")

    # -------------------------------------------------------------
    # VLAN CHECKS
    # -------------------------------------------------------------
    vlan_matches = re.findall(r"vlan (\d+)", config_text)
    if not vlan_matches:
        warnings.append("No VLANs detected in configuration.")
    else:
        info.append(f"Detected VLANs: {', '.join(vlan_matches)}")

    # -------------------------------------------------------------
    # STP CHECKS
    # -------------------------------------------------------------
    if "spanning-tree" not in config_text:
        warnings.append("STP not found — risky for L2 loops.")
    else:
        if "spanning-tree portfast" not in config_text:
            warnings.append("PortFast missing on access ports.")

    # -------------------------------------------------------------
    # OSPF CHECKS
    # -------------------------------------------------------------
    if "router ospf" in config_text:
        info.append("OSPF detected.")
        if "passive-interface default" not in config_text:
            warnings.append("OSPF passive-interface default not configured.")
    else:
        warnings.append("OSPF not found.")

    # -------------------------------------------------------------
    # BGP CHECKS
    # -------------------------------------------------------------
    if "router bgp" in config_text:
        info.append("BGP detected.")
        if "neighbor" not in config_text:
            issues.append("BGP configured but no neighbors found.")
    else:
        warnings.append("BGP not found.")

    # -------------------------------------------------------------
    # ACCESS-LIST CHECKS
    # -------------------------------------------------------------
    if "access-list" not in config_text:
        warnings.append("No ACLs found — verify security posture.")

    # -------------------------------------------------------------
    # FINAL STRUCTURED REPORT
    # -------------------------------------------------------------
    return {
        "issues": issues,
        "warnings": warnings,
        "info": info
    }


# =====================================================================
#  TOPOLOGY GENERATOR (Mermaid)
# =====================================================================
def generate_topology_mermaid(config_text: str) -> str:
    """
    Create a Mermaid topology diagram from config.
    """

    devices = set()
    links = []

    # Detect hostnames
    hostname_match = re.search(r"hostname (\S+)", config_text)
    main_device = hostname_match.group(1) if hostname_match else "Device"

    devices.add(main_device)

    # Basic link detection for CDP/LLDP neighbors
    neighbor_matches = re.findall(r"neighbor (\S+)", config_text)
    for n in neighbor_matches:
        devices.add(n)
        links.append((main_device, n))

    # Build Mermaid graph
    mermaid = ["graph TD"]

    for d in devices:
        mermaid.append(f"    {d}")

    for a, b in links:
        mermaid.append(f"    {a} --> {b}")

    return "\n".join(mermaid)


# =====================================================================
#  EXPORT ENGINE
# =====================================================================
def export_all_formats(audit: dict, topology: str) -> dict:
    """
    Export audit + topology into multiple ready formats.
    """

    audit_json = json.dumps(audit, indent=4)

    md_content = (
        "# NetDoc AI — Audit Report\n\n"
        "## Issues\n"
        + "\n".join(f"- {i}" for i in audit["issues"]) + "\n\n"
        "## Warnings\n"
        + "\n".join(f"- {w}" for w in audit["warnings"]) + "\n\n"
        "## Info\n"
        + "\n".join(f"- {i}" for i in audit["info"]) + "\n\n"
        "## Topology Diagram (Mermaid)\n"
        "```mermaid\n" + topology + "\n```\n"
    )

    txt_content = (
        "NetDoc AI — Audit Report\n\n"
        "Issues:\n" + "\n".join(audit["issues"]) + "\n\n"
        "Warnings:\n" + "\n".join(audit["warnings"]) + "\n\n"
        "Info:\n" + "\n".join(audit["info"]) + "\n\n"
        "Topology:\n" + topology + "\n"
    )

    html_content = (
        "<h1>NetDoc AI — Audit Report</h1>"
        "<h2>Issues</h2><ul>"
        + "".join(f"<li>{i}</li>" for i in audit["issues"]) +
        "</ul><h2>Warnings</h2><ul>"
        + "".join(f"<li>{w}</li>" for w in audit["warnings"]) +
        "</ul><h2>Info</h2><ul>"
        + "".join(f"<li>{i}</li>" for i in audit["info"]) +
        "</ul><h2>Topology Diagram</h2>"
        f"<pre>{topology}</pre>"
    )

    return {
        "json": audit_json,
        "markdown": md_content,
        "txt": txt_content,
        "html": html_content
    }
