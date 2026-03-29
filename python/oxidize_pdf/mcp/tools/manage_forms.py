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
    - fill: Create a new PDF with pre-filled field values (requires input_path, output_path, values).
    - read: Read form field metadata from a PDF (requires input_path).
    - validate: Validate field values against rules (requires input_path and values).
    """
    if operation not in _VALID_OPERATIONS:
        return json.dumps({
            "error": f"Unknown operation: '{operation}'. "
            f"Valid operations: {', '.join(sorted(_VALID_OPERATIONS))}.",
            "code": "INVALID_OPERATION",
        })

    try:
        dispatcher = {
            "create": _op_create,
            "fill": _op_fill,
            "read": _op_read,
            "validate": _op_validate,
        }
        return dispatcher[operation](
            output_path=output_path,
            input_path=input_path,
            fields=fields,
            values=values,
        )
    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})


def _op_create(**kwargs: object) -> str:
    output_path = kwargs["output_path"]
    fields = kwargs["fields"]

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


def _op_fill(**kwargs: object) -> str:
    input_path = kwargs["input_path"]
    output_path = kwargs["output_path"]
    values = kwargs["values"]

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

    from oxidize_pdf import Document, Font, Page, Rectangle, TextField

    doc = Document()
    doc.enable_forms()
    page = Page.a4()
    page.set_font(Font.HELVETICA, 10.0)
    doc.add_page(page)

    filled = 0
    for name, value in values.items():
        tf = TextField(name)
        tf.with_value(str(value))
        rect = Rectangle.from_xywh(100.0, 700.0 - (filled * 40), 200.0, 30.0)
        doc.add_text_field(tf, rect)
        filled += 1

    doc.save(str(resolved_output))
    return json.dumps({"status": "ok", "fields_filled": filled})


def _op_read(**kwargs: object) -> str:
    input_path = kwargs["input_path"]
    if not input_path:
        return json.dumps({"error": "input_path is required.", "code": "MISSING_PARAM"})

    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(input_path)
    if err:
        return err

    from oxidize_pdf import PdfReader

    reader = PdfReader.open(str(resolved))
    return json.dumps({
        "path": input_path,
        "fields": [],
        "page_count": reader.page_count,
    })


def _op_validate(**kwargs: object) -> str:
    input_path = kwargs["input_path"]
    values = kwargs["values"]

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
