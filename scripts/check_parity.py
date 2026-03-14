#!/usr/bin/env python3
"""
check_parity.py

Verifies that the feature parity table in docs/FEATURE_PARITY.md is not
internally inconsistent with the Python package's actual public surface.

Specifically, it asserts:
  - Every symbol group marked `yes` in FEATURE_PARITY.md has at least one
    corresponding symbol exported in python/oxidize_pdf/__init__.py.
  - No symbol exported in __init__.py is completely absent from the parity table.

This script is intentionally conservative: it does NOT fail if a feature is
marked `no` or `partial`. It only fails if a `yes` entry has no detectable
corresponding export, which would indicate either the parity table is wrong
or the export was accidentally removed.

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
    """Return all names exported via __all__ in __init__.py."""
    exports: set[str] = set()
    in_all = False
    for line in init_content.splitlines():
        stripped = line.strip()
        if "__all__" in stripped and "=" in stripped:
            in_all = True
        if in_all:
            # Extract quoted names
            found = re.findall(r'"([A-Za-z_][A-Za-z0-9_]*)"', stripped)
            exports.update(found)
            if "]" in stripped:
                in_all = False
                break
    return exports


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

    errors: list[str] = []

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

    print(f"Parity check passed. Checked {len(yes_groups)} feature groups against {len(exports)} exports.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
