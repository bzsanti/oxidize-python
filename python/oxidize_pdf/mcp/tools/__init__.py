"""MCP tool implementations for oxidize-pdf.

All tool modules are imported here to register their @mcp.tool() decorators.
Import errors are NOT silenced — a broken tool module must fail loudly at startup.
"""

import oxidize_pdf.mcp.tools.read_pdf as read_pdf  # noqa: F401
import oxidize_pdf.mcp.tools.extract_text as extract_text  # noqa: F401
import oxidize_pdf.mcp.tools.convert_pdf as convert_pdf  # noqa: F401
