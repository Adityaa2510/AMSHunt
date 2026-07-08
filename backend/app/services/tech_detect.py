"""
Technology fingerprinting. httpx's -tech-detect gives fast Wappalyzer-style
results; whatweb layers deeper plugin-based fingerprinting on top (catches
CMS/plugin versions httpx misses).
"""
import json
from app.services.tool_runner import run_command_jsonlines, run_command


async def detect_tech_httpx(url: str) -> dict:
    cmd = ["httpx", "-u", url, "-silent", "-json", "-tech-detect", "-status-code", "-title", "-server"]
    results = await run_command_jsonlines(cmd, timeout=60)
    return results[0] if results else {}


async def detect_tech_whatweb(url: str) -> list[dict]:
    cmd = ["whatweb", "--log-json=-", "--no-errors", url]
    raw = await run_command(cmd, timeout=60)
    parsed = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return parsed


async def detect_technologies(url: str) -> dict:
    httpx_result = await detect_tech_httpx(url)
    whatweb_result = await detect_tech_whatweb(url)

    techs = set(httpx_result.get("tech", []))
    for entry in whatweb_result:
        for plugin_name in entry.get("plugins", {}).keys():
            techs.add(plugin_name)

    return {
        "url": url,
        "status_code": httpx_result.get("status_code"),
        "title": httpx_result.get("title"),
        "server": httpx_result.get("webserver") or httpx_result.get("server"),
        "technologies": sorted(techs),
    }
