#!/usr/bin/env python3
"""
check_parity.py

Verifies that the feature parity table in docs/FEATURE_PARITY.md is not
internally inconsistent with the Python package's actual public surface.

Specifically, it asserts:
  - Every symbol group marked `yes` in FEATURE_PARITY.md has at least one
    corresponding symbol exported in python/oxidize_pdf/__init__.py.
  - Audited callables, options, result properties and behavior test entry points
    match docs/parity-contract.json. Runtime equivalence is tested by pytest.

This script is intentionally conservative: it does NOT fail if a feature is
marked `no` or `partial`. It fails for missing legacy exports or any broken
audited contract. It does not establish completeness outside the audited subset.

Symbol group mapping (feature_id_prefix -> expected __init__.py exports):
  DOC  -> Document
  PAGE -> Page
  TXT  -> Font, TextAlign
  GFX  -> Color
  PARSE -> PdfReader, ParsedPage
  OPS  -> split_pdf, merge_pdfs, rotate_pdf, extract_pages
  ERR  -> PdfError, PdfParseError, PdfIoError, PdfEncryptionError, PdfPermissionError

Exit codes:
  0 — all checks passed
  1 — inconsistency detected (details printed to stderr)
"""

import ast
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PARITY_FILE = REPO_ROOT / "docs" / "FEATURE_PARITY.md"
INIT_FILE = REPO_ROOT / "python" / "oxidize_pdf" / "__init__.py"

# Maps feature ID prefix -> minimum set of __init__.py symbols that must be present
# when ANY feature in that group is marked `yes`.
FEATURE_GROUP_SYMBOLS: dict[str, list[str]] = {
    "DOC": ["Document"],
    "PAGE": ["Page"],
    "TXT": ["Font", "TextAlign"],
    "GFX": ["Color"],
    "PARSE": ["PdfReader"],
    "OPS": ["split_pdf", "merge_pdfs", "rotate_pdf", "extract_pages"],
    "ERR": ["PdfError", "PdfParseError", "PdfIoError", "PdfEncryptionError", "PdfPermissionError"],
}


def parse_yes_groups(parity_content: str) -> set[str]:
    """Return the set of feature ID prefixes that have at least one `yes` entry."""
    yes_groups: set[str] = set()
    # Match table rows: | FEAT-NNN | ... | yes | or | yes (with notes) |
    row_pattern = re.compile(r"\|\s*(([A-Z]+)-\d+)\s*\|[^|]+\|\s*yes", re.IGNORECASE)
    for match in row_pattern.finditer(parity_content):
        prefix = match.group(2).upper()
        yes_groups.add(prefix)
    return yes_groups


def parse_init_exports(init_content: str) -> set[str]:
    """Collect literal __all__ definitions and additions without importing native code."""
    exports: set[str] = set()
    for node in ast.parse(init_content).body:
        value = None
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            value = node.value
        elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == "__all__":
            value = node.value
        if isinstance(value, (ast.List, ast.Tuple)):
            exports.update(n.value for n in value.elts if isinstance(n, ast.Constant) and isinstance(n.value, str))
    return exports


