"""
Vulnerability scanning via Nuclei against its community template repo.
Templates are refreshed at worker image build time (see worker/Dockerfile)
so scans stay current against newly published CVEs.
"""
from app.services.tool_runner import run_command_jsonlines

SEVERITY_MAP = {"info": "info", "low": "low", "medium": "medium", "high": "high", "critical": "critical"}


async def run_vuln_scan(url: str, severity_filter: str = "medium,high,critical") -> list[dict]:
    cmd = ["nuclei", "-u", url, "-severity", severity_filter, "-jsonl", "-silent", "-rate-limit", "50"]
    results = await run_command_jsonlines(cmd, timeout=600)

    findings = []
    for r in results:
        info = r.get("info", {})
        findings.append({
            "title": info.get("name", "Unknown finding"),
            "severity": SEVERITY_MAP.get(info.get("severity", "info"), "info"),
            "description": info.get("description"),
            "cve_id": ",".join(info.get("classification", {}).get("cve-id", []) or []) or None,
            "template_id": r.get("template-id"),
            "matched_at": r.get("matched-at"),
            "raw": r,
        })
    return findings
