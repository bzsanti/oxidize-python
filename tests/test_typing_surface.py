"""Runtime inventory and mutations of shipped declarations (issue #265)."""
import importlib.util
from pathlib import Path

import oxidize_pdf
import oxidize_pdf._oxidize_pdf as native
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("typing_surface", ROOT / "scripts/check_typing_surface.py")
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)
STUBS = ROOT / "python/oxidize_pdf"


def test_installed_typing_surface():
    report, errors = checker.inventory(oxidize_pdf, native, STUBS)
    assert not errors, "\n".join(errors)
    assert "partition" in report["PdfReader"]
    assert "next" in report["PageStreamer"]


@pytest.mark.parametrize("filename,old,new,expected", [
    ("__init__.pyi", "    Image as Image,", "", "Public export missing: Image"),
    ("__init__.pyi", "    Image as Image,", "    Color as Image,", "Public alias points to a different object: Image"),
    ("_oxidize_pdf.pyi", "def __init__(self, flag: int, x: float, y: float, color: Color)", "def missing_constructor(self, flag: int, x: float, y: float, color: Color)", "Member missing: GouraudVertex.__init__"),
    ("_oxidize_pdf.pyi", "def partition(self)", "def removed_partition(self)", "Member missing: PdfReader.partition"),
    ("_oxidize_pdf.pyi", "def next(self)", "def ghost(self) -> None: ...\n    def next(self)", "Declared member absent at runtime: PageStreamer.ghost"),
    ("_oxidize_pdf.pyi", "def next(self)", "def next(self, bogus: int)", "PageStreamer.next: runtime parameters"),
    ("_oxidize_pdf.pyi", "config: PlainTextConfig | None = ...", "config: PlainTextConfig | None", "PdfReader.extract_plain_text: runtime parameters"),
])
def test_inventory_rejects_stub_drift(tmp_path, filename, old, new, expected):
    for name in ("__init__.pyi", "_oxidize_pdf.pyi"):
        content = (STUBS / name).read_text(encoding="utf-8")
        if name == filename:
            assert old in content
            content = content.replace(old, new, 1)
        (tmp_path / name).write_text(content, encoding="utf-8")
    _, errors = checker.inventory(oxidize_pdf, native, tmp_path)
    assert any(expected in error for error in errors), errors


@pytest.mark.parametrize("operation", ["merge", "extract", "rotate", "split", "range"])
def test_binary_operation_result_types(tmp_path, operation):
    document = oxidize_pdf.Document()
    document.add_page(oxidize_pdf.Page.a4())
    path = str(tmp_path / "source.pdf")
    document.save(path)
    if operation == "merge":
        result = oxidize_pdf.merge_pdfs_to_bytes([path])
    elif operation == "extract":
        result = oxidize_pdf.extract_pages_to_bytes(path, [0])
    elif operation == "rotate":
        result = oxidize_pdf.rotate_pdf_to_bytes(path, 90)
    elif operation == "range":
        result = oxidize_pdf.extract_page_range_to_bytes(path, 0, 0)
    else:
        pages = oxidize_pdf.split_pdf_to_bytes(path)
        assert isinstance(pages, list) and len(pages) == 1
        result = pages[0]
    assert isinstance(result, bytes)
    assert result.startswith(b"%PDF-")
    assert oxidize_pdf.PdfReader.from_bytes(result).page_count == 1