def check_contract(exports: set[str]) -> list[str]:
    """Check the explicitly audited subset; never interpret this as full Rust parity."""
    contract = json.loads((REPO_ROOT / "docs/parity-contract.json").read_text(encoding="utf-8"))
    tree = ast.parse((REPO_ROOT / "python/oxidize_pdf/_oxidize_pdf.pyi").read_text(encoding="utf-8"))
    declarations = {n.name: n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))}
    errors = []
    pin = re.search(r'^oxidize-pdf\s*=\s*\{\s*version\s*=\s*"=([^"]+)"', (REPO_ROOT / "Cargo.toml").read_text(encoding="utf-8"), re.MULTILINE)
    if pin is None or pin.group(1) != contract["core"]:
        errors.append("Core pin changed: reconcile the audited parity contract before upgrading")
    for path, expected in contract["callables"].items():
        parts = path.split(".")
        if parts[0] not in exports:
            errors.append(f"Missing audited export: {parts[0]}")
        member = declarations.get(parts[0])
        name = parts[1] if len(parts) > 1 else "__init__"
        if isinstance(member, ast.ClassDef):
            member = next((n for n in member.body if isinstance(n, ast.FunctionDef) and n.name == name), None)
        if not isinstance(member, ast.FunctionDef):
            errors.append(f"Missing callable declaration: {path}")
            continue
        args = [a.arg for a in member.args.posonlyargs + member.args.args + member.args.kwonlyargs if a.arg != "self" or (len(parts) > 1 and "self" in expected)]
        if args != expected:
            errors.append(f"Option mismatch for {path}: {args} != {expected}")
    for name, properties in contract["properties"].items():
        node = declarations.get(name)
        actual = {n.name for n in node.body if isinstance(n, ast.FunctionDef)} if isinstance(node, ast.ClassDef) else set()
        if name not in exports or not set(properties) <= actual:
            errors.append(f"Missing result contract: {name}")
    tests = ast.parse((REPO_ROOT / "tests/test_existing_document.py").read_text(encoding="utf-8"))
    names = {n.name for n in tests.body if isinstance(n, ast.FunctionDef)}
    if not set(contract["required_tests"]) <= names:
        errors.append("Missing audited behavioral tests")
    for relative, required in contract.get("additional_tests", {}).items():
        tree = ast.parse((REPO_ROOT / relative).read_text(encoding="utf-8"))
        names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        if not set(required) <= names:
            errors.append(f"Missing audited behavioral tests: {relative}")
    for relative, records in contract.get("typed_dicts", {}).items():
        records_tree = ast.parse((REPO_ROOT / relative).read_text(encoding="utf-8"))
        classes = {n.name: n for n in records_tree.body if isinstance(n, ast.ClassDef)}
        for name, required in records.items():
            record = classes.get(name)
            fields = {n.target.id for n in record.body
                      if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)} if record else set()
            if fields != set(required):
                errors.append(f"Typed event fields changed: {name}")
    signature = contract.get("signature_errors")
    if signature:
        tree = ast.parse((REPO_ROOT / signature["module"]).read_text(encoding="utf-8"))
        classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
        for name, bases in signature["classes"].items():
            node = classes.get(name)
            if name not in exports or node is None or [ast.unparse(b) for b in node.bases] != bases:
                errors.append(f"Signature error inheritance/export changed: {name}")
        definitions = {n.targets[0].id: n.value for n in tree.body
                       if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
        codes = definitions.get("SignatureErrorCode")
        actual_codes = set()
        if isinstance(codes, ast.Subscript) and ast.unparse(codes.value) == "Literal":
            values = codes.slice.elts if isinstance(codes.slice, ast.Tuple) else [codes.slice]
            actual_codes = {n.value for n in values if isinstance(n, ast.Constant)}
        if actual_codes != set(signature["codes"]):
            errors.append("Signature error codes changed")
        for name, expected in (("SignatureErrorDetails", signature["fields"]),
                               ("PdfSignatureError", {"code": "SignatureErrorCode", "details": "SignatureErrorDetails"})):
            node = classes.get(name)
            actual = {n.target.id: ast.unparse(n.annotation) for n in node.body
                      if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)} if node else {}
            if actual != expected:
                errors.append(f"Signature error fields/types changed: {name}")
    return errors


def main() -> int:
    if not PARITY_FILE.exists():
        print(f"ERROR: {PARITY_FILE} not found.", file=sys.stderr)
        return 1

    if not INIT_FILE.exists():
        print(f"ERROR: {INIT_FILE} not found.", file=sys.stderr)
        return 1

    parity_content = PARITY_FILE.read_text(encoding="utf-8")
    init_content = INIT_FILE.read_text(encoding="utf-8")

    yes_groups = parse_yes_groups(parity_content)
    exports = parse_init_exports(init_content)

    errors: list[str] = check_contract(exports)

    # Check: every `yes` group has its required symbols in __init__.py
    for prefix in sorted(yes_groups):
        required = FEATURE_GROUP_SYMBOLS.get(prefix)
        if required is None:
            # Unknown prefix — not an error, just a warning
            print(f"  WARNING: Feature prefix '{prefix}' has no symbol mapping in check_parity.py.")
            continue
        missing = [sym for sym in required if sym not in exports]
        if missing:
            errors.append(
                f"Feature group '{prefix}' is marked `yes` in FEATURE_PARITY.md "
                f"but these symbols are missing from __init__.py: {missing}"
            )

    if errors:
        print("PARITY CHECK FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        print(
            "\nEither update docs/FEATURE_PARITY.md to reflect the actual state, "
            "or restore the missing symbols.",
            file=sys.stderr,
        )
        return 1

    print(f"Partial parity contract passed: audited APIs plus {len(yes_groups)} legacy groups, {len(exports)} exports. Full Rust parity remains pending.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
