"""The distributed MCP extra must select the new SDK, not a legacy fallback."""

from importlib.metadata import version


def test_sdk_major_version():
    assert version("mcp").split(".")[0] == "2"


def test_fastmcp_major_version():
    assert version("fastmcp").split(".")[0] == "4"
