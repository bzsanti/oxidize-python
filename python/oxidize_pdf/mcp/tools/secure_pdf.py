"""MCP tool: secure_pdf — encrypt, check permissions, and verify signatures."""

import json

from oxidize_pdf.mcp.server import mcp

_VALID_OPERATIONS = frozenset({"encrypt", "permissions", "verify_signatures"})


@mcp.tool()
def secure_pdf(
    operation: str,
    input_path: str | None = None,
    output_path: str | None = None,
    user_password: str | None = None,
    owner_password: str | None = None,
    password: str | None = None,
) -> str:
    """Secure PDF operations: encrypt, check permissions, verify signatures.

    Operations:
    - encrypt: Encrypt a PDF with user/owner passwords (requires input_path, output_path, passwords).
    - permissions: Check if a PDF is encrypted and report encryption status (requires input_path).
    - verify_signatures: Verify digital signatures in a PDF (requires input_path).
    """
    if operation not in _VALID_OPERATIONS:
        return json.dumps({
            "error": f"Unknown operation: '{operation}'. "
            f"Valid operations: {', '.join(sorted(_VALID_OPERATIONS))}.",
            "code": "INVALID_OPERATION",
        })

    try:
        dispatcher = {
            "encrypt": _op_encrypt,
            "permissions": _op_permissions,
            "verify_signatures": _op_verify_signatures,
        }
        return dispatcher[operation](
            input_path=input_path,
            output_path=output_path,
            user_password=user_password,
            owner_password=owner_password,
            password=password,
        )
    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})


def _op_encrypt(**kwargs: object) -> str:
    input_path = kwargs["input_path"]
    output_path = kwargs["output_path"]
    user_password = kwargs["user_password"]
    owner_password = kwargs["owner_password"]

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

    for i in range(reader.page_count):
        parsed = reader.get_page(i)
        page = Page(parsed.width, parsed.height)
        page.set_font(Font.HELVETICA, 10.0)
        text = reader.extract_text_from_page(i)
        if text:
            page.text_at(50.0, 750.0, text[:500])
        doc.add_page(page)

    doc.encrypt(user_password, owner_password)
    doc.save(str(resolved_output))
    return json.dumps({"status": "ok", "operation": "encrypt"})


def _op_permissions(**kwargs: object) -> str:
    input_path = kwargs["input_path"]
    password = kwargs.get("password")

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
            "note": "Permission details require document-level access after unlock.",
            "encrypted": is_encrypted,
        },
    })


def _op_verify_signatures(**kwargs: object) -> str:
    input_path = kwargs["input_path"]

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
