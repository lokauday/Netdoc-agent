import re


# ============================================================
#  SECURITY AUDIT ENGINE — returns dict
# ============================================================

def run_security_audit(parsed):
    """
    parsed = dict from parser:
      {
        hostname: str
        vlans: [...]
        interfaces: {...}
        cdp_neighbors: {...}
        raw: "full config text"
      }
    """

    raw = parsed.get("raw", "")
    interfaces = parsed.get("interfaces", {})
    vlans = parsed.get("vlans", [])
    neighbors = parsed.get("cdp_neighbors", {})

    audit = {
        "hostname": parsed.get("hostname", "Unknown"),
        "weak_passwords": [],
        "aaa_misconfig": [],
        "unused_interface_issues": [],
        "vlan_issues": [],
        "stp_issues": [],
        "cdp_issues": [],
        "acl_issues": [],
        "summary": []
    }

    # ============================================================
    # 1) Weak Passwords
    # ============================================================
    weak_pw_patterns = [
        r"password\s+\d?\s*cisco",
        r"password\s+\d?\s*admin",
        r"password\s+\d?\s*1234",
        r"username\s+\w+\s+password",
        r"enable password",
        r"enable secret 5\s*\$1\$"  # weak MD5
    ]

    for pattern in weak_pw_patterns:
        matches = re.findall(pattern, raw, flags=re.IGNORECASE)
        for m in matches:
            audit["weak_passwords"].append(m)

    if not audit["weak_passwords"]:
        audit["weak_passwords"] = ["OK"]


    # ============================================================
    # 2) AAA Misconfiguration
    # ============================================================
    if "aaa new-model" not in raw.lower():
        audit["aaa_misconfig"].append("AAA not enabled")

    if "tacacs" not in raw.lower() and "radius" not in raw.lower():
        audit["aaa_misconfig"].append("No TACACS+/RADIUS configured")

    if not audit["aaa_misconfig"]:
        audit["aaa_misconfig"] = ["OK"]


    # ============================================================
    # 3) Unused Interfaces Not Shutdown
    # ============================================================
    for intf, data in interfaces.items():
        if "admin_down" not in data and data.get("status") == "up" and data.get("protocol") == "down":
            audit["unused_interface_issues"].append(f"{intf} admin UP but not used")

    if not audit["unused_interface_issues"]:
        audit["unused_interface_issues"] = ["OK"]


    # ============================================================
    # 4) VLAN & Trunk Issues
    # ============================================================
    default_vlans = ["1", "1002", "1003", "1004", "1005"]

    for v in vlans:
        if str(v) in default_vlans:
            audit["vlan_issues"].append(f"Default VLAN {v} still active")

    if "switchport access vlan 1" in raw.lower():
        audit["vlan_issues"].append("Interfaces using VLAN 1")

    if not audit["vlan_issues"]:
        audit["vlan_issues"] = ["OK"]


    # ============================================================
    # 5) STP Security
    # ============================================================
    if "spanning-tree portfast" not in raw.lower():
        audit["stp_issues"].append("Missing PortFast")

    if "bpduguard enable" not in raw.lower():
        audit["stp_issues"].append("No BPDU Guard")

    if not audit["stp_issues"]:
        audit["stp_issues"] = ["OK"]


    # ============================================================
    # 6) CDP Exposure
    # ============================================================
    if neighbors and "no cdp run" not in raw.lower():
        audit["cdp_issues"].append("CDP enabled — exposes device info")

    if not audit["cdp_issues"]:
        audit["cdp_issues"] = ["OK"]


    # ============================================================
    # 7) ACL Gaps
    # ============================================================
    if "access-list" not in raw.lower():
        audit["acl_issues"].append("No ACLs configured anywhere")

    if "line vty" in raw.lower() and "access-class" not in raw.lower():
        audit["acl_issues"].append("VTY lines allow open access (no ACL)")

    if not audit["acl_issues"]:
        audit["acl_issues"] = ["OK"]


    # ============================================================
    # SUMMARY
    # ============================================================
    for section, items in audit.items():
        if section == "summary": 
            continue
        if items != ["OK"]:
            audit["summary"].append(f"{section}: {len(items)} issues")
        else:
            audit["summary"].append(f"{section}: OK")

    return audit
