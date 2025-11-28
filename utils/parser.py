import re
import json

# ============================================================
#  NETDOC AI — CONFIG PARSER (STABLE VERSION)
#  Extracts:
#   • Hostname
#   • Model / Version
#   • VLANs
#   • Interfaces
#   • CDP/LLDP Neighbors
#   • Routing Info
# ============================================================


def safe_value(v):
    """Normalize blank/None values for safety."""
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    return v


def parse_config(text):
    """
    Parse multi-device Cisco configuration.
    Return structured JSON safe for UI, Audit, Topology.
    """
    device = {
        "device_summary": {
            "hostname": None,
            "model": None,
            "serial": None,
            "os_version": None
        },
        "vlans": [],
        "interfaces": [],
        "neighbors": [],
        "routing_summary": {
            "dynamic_protocols": [],
            "default_route": None,
            "total_routes": None
        },
        "ascii_topology": ""
    }

    # ============================================================
    # Device Summary
    # ============================================================

    # Hostname
    m = re.search(r"hostname\s+(\S+)", text, re.I)
    if m:
        device["device_summary"]["hostname"] = m.group(1)

    # Model / Version
    m = re.search(r"Version\s+([\w\.\(\)\/]+)", text)
    if m:
        device["device_summary"]["os_version"] = m.group(1)

    # IOS Model
    m = re.search(r"System image file is \"(.+?)\"", text)
    if m:
        device["device_summary"]["model"] = m.group(1)

    # Serial Number
    m = re.search(r"Processor board ID\s+(\S+)", text)
    if m:
        device["device_summary"]["serial"] = m.group(1)

    # ============================================================
    # VLANs
    # ============================================================

    vlan_regex = r"^\s*(\d+)\s+([\w\-]+)\s+active"
    for vid, vname in re.findall(vlan_regex, text, re.M):
        device["vlans"].append({
            "vlan_id": vid,
            "name": vname,
            "ports": []
        })

    # ============================================================
    # Interfaces (IP, Status, VLAN)
    # ============================================================

    int_blocks = re.findall(
        r"(interface\s+[\w\/\.]+)([\s\S]*?)(?=\ninterface|\n!\n)",
        text,
        re.I
    )

    for header, body in int_blocks:
        name = header.split()[1]

        ip = None
        vlan = None
        desc = None

        # description
        m = re.search(r"description\s+(.+)", body)
        if m:
            desc = m.group(1).strip()

        # ip address
        m = re.search(r"ip address\s+([\d\.]+)\s+([\d\.]+)", body)
        if m:
            ip = m.group(1)

        # switchport access vlan
        m = re.search(r"switchport access vlan\s+(\d+)", body)
        if m:
            vlan = m.group(1)

        device["interfaces"].append({
            "name": name,
            "description": safe_value(desc),
            "ip_address": safe_value(ip),
            "vlan": safe_value(vlan),
            "status": "up" if "no shutdown" in body else "down",
            "protocol": "up"
        })

    # ============================================================
    # Neighbors (CDP/LLDP)
    # ============================================================

    cdp_regex = r"Device ID:\s*(\S+)[\s\S]*?Interface:\s*(\S+),\s*Port ID\s*\(outgoing port\):\s*(\S+)"
    for dev, local_if, neigh_if in re.findall(cdp_regex, text, re.I):
        device["neighbors"].append({
            "local_interface": local_if,
            "neighbor_device": dev,
            "neighbor_interface": neigh_if
        })

    # ============================================================
    # Routing Summary
    # ============================================================

    # dynamic protocols
    protocols = re.findall(r"router\s+(ospf|bgp|eigrp|isis)\s+[\d]+", text, re.I)
    device["routing_summary"]["dynamic_protocols"] = list(set([p.upper() for p in protocols]))

    # default route
    m = re.search(r"ip route 0.0.0.0 0.0.0.0\s+(\S+)", text)
    if m:
        device["routing_summary"]["default_route"] = m.group(1)

    # total routes
    m = re.search(r"Gateway of last resort.*", text)
    if m:
        device["routing_summary"]["total_routes"] = len(protocols)

    # ============================================================
    # ASCII Topology (Basic)
    # ============================================================

    topo = []
    for n in device["neighbors"]:
        topo.append(f"{n['local_interface']} --> {n['neighbor_device']}:{n['neighbor_interface']}")

    if topo:
        device["ascii_topology"] = "\n".join(topo)

    return device
