# ============================================================
#  NETWORK TOPOLOGY GENERATOR (Mermaid.js)
# ============================================================

def generate_topology_mermaid(parsed):
    """
    parsed["cdp_neighbors"] expected:
    {
        "Gig1/0/1": {"device": "CORE1", "port": "Gig0/1"},
        "Gig1/0/2": {"device": "Access1", "port": "Eth1"},
        ...
    }
    """

    neighbors = parsed.get("cdp_neighbors", {})
    hostname = parsed.get("hostname", "Device")

    mermaid = ["graph TD"]

    # Add main device node
    mermaid.append(f'    {hostname}["{hostname}"]')

    # Build links
    for local_intf, info in neighbors.items():
        remote_dev = info.get("device", "Unknown")
        remote_intf = info.get("port", "")

        # Add remote node
        mermaid.append(f'    {remote_dev}["{remote_dev}"]')

        # Create a labeled connection
        mermaid.append(
            f'    {hostname} -- "{local_intf} ↔ {remote_intf}" --> {remote_dev}'
        )

    # If no neighbors, show placeholder
    if not neighbors:
        mermaid.append('    Empty["No CDP/LLDP neighbors detected"]')
        mermaid.append(f"    {hostname} --> Empty")

    return "\n".join(mermaid)
