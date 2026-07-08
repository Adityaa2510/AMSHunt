"""
Asset discovery: enumerates subdomains for a root domain using subfinder,
optionally supplemented by amass if ASM_USE_AMASS is set.
"""
import os
import tempfile
from app.services.tool_runner import run_command_jsonlines, run_command

USE_AMASS = os.getenv("ASM_USE_AMASS", "false").lower() == "true"


async def discover_subdomains(root_domain: str) -> list[str]:
    subfinder_cmd = ["subfinder", "-d", root_domain, "-silent", "-json"]
    results = await run_command_jsonlines(subfinder_cmd, timeout=180)
    subdomains = {r["host"] for r in results if "host" in r}

    if USE_AMASS:
        amass_cmd = ["amass", "enum", "-passive", "-d", root_domain, "-silent"]
        raw = await run_command(amass_cmd, timeout=300)
        subdomains.update(line.strip() for line in raw.splitlines() if line.strip())

    return sorted(subdomains)


async def resolve_live_hosts(hosts: list[str]) -> list[dict]:
    """Filters hosts down to ones that respond over HTTP(S) via httpx, with metadata."""
    if not hosts:
        return []
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("\n".join(hosts))
        target_file = f.name

    cmd = [
        "httpx", "-l", target_file, "-silent", "-json",
        "-status-code", "-title", "-tech-detect", "-follow-redirects",
    ]
    return await run_command_jsonlines(cmd, timeout=180)
