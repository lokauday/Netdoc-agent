# ============================================================
#  SECURITY ENGINE — STATIC AUDIT (No AI Required)
#  Produces structured findings used in UI + PDF exports
# ============================================================

import re

def find_weak_passwords(raw_text):
    patterns = [
        r"password 0 \S+",
        r"username \S+ password",
        r"enable password \S+",
        r"enable secret \S+",
        r"password \S+",
        r"secret \S+",
    ]

    weak_keywords = ["cisco", "admin", "1234", "12345", "password"]

    found = []

    for p in patterns:
        matches = re.findall(p, raw_text, re.IGNORECASE)
        for m in matches:
            # Check if weak phrase appears
            if any(w in m.lower() for w in weak_keywords):
                found.append(m)

    return list(set(found))


def find_missing_aaa(raw_text):
    if "aaa new-model" not in raw_text.lower():
        return "AAA is NOT enabled"
    return "OK"


def find_stp_issues(raw_text):
    issues = []
    if "spanning-tree portfast" not in raw_text.lower():
        issues.append("No STP PortFast detected")

    if "bpduguard" not in raw_text.lower():
        issues.append("No BPDU Guard detected")

    return issues


def find_default_vlan(raw_text):
    issues = []
    # default VLAN has risks
    vlan10 = re.findall(r"interface vlan ?1", raw_text, re.IGNORECASE)
    if vlan10:
        issues.append("VLAN 1 active — not recommended")

    trunks = re.findall(r"switchport trunk allowed vlan.*1", raw_text)
    if trunks:
        issues.append("VLAN 1 allowed on trunk")

    return issues


def find_no_logging(raw_text):
    if "logging buffered" not in raw_text.lower():
        return "Logging not configured"
    return "OK"


def find_cdp_exposure(raw_text):
    if "cdp run" in raw_text.lower():
        return "CDP is enabled — may expose topology"
    return "OK"


def find_interface_problems(parsed):
    problems = []

    intfs = parsed.get("interfaces", {})

    for name, data in intfs.items():
        if data.get("status") == "down":
            problems.append(f"{name} is down")

        if data.get("ip") in ["0.0.0.0", None]:
            problems.append(f"{name} missing IP")

    return problems


# -------------------------------------------------------------
# MAIN AUDIT WRAPPER
# -------------------------------------------------------------
def run_security_audit(parsed):
    raw = parsed.get("raw", "")

    audit = {
        "weak_passwords": find_weak_passwords(raw),
        "aaa_status": find_missing_aaa(raw),
        "stp_issues": find_stp_issues(raw),
        "default_vlan_risks": find_default_vlan(raw),
        "logging": find_no_logging(raw),
        "cdp_exposure": find_cdp_exposure(raw),
        "interface_warnings": find_interface_problems(parsed),
    }

    return audit
