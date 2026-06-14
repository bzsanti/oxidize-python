# Dockerfile for the oxidize-pdf MCP server (`oxidize-mcp`).
#
# Purpose: provide a self-contained image that starts the MCP server over stdio
# and responds to introspection requests (initialize / tools/list), as required
# by Glama's automated listing checks (https://glama.ai/mcp/servers).
#
# The image installs the published `oxidize-pdf` wheel from PyPI, which bundles
# the compiled Rust extension — the same artifact end users run via
# `uvx oxidize-mcp`. The `[mcp]` extra pulls in fastmcp and pydantic.
#
# Build:  docker build -t oxidize-mcp .
# Run:    docker run --rm -i oxidize-mcp        # stdio transport; -i keeps stdin open

FROM python:3.12-slim

# Pinned to the current release so the image is reproducible. Bump on each
# release that changes the MCP surface.
ARG OXIDIZE_PDF_VERSION=0.10.0

# Non-root user: the server only reads/writes PDFs passed over stdio.
RUN useradd --create-home --uid 10001 oxidize

RUN pip install --no-cache-dir "oxidize-pdf[mcp]==${OXIDIZE_PDF_VERSION}"

USER oxidize
WORKDIR /home/oxidize

# FastMCP defaults to the stdio transport; an MCP client (or Glama's checker)
# speaks JSON-RPC over stdin/stdout.
ENTRYPOINT ["oxidize-mcp"]
