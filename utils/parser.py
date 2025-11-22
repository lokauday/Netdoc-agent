import re
import json

def parse_config(text):
    data = {
        "device_summary": {},
        "vlans": [],
        "interfaces": [],
        "neighbors": [],
        "routing_summary": {},
        "ascii_topology": ""
    }

    # --------------------- Hostname ---------------------
    m = re.search(r"hostname (\S+)", text)
    data["device_summary"]["hostname"] = m.group(1) if m else None

    # --------------------- Model ---------------------
    m = re.search(r"Model number\s+(\S+)", text)
    data["device_summary"]["model"] = m.group(1) if m else None

    # --------------------- Serial ---------------------
    m = re.search(r"System serial number\s+(\S+)", text)
    data["device_summary"]["serial"] = m.group(1) if m else None

    # --------------------- VLAN Parsing ---------------------
    vlan_blocks = re.findall(r"vlan (\d+)\n\s*name (\S+)", text)
    for vid, name in vlan_blocks:
        data["vlans"].append({"vlan_id": vid, "name": name, "ports": []})

    # --------------------- Interface VLANs ---------------------
    int_blocks = re.findall(
        r"interface Vlan(\d+)[\s\S]+?ip address (\S+)",
        text
    )
    for vlan, ipaddr in int_blocks:
        data["interfaces"].append({
            "name": f"Vlan{vlan}",
            "description": None,
            "ip_address": ipaddr,
            "vlan": vlan,
            "status": "up",
            "protocol": "up"
        })

    # --------------------- CDP Neighbors ---------------------
    cdp = re.findall(
        r"Device ID: (\S+)[\s\S]+?Interface: (\S+), Port ID \(outgoing port\): (\S+)",
        text
    )
    for neigh, local_if, neigh_if in cdp:
        data["neighbors"].append({
            "local_interface": local_if,
            "neighbor_device": neigh,
            "neighbor_interface": neigh_if
        })

    return data
