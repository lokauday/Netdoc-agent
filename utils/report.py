def build_markdown_report(parsed: dict) -> str:
    md = f"# Network Device Report\n\n"

    md += f"## Hostname: {parsed.get('hostname')}\n\n"

    md += "## VLANs\n"
    for v in parsed.get("vlans", []):
        md += f"- VLAN {v}\n"

    md += "\n## Interfaces\n"
    for iface, info in parsed.get("interfaces", {}).items():
        md += f"### {iface}\n"
        md += f"- Status: {info['status']}\n"
        md += f"- IP: {info['ip']}\n"

    md += "\n## CDP Neighbors\n"
    for dev, info in parsed.get("cdp_neighbors", {}).items():
        md += f"- {dev}: {info}\n"

    return md
