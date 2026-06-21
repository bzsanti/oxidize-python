"""MCP tool: secure_pdf — encrypt, check permissions, and verify signatures."""

import json
from typing import Annotated, Literal, Optional

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Encrypt / inspect PDF security",
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=False,
    )
)
def secure_pdf(
    operation: Annotated[
        Literal["encrypt", "permissions", "verify_signatures"],
        Field(
            description="'encrypt' writes a password-protected copy; "
            "'permissions' reports encryption status; 'verify_signatures' checks "
            "digital signatures. Only 'encrypt' writes a file."
        ),
    ],
    input_path: Optional[str] = Field(
        default=None,
        description="Source PDF. Required for all three operations.",
    ),
    output_path: Optional[str] = Field(
        default=None,
        description="Destination .pdf for the encrypted copy (overwritten if "
        "present). Required for 'encrypt'; unused otherwise.",
    ),
    user_password: Optional[str] = Field(
        default=None,
        description="Open password for the encrypted copy. Required for 'encrypt'.",
    ),
    owner_password: Optional[str] = Field(
        default=None,
        description="Owner/permissions password. Required for 'encrypt'.",
    ),
    password: Optional[str] = Field(
        default=None,
        description="Password used to unlock the file when checking "
        "'permissions' on an encrypted PDF. Unused by other operations.",
    ),
) -> str:
    """Encrypt a PDF, report its encryption status, or verify its signatures.

    Returns JSON per operation: encrypt→{status, operation, page_count, note};
    permissions→{path, is_encrypted, unlocked, permissions}; verify_signatures→
    {path, signatures, signature_count}. 'permissions' and 'verify_signatures'
    are read-only; 'encrypt' writes output_path (overwriting).

    Caveat: 'encrypt' rebuilds the document from its text, preserving content and
    layout but possibly dropping images, embedded fonts and vector graphics (the
    current API has no in-place encryption). To encrypt a PDF you are authoring,
    pass the passwords to save_pdf instead.
    """
    try:
        if operation == "encrypt":
            return _op_encrypt(
                input_path=input_path,
                output_path=output_path,
                user_password=user_password,
                owner_password=owner_password,
            )
        elif operation == "permissions":
            return _op_permissions(input_path=input_path, password=password)
        else:
            return _op_verify_signatures(input_path=input_path)
    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})


def _op_encrypt(
    *,
    input_path: str | None,
    output_path: str | None,
    user_password: str | None,
    owner_password: str | None,
) -> str:
    if not input_path:
        return json.dumps({"error": "input_path is required.", "code": "MISSING_PARAM"})
    if not output_path:
        return json.dumps({"error": "output_path is required.", "code": "MISSING_PARAM"})
    if not user_password or not owner_password:
        return json.dumps({
            "error": "user_password and owner_password are required.",
            "code": "MISSING_PARAM",
        })

    from oxidize_pdf.mcp.tools.base import setup_output_path, setup_pdf_path

    resolved_input, err = setup_pdf_path(input_path)
    if err:
        return err
    resolved_output, err = setup_output_path(output_path)
    if err:
        return err

    from oxidize_pdf import Document, Font, Page, PdfReader

    reader = PdfReader.open(str(resolved_input))
    doc = Document()

    meta = reader.metadata()
    if meta.title:
        doc.set_title(meta.title)
    if meta.author:
        doc.set_author(meta.author)

    for i in range(reader.page_count):
        parsed = reader.get_page(i)
        page = Page(parsed.width, parsed.height)

        chunks = reader.extract_text_chunks(i)
        for chunk in chunks:
            font = getattr(Font, chunk.font_name.upper().replace("-", "_"), Font.HELVETICA)
            page.set_font(font, chunk.font_size)
            page.text_at(chunk.x, chunk.y, chunk.text)

        if not chunks:
            page.set_font(Font.HELVETICA, 10.0)

        doc.add_page(page)

    doc.encrypt(user_password, owner_password)
    doc.save(str(resolved_output))
    return json.dumps({
        "status": "ok",
        "operation": "encrypt",
        "page_count": reader.page_count,
        "note": "Text content preserved; non-text elements (images, vector graphics) may be lost.",
    })


def _op_permissions(
    *,
    input_path: str | None,
    password: str | None,
) -> str:
    if not input_path:
        return json.dumps({"error": "input_path is required.", "code": "MISSING_PARAM"})

    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(input_path)
    if err:
        return err

    from oxidize_pdf import PdfReader

    reader = PdfReader.open(str(resolved))
    is_encrypted = reader.is_encrypted

    unlocked = False
    if is_encrypted and password:
        reader.unlock(password)
        unlocked = True

    return json.dumps({
        "path": input_path,
        "is_encrypted": is_encrypted,
        "unlocked": unlocked,
        "permissions": {
            "encrypted": is_encrypted,
        },
    })


def _op_verify_signatures(*, input_path: str | None) -> str:
    if not input_path:
        return json.dumps({"error": "input_path is required.", "code": "MISSING_PARAM"})

    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(input_path)
    if err:
        return err

    from oxidize_pdf import verify_pdf_signatures

    with open(str(resolved), "rb") as f:
        data = f.read()

    sigs = verify_pdf_signatures(data)
    sig_list = []
    for sig in sigs:
        sig_list.append({
            "valid": getattr(sig, "is_valid", None),
            "signer": getattr(sig, "signer", None),
        })

    return json.dumps({
        "path": input_path,
        "signatures": sig_list,
        "signature_count": len(sig_list),
    })
