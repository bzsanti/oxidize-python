"""MCP tool implementations for oxidize-pdf.

All tool modules are imported here to register their @mcp.tool() decorators.
Import errors are NOT silenced — a broken tool module must fail loudly at startup.
"""

import oxidize_pdf.mcp.tools.read_pdf as read_pdf  # noqa: F401
import oxidize_pdf.mcp.tools.extract_text as extract_text  # noqa: F401
import oxidize_pdf.mcp.tools.convert_pdf as convert_pdf  # noqa: F401
import oxidize_pdf.mcp.tools.analyze_pdf as analyze_pdf  # noqa: F401
import oxidize_pdf.mcp.tools.extract_entities as extract_entities  # noqa: F401
import oxidize_pdf.mcp.tools.manipulate_pdf as manipulate_pdf  # noqa: F401
import oxidize_pdf.mcp.tools.annotate_pdf as annotate_pdf  # noqa: F401
import oxidize_pdf.mcp.tools.manage_forms as manage_forms  # noqa: F401
import oxidize_pdf.mcp.tools.secure_pdf as secure_pdf  # noqa: F401
import oxidize_pdf.mcp.tools.create_pdf as create_pdf  # noqa: F401
import oxidize_pdf.mcp.tools.add_pdf_content as add_pdf_content  # noqa: F401
import oxidize_pdf.mcp.tools.save_pdf as save_pdf  # noqa: F401
