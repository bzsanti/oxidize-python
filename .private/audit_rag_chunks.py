"""Empirical end-to-end audit of ``PdfReader.rag_chunks()`` on real PDFs.

Run with: ``.venv/bin/python .private/audit_rag_chunks.py``

Produces a report on stdout showing, for each fixture:

  * chunk count
  * pairwise substring containment violations (disjointness check)
  * duplicate-content ratio (size of chunk N+1 when it contains chunk N)
  * heading_context population rate
  * element_types distribution

This is the script that would have caught the v0.1.0 bug before publishing.
It intentionally lives under ``.private/`` because the fixtures referenced
may be private/confidential documents that cannot enter the test suite.
"""

from __future__ import annotations

import sys
from pathlib import Path

import oxidize_pdf as op


FIXTURES = [
    Path("/home/santi/repos/BelowZero/oxidizePdf/fixtures/Providers_vs_Repositories_Analysis.pdf"),
    Path("/home/santi/repos/BelowZero/oxidizePdf/fixtures/Recomendaciones_Codigo.pdf"),
    Path("/home/santi/repos/BelowZero/oxidizePdf/fixtures/Notas_MIPs_RADIO_Libera_Pulse_ES.pdf"),
]


def audit_one(pdf_path: Path) -> dict:
    reader = op.PdfReader.open(str(pdf_path))
    chunks = reader.rag_chunks()

    # Pairwise substring-containment violations — the bug signature.
    violations: list[tuple[int, int]] = []
    for i in range(len(chunks)):
        for j in range(i + 1, len(chunks)):
            ti, tj = chunks[i].text, chunks[j].text
            if ti and tj and (ti in tj or tj in ti):
                violations.append((i, j))

    # Distribution summary.
    element_types: dict[str, int] = {}
    for c in chunks:
        for t in c.element_types:
            element_types[t] = element_types.get(t, 0) + 1

    heading_populated = sum(1 for c in chunks if c.heading_context)

    token_estimates = [c.token_estimate for c in chunks]

    return {
        "file": pdf_path.name,
        "chunk_count": len(chunks),
        "violations": violations,
        "violation_count": len(violations),
        "element_types": element_types,
        "heading_context_populated": heading_populated,
        "heading_context_total": len(chunks),
        "token_estimate_sum": sum(token_estimates),
        "token_estimate_max": max(token_estimates) if token_estimates else 0,
        "token_estimate_min": min(token_estimates) if token_estimates else 0,
    }


def print_report(report: dict) -> None:
    print(f"\n── {report['file']} ──")
    print(f"  chunks: {report['chunk_count']}")
    print(
        f"  substring-containment violations: "
        f"{report['violation_count']} "
        f"({'DISJOINT ✓' if report['violation_count'] == 0 else 'BUG PRESENT ✗'})"
    )
    if report["violations"][:5]:
        print(f"    first violations (i,j): {report['violations'][:5]}")
    print(
        f"  heading_context populated: "
        f"{report['heading_context_populated']}/{report['heading_context_total']}"
    )
    print(f"  element_types distribution: {report['element_types']}")
    print(
        f"  token_estimate (min/max/sum): "
        f"{report['token_estimate_min']} / "
        f"{report['token_estimate_max']} / "
        f"{report['token_estimate_sum']}"
    )


def main() -> int:
    print(f"Bridge version: {op.__version__ if hasattr(op, '__version__') else 'n/a'}")
    print(f"Auditing {len(FIXTURES)} fixture(s)...")

    all_disjoint = True
    for path in FIXTURES:
        if not path.exists():
            print(f"  SKIP — not found: {path}")
            continue
        report = audit_one(path)
        print_report(report)
        if report["violation_count"] > 0:
            all_disjoint = False

    print()
    if all_disjoint:
        print("RESULT: ✅ all fixtures produced disjoint chunks — bug fixed.")
        return 0
    else:
        print("RESULT: ❌ substring containment violations detected — bug present.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
