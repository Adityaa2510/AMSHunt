"""
Thin wrapper around asyncio subprocess execution for CLI security tools.
All tool wrappers (nmap, subfinder, httpx, nuclei, whatweb) go through this
for consistent timeout handling, logging, and error capture.
"""
import asyncio
import json
import logging
import shlex

logger = logging.getLogger("asm.tools")

DEFAULT_TIMEOUT = 300


class ToolExecutionError(Exception):
    def __init__(self, tool: str, returncode: int, stderr: str):
        self.tool = tool
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"{tool} exited with code {returncode}: {stderr[:500]}")


async def run_command(cmd: list[str], timeout: int = DEFAULT_TIMEOUT) -> str:
    logger.info("Running: %s", " ".join(shlex.quote(c) for c in cmd))
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise ToolExecutionError(cmd[0], -1, f"timed out after {timeout}s")

    if proc.returncode is not None and proc.returncode > 1:
        # Many recon tools (nuclei, subfinder) exit 1 on "no results found", not a real failure.
        raise ToolExecutionError(cmd[0], proc.returncode, stderr.decode(errors="ignore"))

    return stdout.decode(errors="ignore")


async def run_command_jsonlines(cmd: list[str], timeout: int = DEFAULT_TIMEOUT) -> list[dict]:
    raw = await run_command(cmd, timeout=timeout)
    results = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return results
