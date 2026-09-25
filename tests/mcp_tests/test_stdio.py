"""Exercise installed entry points with real, isolated SDK clients."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

PROBE = Path(__file__).parent / "clients" / "stdio_probe.py"


@pytest.mark.parametrize("launch", ["module", "entrypoint"])
def test_sdk_v2_stdio(launch, tmp_path):
    result = subprocess.run(
        [sys.executable, str(PROBE), sys.executable, launch, str(tmp_path)],
        capture_output=True, text=True, timeout=55,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["protocol"] == "2026-07-28"


def test_legacy_sdk_stdio(tmp_path):
    legacy_python = os.environ.get("OXIDIZE_LEGACY_PYTHON")
    if not legacy_python:
        pytest.skip("CI interoperability job supplies an isolated MCP 1.26.0 client")
    result = subprocess.run(
        [legacy_python, str(PROBE), sys.executable, "entrypoint", str(tmp_path)],
        capture_output=True, text=True, timeout=55,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["sdk"] == "1.26.0"
    assert report["protocol"] == "2025-11-25"


@pytest.mark.asyncio
async def test_stdout_is_jsonrpc_and_server_version_is_explicit(tmp_path):
    """Inspect actual lines so permissive SDK logging cannot hide stdout noise."""
    import asyncio

    async def exchange():
        with (tmp_path / "stderr.log").open("wb") as stderr:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "oxidize_pdf.mcp.server",
                stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
                stderr=stderr, cwd=tmp_path,
                env={**os.environ, "OXIDIZE_WORKSPACE": str(tmp_path)},
            )
            try:
                process.stdin.write(json.dumps({
                    "jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2025-11-25", "capabilities": {},
                               "clientInfo": {"name": "wire-test", "version": "1"}},
                }).encode() + b"\n")
                await process.stdin.drain()
                while True:
                    line = await process.stdout.readline()
                    assert line, (tmp_path / "stderr.log").read_text()
                    message = json.loads(line)
                    assert message["jsonrpc"] == "2.0"
                    if message.get("id") == 1:
                        assert message["result"]["protocolVersion"] == "2025-11-25"
                        assert message["result"]["serverInfo"]["name"] == "oxidize-pdf"
                        assert message["result"]["serverInfo"]["version"] == "1.0.0"
                        break
            finally:
                process.stdin.close()
                try:
                    await asyncio.wait_for(process.wait(), 5)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()

    await asyncio.wait_for(exchange(), 20)
