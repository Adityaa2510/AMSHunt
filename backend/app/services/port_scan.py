"""
Port scanning via Nmap. Uses -oX (XML output) parsed into structured dicts,
since XML is nmap's most complete and stable output format.
"""
import os
import tempfile
import xml.etree.ElementTree as ET
from app.services.tool_runner import run_command

MAX_RATE = os.getenv("NMAP_MAX_RATE", "100")


async def scan_ports(target: str, ports: str = "1-1000") -> dict:
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        out_path = f.name

    cmd = ["nmap", "-sV", "-T4", "--max-rate", MAX_RATE, "-p", ports, "-oX", out_path, target]
    await run_command(cmd, timeout=600)

    tree = ET.parse(out_path)
    root = tree.getroot()

    host_el = root.find("host")
    if host_el is None:
        return {"host_up": False, "ports": []}

    status = host_el.find("status")
    host_up = status is not None and status.get("state") == "up"

    open_ports = []
    ports_el = host_el.find("ports")
    if ports_el is not None:
        for port_el in ports_el.findall("port"):
            state_el = port_el.find("state")
            if state_el is None or state_el.get("state") != "open":
                continue
            service_el = port_el.find("service")
            open_ports.append({
                "port": int(port_el.get("portid")),
                "protocol": port_el.get("protocol"),
                "service": service_el.get("name") if service_el is not None else None,
                "product": service_el.get("product") if service_el is not None else None,
                "version": service_el.get("version") if service_el is not None else None,
            })

    return {"host_up": host_up, "ports": open_ports}
