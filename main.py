import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def read_file(path: str) -> str:
    """Read a text file and return its content."""
    with open(path, "r") as f:
        return f.read()


def build_prompt(config_text: str) -> str:
    """Build the prompt we send to the AI."""
    return f"""
You are a senior network engineer and documentation specialist.

You will be given raw CLI outputs from one or more Cisco switches/routers, including:
- show running-config
- show vlan brief
- show ip interface brief
- show cdp neighbors
- show lldp neighbors
- show version
- show ip route (if present)

From this, produce a STRICT JSON object with the following keys:

"device_summary": {{
  "hostname": string or null,
  "model": string or null,
  "serial": string or null,
  "os_version": string or null
}},

"vlans": [
  {{"vlan_id": "10", "name": "USERS", "ports": ["Gi1/0/1","Gi1/0/2"]}}
],

"interfaces": [
  {{
    "name": "GigabitEthernet1/0/1",
    "description": "Uplink to Core" or "",
    "ip_address": "10.0.1.1/24" or null,
    "vlan": "10" or null,
    "status": "up" or "down" or null,
    "protocol": "up" or "down" or null
  }}
],

"neighbors": [
  {{
    "local_interface": "GigabitEthernet1/0/1",
    "neighbor_device": "CORE1",
    "neighbor_interface": "GigabitEthernet0/1"
  }}
],

"routing_summary": {{
  "dynamic_protocols": ["OSPF","BGP"] or [],
  "default_route": "0.0.0.0/0 via 10.0.0.1" or null,
  "total_routes": integer or null
}},

"security_findings": [
  {{
    "issue": "Example: VTY lines use password-only authentication",
    "severity": "low/medium/high/critical",
    "recommendation": "Example: Use AAA with local or TACACS+ users"
  }}
],

"ascii_topology": "Simple ASCII art drawing of the topology using device names and interfaces."

Rules:
- Infer reasonable values when possible.
- If information is missing, use null or empty values.
- For security_findings, look for obvious things: weak or plain-text passwords, lack of AAA, no logging, no BPDU guard, default VLAN usage, unused open interfaces, etc.
- Return ONLY valid JSON text. No comments, no markdown, no extra text.

CONFIG_START
{config_text}
CONFIG_END
"""


def call_openai(prompt: str) -> str:
    """Call OpenAI using chat.completions and return the JSON text."""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    # The assistant's reply content (should be pure JSON text)
    return response.choices[0].message.content


def build_markdown_report(data: dict) -> str:
    """Turn the parsed JSON into a markdown documentation report."""
    device = data.get("device_summary", {}) or {}
    vlans = data.get("vlans", []) or []
    interfaces = data.get("interfaces", []) or []
    neighbors = data.get("neighbors", []) or []
    routing = data.get("routing_summary", {}) or {}
    security = data.get("security_findings", []) or []
    ascii_topology = data.get("ascii_topology", "") or ""

    md = []

    md.append("# Network Documentation Report\n")

    # Device summary
    md.append("## Device Summary")
    md.append(f"- **Hostname:** {device.get('hostname', '')}")
    md.append(f"- **Model:** {device.get('model', '')}")
    md.append(f"- **Serial:** {device.get('serial', '')}")
    md.append(f"- **OS Version:** {device.get('os_version', '')}\n")

    # VLANs
    md.append("## VLANs")
    if vlans:
        md.append("| VLAN ID | Name | Ports |")
        md.append("|--------|------|-------|")
        for v in vlans:
            ports = ", ".join(v.get("ports", []) or [])
            md.append(f"| {v.get('vlan_id','')} | {v.get('name','')} | {ports} |")
    else:
        md.append("_No VLAN information found._")

    # Interfaces
    md.append("\n## Interfaces")
    if interfaces:
        md.append("| Interface | Description | IP Address | VLAN | Status | Protocol |")
        md.append("|-----------|-------------|-----------|------|--------|----------|")
        for intf in interfaces:
            md.append(
                f"| {intf.get('name','')} "
                f"| {intf.get('description','')} "
                f"| {intf.get('ip_address','')} "
                f"| {intf.get('vlan','')} "
                f"| {intf.get('status','')} "
                f"| {intf.get('protocol','')} |"
            )
    else:
        md.append("_No interface information found._")

    # Neighbors
    md.append("\n## Neighbors (CDP/LLDP)")
    if neighbors:
        md.append("| Local Interface | Neighbor Device | Neighbor Interface |")
        md.append("|----------------|-----------------|--------------------|")
        for n in neighbors:
            md.append(
                f"| {n.get('local_interface','')} "
                f"| {n.get('neighbor_device','')} "
                f"| {n.get('neighbor_interface','')} |"
            )
    else:
        md.append("_No neighbor information found._")

    # Routing summary
    md.append("\n## Routing Summary")
    md.append(f"- Dynamic Protocols: {', '.join(routing.get('dynamic_protocols', []) or [])}")
    md.append(f"- Default Route: {routing.get('default_route','')}")
    md.append(f"- Total Routes: {routing.get('total_routes','')}")

    # Security findings
    md.append("\n## Security Findings")
    if security:
        for finding in security:
            md.append(f"- **Issue:** {finding.get('issue','')}")
            md.append(f"  - Severity: **{finding.get('severity','')}**")
            md.append(f"  - Recommendation: {finding.get('recommendation','')}\n")
    else:
        md.append("_No obvious security issues detected (based on config provided)._")

    # ASCII topology
    md.append("\n## Topology (ASCII View)")
    if ascii_topology:
        md.append("```")
        md.append(ascii_topology)
        md.append("```")
    else:
        md.append("_No topology information generated._")

    return "\n".join(md)


if __name__ == "__main__":
    # 1) Read your sample config
    config_text = read_file("sample_config.txt")

    # 2) Build prompt and call OpenAI
    prompt = build_prompt(config_text)
    json_text = call_openai(prompt)

    # 3) Parse JSON text to dict
    data = json.loads(json_text)

    # 4) Build markdown report
    md_report = build_markdown_report(data)

    # 5) Save to file
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(md_report)

    print("✅ Documentation generated: report.md")
