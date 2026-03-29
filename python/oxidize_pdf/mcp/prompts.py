"""MCP prompts for oxidize-pdf — guided multi-step workflows."""

from oxidize_pdf.mcp.server import mcp


@mcp.prompt(name="create-invoice")
def create_invoice(company: str, items: str) -> str:
    """Guide the LLM through creating a PDF invoice."""
    return (
        f"Create a professional PDF invoice for **{company}** with the following items:\n"
        f"{items}\n\n"
        "Follow these steps using oxidize-pdf tools:\n"
        "1. Call `create_pdf` with a title like 'Invoice - {company}'.\n"
        "2. Use `add_pdf_content` to add header text (company name, date, invoice number).\n"
        "3. Use `add_pdf_content` to add each line item with quantity, description, and price.\n"
        "4. Use `add_pdf_content` to add a total at the bottom.\n"
        "5. Call `save_pdf` to write the final invoice PDF.\n"
    )


@mcp.prompt(name="extract-for-rag")
def extract_for_rag(path: str, chunk_size: str = "256") -> str:
    """Guide the LLM through extracting PDF content for RAG ingestion."""
    return (
        f"Extract content from `{path}` for RAG (Retrieval-Augmented Generation) ingestion.\n\n"
        "Follow these steps:\n"
        f"1. Call `convert_pdf` with `format='rag'` and `chunk_size={chunk_size}` on the file.\n"
        "2. The result will contain text chunks suitable for embedding.\n"
        "3. Each chunk should be stored in your vector database with metadata "
        "(page number, chunk index, source file).\n"
        "4. For large documents, process chunks in batches to avoid memory issues.\n"
    )


@mcp.prompt(name="review-pdf")
def review_pdf(path: str) -> str:
    """Guide the LLM through a comprehensive PDF review."""
    return (
        f"Perform a comprehensive review of the PDF at `{path}`.\n\n"
        "Follow these steps:\n"
        "1. Call `read_pdf` to get document metadata (page count, title, author).\n"
        "2. Call `extract_text` to read the full text content.\n"
        "3. Call `analyze_pdf` with `check='validate'` to verify structural integrity.\n"
        "4. Call `analyze_pdf` with `check='corruption'` to check for corruption.\n"
        "5. Call `analyze_pdf` with `check='compliance'` to check PDF/A compliance.\n"
        "6. Summarize your findings: document quality, issues found, and recommendations.\n"
    )


@mcp.prompt(name="compare-documents")
def compare_documents(path1: str, path2: str) -> str:
    """Guide the LLM through comparing two PDF documents."""
    return (
        f"Compare the PDF documents at `{path1}` and `{path2}`.\n\n"
        "Follow these steps:\n"
        f"1. Call `analyze_pdf` with `check='compare'`, `path='{path1}'`, "
        f"and `compare_path='{path2}'`.\n"
        "2. Review the similarity score and difference count.\n"
        "3. Call `read_pdf` on both files to compare metadata.\n"
        "4. Call `extract_text` on both files to compare content.\n"
        "5. Summarize: structural differences, content differences, and overall assessment.\n"
    )


@mcp.prompt(name="fill-form")
def fill_form(form_path: str, context: str) -> str:
    """Guide the LLM through filling a PDF form."""
    return (
        f"Fill the PDF form at `{form_path}` using the following context:\n"
        f"{context}\n\n"
        "Follow these steps:\n"
        f"1. Call `manage_forms` with `operation='read'` and `input_path='{form_path}'` "
        "to discover available form fields.\n"
        "2. Map the context values above to the discovered field names.\n"
        f"3. Call `manage_forms` with `operation='fill'`, `input_path='{form_path}'`, "
        "and the mapped `values` dict.\n"
        "4. Optionally call `manage_forms` with `operation='validate'` to verify the fill.\n"
    )
