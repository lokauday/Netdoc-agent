# ===============================================================
#  NetDoc AI — CONFIG PARSER (Cisco / Juniper / Arista)
# ===============================================================

import re


# ---------------------------------------------------------------
# Clean config text
# ---------------------------------------------------------------
def clean_config(text: str) -> str:
    lines = text.splitlines()

    cleaned = []
    for line in lines:
        line = line.rstrip()

        # Skip empty & noisy lines
        if not line:
            continue
        if line.startswith("!"):
            continue
        if line.startswith("#"):
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


# ---------------------------------------------------------------
# Extract hostname
# ---------------------------------------------------------------
def extract_hostname(text: str) -> str:
    match = re.search(r"hostname (\S+)", text)
    return match.group(1) if match else "UnknownDevice"


# ---------------------------------------------------------------
# Extract VLANs
# ---------------------------------------------------------------
def extract_vlans(text: str) -> list:
    return re.findall(r"vlan (\d+)", text)


# ---------------------------------------------------------------
# Extract interfaces
# ---------------------------------------------------------------
def extract_interfaces(text: str) -> list:
    matches = re.findall(r"interface (\S+)", text)
    return matches


# ---------------------------------------------------------------
# Extract OSPF process IDs
# ---------------------------------------------------------------
def extract_ospf(text: str) -> list:
    return re.findall(r"router ospf (\d+)", text)


# ---------------------------------------------------------------
# Extract BGP AS numbers
# ---------------------------------------------------------------
def extract_bgp(text: str) -> list:
    return re.findall(r"router bgp (\d+)", text)


# ---------------------------------------------------------------
# Extract ACL names / numbers
# ---------------------------------------------------------------
def extract_acls(text: str) -> list:
    acl1 = re.findall(r"access-list (\S+)", text)
    acl2 = re.findall(r"ip access-list (\S+)", text)
    return list(set(acl1 + acl2))


# ---------------------------------------------------------------
# Extract CDP / LLDP neighbors
# ---------------------------------------------------------------
def extract_neighbors(text: str) -> list:
    cdp = re.findall(r"cdp neighbor (\S+)", text)
    lldp = re.findall(r"lldp neighbor (\S+)", text)
    generic = re.findall(r"neighbor (\S+)", text)

    return list(set(cdp + lldp + generic))


# ---------------------------------------------------------------
# FULL CONFIG PARSE ENTRYPOINT
# ---------------------------------------------------------------
def parse_config(text: str) -> dict:
    """
    Main parser used by ALL modules.
    Returns normalized structured config data.
    """

    cleaned = clean_config(text)

    parsed = {
        "hostname": extract_hostname(cleaned),
        "interfaces": extract_interfaces(cleaned),
        "vlans": extract_vlans(cleaned),
        "ospf": extract_ospf(cleaned),
        "bgp": extract_bgp(cleaned),
        "acls": extract_acls(cleaned),
        "neighbors": extract_neighbors(cleaned),
        "raw": cleaned
    }

    return parsed
