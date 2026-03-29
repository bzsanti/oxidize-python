"""MCP tool: manage_forms — create, fill, read, and validate PDF forms."""

import json

from oxidize_pdf.mcp.server import mcp

_VALID_OPERATIONS = frozenset({"create", "fill", "read", "validate"})


@mcp.tool()
def manage_forms(
    operation: str,
    output_path: str | None = None,
    input_path: str | None = None,
    fields: list[dict] | None = None,
    values: dict | None = None,
) -> str:
    """Manage PDF form fields.

    Operations:
    - create: Create a new PDF with form fields (requires output_path and fields).
    - fill: Create a new PDF with pre-filled form fields, preserving the original
      document as a visual base via overlay (requires input_path, output_path, values).
    - read: Read form structure from a PDF by extracting text entities (requires input_path).
    - validate: Validate field values against required rules (requires input_path and values).
    """
    if operation not in _VALID_OPERATIONS:
        return json.dumps({
            "error": f"Unknown operation: '{operation}'. "
            f"Valid operations: {', '.join(sorted(_VALID_OPERATIONS))}.",
            "code": "INVALID_OPERATION",
        })

    try:
        if operation == "create":
            return _op_create(output_path=output_path, fields=fields)
        elif operation == "fill":
            return _op_fill(
                input_path=input_path, output_path=output_path, values=values,
            )
        elif operation == "read":
            return _op_read(input_path=input_path)
        else:
            return _op_validate(input_path=input_path, values=values)
    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})


def _op_create(
    *,
    output_path: str | None,
    fields: list[dict] | None,
) -> str:
    if not output_path:
        return json.dumps({"error": "output_path is required.", "code": "MISSING_PARAM"})
    if not fields:
        return json.dumps({"error": "fields is required.", "code": "MISSING_PARAM"})

    from oxidize_pdf.mcp.tools.base import setup_output_path

    resolved, err = setup_output_path(output_path)
    if err:
        return err

    from oxidize_pdf import Document, Font, Page, Rectangle, TextField

    doc = Document()
    doc.enable_forms()
    page = Page.a4()
    page.set_font(Font.HELVETICA, 10.0)
    doc.add_page(page)

    created = 0
    for field_def in fields:
        field_type = field_def.get("type", "text")
        name = field_def.get("name", f"field_{created}")
        x = float(field_def.get("x", 0))
        y = float(field_def.get("y", 0))
        w = float(field_def.get("width", 150))
        h = float(field_def.get("height", 25))

        if field_type == "text":
            tf = TextField(name)
            default = field_def.get("default_value")
            if default:
                tf.with_default_value(default)
            rect = Rectangle.from_xywh(x, y, w, h)
            doc.add_text_field(tf, rect)
            created += 1

    doc.save(str(resolved))
    return json.dumps({"status": "ok", "fields_created": created})


def _op_fill(
    *,
    input_path: str | None,
    output_path: str | None,
    values: dict | None,
) -> str:
    if not input_path:
        return json.dumps({"error": "input_path is required.", "code": "MISSING_PARAM"})
    if not output_path:
        return json.dumps({"error": "output_path is required.", "code": "MISSING_PARAM"})
    if not values:
        return json.dumps({"error": "values is required.", "code": "MISSING_PARAM"})

    from oxidize_pdf.mcp.tools.base import setup_output_path, setup_pdf_path

    resolved_input, err = setup_pdf_path(input_path)
    if err:
        return err
    resolved_output, err = setup_output_path(output_path)
    if err:
        return err

    import tempfile
    from pathlib import Path

    from oxidize_pdf import (
        Document,
        Font,
        OverlayOptions,
        Page,
        PdfReader,
        Rectangle,
        TextField,
        overlay_pdf,
    )

    reader = PdfReader.open(str(resolved_input))
    parsed = reader.get_page(0)

    form_doc = Document()
    form_doc.enable_forms()
    page = Page(parsed.width, parsed.height)
    page.set_font(Font.HELVETICA, 10.0)
    form_doc.add_page(page)

    filled = 0
    for name, value in values.items():
        tf = TextField(name)
        tf.with_value(str(value))
        rect = Rectangle.from_xywh(100.0, 700.0 - (filled * 40), 200.0, 30.0)
        form_doc.add_text_field(tf, rect)
        filled += 1

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        form_doc.save(tmp.name)
        form_tmp = Path(tmp.name)

    try:
        overlay_pdf(
            str(resolved_input),
            str(form_tmp),
            str(resolved_output),
            OverlayOptions(),
        )
    finally:
        form_tmp.unlink(missing_ok=True)

    return json.dumps({"status": "ok", "fields_filled": filled})


def _op_read(*, input_path: str | None) -> str:
    if not input_path:
        return json.dumps({"error": "input_path is required.", "code": "MISSING_PARAM"})

    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(input_path)
    if err:
        return err

    from oxidize_pdf import PdfReader

    reader = PdfReader.open(str(resolved))
    page_count = reader.page_count

    fields: list[dict] = []
    for page_idx in range(page_count):
        chunks = reader.extract_text_chunks(page_idx)
        for chunk in chunks:
            fields.append({
                "text": chunk.text,
                "page": page_idx,
                "x": chunk.x,
                "y": chunk.y,
                "font_size": chunk.font_size,
            })

    return json.dumps({
        "path": input_path,
        "fields": fields,
        "page_count": page_count,
    })


def _op_validate(
    *,
    input_path: str | None,
    values: dict | None,
) -> str:
    if not input_path:
        return json.dumps({"error": "input_path is required.", "code": "MISSING_PARAM"})
    if not values:
        return json.dumps({"error": "values is required.", "code": "MISSING_PARAM"})

    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(input_path)
    if err:
        return err

    from oxidize_pdf import FieldValidator, FieldValue, FormValidationSystem, ValidationRule

    fvs = FormValidationSystem()
    results = {}
    all_valid = True

    for name, value in values.items():
        fv = FieldValidator(name)
        fv.add_rule(ValidationRule.required())
        fvs.add_validator(fv)

        fv_value = FieldValue.text(str(value)) if value else FieldValue.empty()
        result = fvs.validate_field(name, fv_value)
        results[name] = {
            "is_valid": result.is_valid,
            "errors": result.errors,
        }
        if not result.is_valid:
            all_valid = False

    return json.dumps({
        "valid": all_valid,
        "fields": results,
    })
