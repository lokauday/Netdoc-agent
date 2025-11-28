# ============================================================
#  NetDoc AI — Enterprise Edition
#  PARSER.PY — Cisco IOS / ASA / NX-OS basic parser
# ============================================================

import re
import json

def parse_config(text):
    """
    Basic deterministic config parser.
    This extracts hostname, VLANs, interfaces, CDP neighbors, etc.
    """

    if not text or text.strip() == "":
        return {}

    output = {
        "hostname": None,
        "vlans": [],
        "interfaces": {},
        "cdp_neighbors": {},
        "raw": text
    }

    # ------------------------------
    # HOSTNAME
    # ------------------------------
    match = re.search(r"hostname\s+(\S+)", text, re.IGNORECASE)
    if match:
        output["hostname"] = match.group(1)

    # ------------------------------
    # VLANs
    # ------------------------------
    vlans = re.findall(r"vlan\s+(\d+)", text, re.IGNORECASE)
    output["vlans"] = list(sorted(set(vlans)))

    # ------------------------------
    # INTERFACES
    # ------------------------------
    interfaces = re.findall(
        r"interface\s+(\S+)(.*?)\n!", text, re.DOTALL | re.IGNORECASE
    )
    for if_name, body in interfaces:
        output["interfaces"][if_name] = body.strip()

    # ------------------------------
    # CDP NEIGHBORS
    # (Simple extraction)
    # ------------------------------
    cdp = re.findall(
        r"Device ID:\s+(\S+).*?Interface:\s+(\S+),", text,
        re.DOTALL | re.IGNORECASE
    )
    for neighbor, iface in cdp:
        output["cdp_neighbors"][iface] = neighbor

    return output
