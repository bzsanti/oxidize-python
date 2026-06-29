"""Real-content image-extraction tests (issue #119).

`oxidize-pdf` is built with ``default-features = false``, which excludes the
upstream ``external-images`` feature. Issue #119 raised the concern that this
silently degrades image extraction to empty/stub results. These tests pin the
*actual* behaviour by extracting a real embedded JPEG and asserting real pixel
content — not merely "no error" or "non-empty list".

The embedding round-trip uses JPEG on purpose: a JPEG embedded via
``Image.from_jpeg_data`` is stored in the PDF as a ``DCTDecode`` XObject whose
stream is the JPEG bytes verbatim, so extraction must return a byte-faithful,
decodable JPEG when extraction works correctly.
"""

import io

import pytest

from oxidize_pdf import (
    Document,
    ExtractImagesOptions,
    Image,
    Page,
    extract_images_from_pdf,
)

PIL = pytest.importorskip("PIL")
from PIL import Image as PILImage  # noqa: E402


def _make_jpeg(width: int, height: int, color: tuple[int, int, int]) -> bytes:
    """Return real baseline-JPEG bytes of the given size filled with ``color``."""
    buf = io.BytesIO()
    PILImage.new("RGB", (width, height), color).save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def _pdf_with_embedded_jpeg(jpeg_bytes: bytes, w: float, h: float) -> bytes:
    """Build a one-page PDF embedding ``jpeg_bytes`` as an image XObject."""
    img = Image.from_jpeg_data(jpeg_bytes)
    # Dimensions must be parsed from the JPEG header by the core, not external-images.
    assert (img.width, img.height) == (int(w), int(h))

    page = Page.a4()
    page.add_image("Im0", img)
    page.draw_image("Im0", 100.0, 100.0, w, h)

    doc = Document()
    doc.add_page(page)
    return doc.save_to_bytes()


def test_extract_real_embedded_jpeg_returns_faithful_content(tmp_path):
    """A real embedded JPEG is extracted with correct dimensions and pixels.

    Fails (exposing silent degradation) if extraction returns an empty list,
    wrong dimensions, a non-JPEG/undecodable file, or blank pixel content.
    """
    jpeg_bytes = _make_jpeg(48, 32, (220, 30, 30))
    pdf_bytes = _pdf_with_embedded_jpeg(jpeg_bytes, 48.0, 32.0)

    pdf_path = tmp_path / "with_image.pdf"
    pdf_path.write_bytes(pdf_bytes)

    out_dir = tmp_path / "extracted"
    out_dir.mkdir()

    results = extract_images_from_pdf(str(pdf_path), ExtractImagesOptions(str(out_dir)))

    assert len(results) == 1, f"expected exactly 1 extracted image, got {results}"
    record = results[0]
    assert record["width"] == 48
    assert record["height"] == 32

    data = (tmp_path / record["file_path"]).read_bytes() if not record["file_path"].startswith("/") \
        else open(record["file_path"], "rb").read()

    # DCTDecode stores the JPEG stream verbatim: magic bytes must be present.
    assert data[:3] == b"\xff\xd8\xff", "extracted file is not a JPEG"

    decoded = PILImage.open(io.BytesIO(data))
    assert decoded.size == (48, 32), f"decoded size {decoded.size} != (48, 32)"

    # Real pixel content (solid red), not a blank/stub image.
    r, g, b = decoded.convert("RGB").getpixel((24, 16))
    assert r > 150 and g < 100 and b < 100, f"unexpected pixel colour {(r, g, b)}"


def test_extracted_jpeg_is_byte_identical_to_embedded_stream(tmp_path):
    """DCTDecode round-trip is byte-exact when external-images is disabled.

    With the feature off there is no re-encoding/preprocessing, so the extracted
    bytes must equal the embedded JPEG stream exactly. This is the precise
    guarantee documented for #119.
    """
    jpeg_bytes = _make_jpeg(64, 40, (20, 180, 60))
    pdf_bytes = _pdf_with_embedded_jpeg(jpeg_bytes, 64.0, 40.0)

    pdf_path = tmp_path / "with_image.pdf"
    pdf_path.write_bytes(pdf_bytes)
    out_dir = tmp_path / "extracted"
    out_dir.mkdir()

    results = extract_images_from_pdf(str(pdf_path), ExtractImagesOptions(str(out_dir)))
    assert len(results) == 1, f"expected exactly 1 extracted image, got {results}"

    extracted = open(results[0]["file_path"], "rb").read()
    assert extracted == jpeg_bytes, "extracted JPEG differs from the embedded stream"
