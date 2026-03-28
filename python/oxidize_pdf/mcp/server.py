"""FastMCP server definition for oxidize-pdf."""

from fastmcp import FastMCP

mcp = FastMCP(name="oxidize-pdf")

import oxidize_pdf.mcp.tools  # noqa: E402, F401


def run() -> None:
    """Entry point for the oxidize-mcp command."""
    mcp.run()


if __name__ == "__main__":
    run()
