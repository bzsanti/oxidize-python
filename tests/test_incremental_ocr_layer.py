"""#278: caller-supplied text, real incremental bytes, permissions and atomicity."""
from pathlib import Path
import pytest
import oxidize_pdf as p

F = p.OcrLayerFragment
P = p.OcrLayerPage
E = p.IncrementalOcrLayerEditor


def make_pdf(*, font_entry=b'/F1 5 0 R', contents=b'8 0 R'):
    """Independent two-page PDF with inherited fonts, an image, annotation and info."""
    content = b'q 10 0 0 10 10 10 cm /Im1 Do Q\nBT /F1 12 Tf 30 180 Td (ORIGINAL) Tj ET'
    objects = [b'<< /Type /Catalog /Pages 2 0 R /Lang (es-ES) >>',
               b'<< /Type /Pages /Count 2 /Kids [3 0 R 4 0 R] /MediaBox [0 0 200 300] /Resources << /Font << ' + font_entry + b' >> /XObject << /Im1 6 0 R >> >> >>',
               b'<< /Type /Page /Parent 2 0 R /Rotate 90 /Annots [7 0 R] /Contents ' + contents + b' >>',
               b'<< /Type /Page /Parent 2 0 R >>',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
               b'<< /Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Length 3 >>\nstream\n\xff\x00\x00\nendstream',
               b'<< /Type /Annot /Subtype /Text /Rect [10 10 20 20] /Contents (KEEP-NOTE) >>',
               b'<< /Length %d >>\nstream\n' % len(content) + content + b'\nendstream',
               b'<< /Title (Preserved title) >>']
    data = b'%PDF-1.7\n'
    offsets = []
    for number, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += f'{number} 0 obj\n'.encode() + obj + b'\nendobj\n'
    xref = len(data)
    data += b'xref\n0 10\n0000000000 65535 f \n'
    data += b''.join(f'{offset:010d} 00000 n \n'.encode() for offset in offsets)
    return data + f'trailer\n<< /Size 10 /Root 1 0 R /Info 9 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()


def layer(page=0, text='café 世界 😀'):
    return P(page, 'es-ES', [F(text, [30., 80., 100., 12.], 0.95, 7)])


def plan_values(plan):
    return plan.pages, plan.streams_added, plan.resources_added, plan.pages_skipped_existing_ocr


def test_ocr_layer_plan_apply_unicode_and_preservation():
    base = make_pdf()
    editor = E(base)
    request = layer()
    planned = editor.plan([request])
    assert plan_values(planned) == ([0], 1, 1, [])
    result = editor.apply([request])
    assert plan_values(result.plan) == plan_values(planned)
    assert result.pdf_bytes.startswith(base)
    assert result.pdf_bytes.count(b'%%EOF') == base.count(b'%%EOF') + 1
    reader = p.PdfReader.from_bytes(result.pdf_bytes)
    assert reader.page_count == 2 and reader.metadata().title == 'Preserved title'
    assert reader.get_page(0).rotation == 90
    text = reader.extract_text_from_page(0)
    assert 'ORIGINAL' in text and 'café 世界 😀' in text
    streams = reader.get_page_content_streams(0)
    assert streams[0] == p.PdfReader.from_bytes(base).get_page_content_streams(0)[0]
    assert len(streams) == 2 and b'3 Tr' in streams[1]
    assert b'/OxidizeRegion [30.000000 80.000000 100.000000 12.000000]' in streams[1]
    assert b'/OxidizeConfidence 0.950000' in streams[1] and b'/OxidizeReadingOrder 7' in streams[1]
    assert b'/ActualText <FEFF00630061006600E900204E16754C0020D83DDE00>' in streams[1]
    assert plan_values(editor.plan([request])) == ([0], 1, 1, [])


def test_ocr_layer_owned_inputs_and_results():
    region = [30., 80., 90., 12.]
    fragment = F('owned', region, 0.8, 2)
    fragments = [fragment]
    page = P(1, 'en', fragments)
    region[0] = -999.
    fragments.clear()
    assert fragment.text == page.fragments[0].text == 'owned'
    assert fragment.region == [30., 80., 90., 12.]
    assert (fragment.confidence, fragment.reading_order, page.page_index, page.language) == (0.8, 2, 1, 'en')
    page.fragments.clear()
    page.fragments[0].region.clear()
    assert len(page.fragments) == 1 and len(page.fragments[0].region) == 4
    result = E(make_pdf()).apply([page])
    result.plan.pages.clear()
    assert result.plan.pages == [1]
    with pytest.raises(AttributeError):
        page.language = 'changed'
    with pytest.raises(AttributeError):
        fragment.text = 'changed'


def test_ocr_layer_sorted_plan_determinism_and_logical_order():
    base = make_pdf()
    pages = [P(0, 'en', [F('First', [20., 80., 30., 12.], 1., 2),
                         F('Second', [60., 80., 50., 12.], 0., 9)]), layer(1, 'Other')]
    editor = E(base)
    forward = editor.apply(pages)
    reverse = editor.apply(list(reversed(pages)))
    assert forward.pdf_bytes == reverse.pdf_bytes
    assert plan_values(reverse.plan) == ([0, 1], 2, 2, [])
    text = p.PdfReader.from_bytes(forward.pdf_bytes).extract_text_from_page(0)
    assert text.index('First') < text.index('Second')


def test_ocr_layer_noop_skip_and_mixed_existing_pages():
    base = make_pdf()
    editor = E(base)
    for pages in ([], [P(0, 'en', [])]):
        assert plan_values(editor.plan(pages)) == ([], 0, 0, [])
        assert editor.apply(pages).pdf_bytes == base
    first = editor.apply([layer()])
    existing = E(first.pdf_bytes)
    skipped = existing.apply([layer(0, 'replacement is not applied')])
    assert skipped.pdf_bytes == first.pdf_bytes
    assert plan_values(skipped.plan) == ([], 0, 0, [0])
    mixed = existing.apply([layer(1, 'new page'), layer()])
    assert plan_values(mixed.plan) == ([1], 1, 1, [0])
    assert mixed.pdf_bytes.startswith(first.pdf_bytes)
    assert 'new page' in p.PdfReader.from_bytes(mixed.pdf_bytes).extract_text_from_page(1)


@pytest.mark.parametrize('bad', [
    P(2, 'en', []), P(0, '', []), P(0, '   ', []), P(0, '日本語', []),
    P(0, 'en', [F('', [0., 0., 1., 1.], 1., 0)]),
    P(0, 'en', [F('x', [0., 0., 0., 1.], 1., 0)]),
    P(0, 'en', [F('x', [0., 0., 1., -1.], 1., 0)]),
    P(0, 'en', [F('x', [float('nan'), 0., 1., 1.], 1., 0)]),
    P(0, 'en', [F('x', [0., float('inf'), 1., 1.], 1., 0)]),
    P(0, 'en', [F('x', [0., 0., 1., 1.], -0.1, 0)]),
    P(0, 'en', [F('x', [0., 0., 1., 1.], 1.1, 0)]),
    P(0, 'en', [F('x', [0., 0., 1., 1.], float('nan'), 0)]),
    P(0, 'en', [F('x', [0., 0., 1., 1.], 1., 1), F('y', [1., 0., 1., 1.], 1., 1)]),
    P(0, 'en', [F('x', [0., 0., 1., 1.], 1., 2), F('y', [1., 0., 1., 1.], 1., 1)]),
])
def test_ocr_layer_invalid_batch_atomic_and_retry(bad):
    base = make_pdf()
    editor = E(base)
    good = layer(1)
    for method in (editor.plan, editor.apply):
        with pytest.raises(p.PdfParseError):
            method([good, bad])
    assert editor.apply([]).pdf_bytes == base
    assert editor.apply([good]).plan.pages == [1]


def test_ocr_layer_duplicate_pages_rejected():
    editor = E(make_pdf())
    for method in (editor.plan, editor.apply):
        with pytest.raises(p.PdfParseError, match='more than once'):
            method([layer(), layer()])


@pytest.mark.parametrize('permission', [1, 2, 3])
@pytest.mark.parametrize('empty', [False, True])
def test_ocr_layer_docmdp_denies_plan_and_apply(permission, empty):
    base = (Path(__file__).parent / 'fixtures/signatures/docmdp_p2_rsa.pdf').read_bytes()
    assert b'/P 2' in base
    base = base.replace(b'/P 2', f'/P {permission}'.encode(), 1)
    # Policy interpretation only: changing P invalidates cryptographic authenticity.
    editor = E(base)
    for method in (editor.plan, editor.apply):
        with pytest.raises(p.PdfPermissionError, match='DocMDP'):
            method([] if empty else [layer()])


def test_ocr_layer_encrypted_pdf_is_rejected(tmp_path):
    doc = p.Document(); doc.add_page(p.Page.a4()); doc.encrypt('user', 'owner')
    path = tmp_path / 'locked.pdf'; doc.save(str(path))
    editor = E(path.read_bytes())
    for method in (editor.plan, editor.apply):
        with pytest.raises(p.PdfPermissionError, match='encrypted'):
            method([layer()])


@pytest.mark.parametrize('base,match', [
    (make_pdf(font_entry=b'/OxidizeOCR 5 0 R'), 'font name'),
    (make_pdf(contents=b'[42]'), 'indirect'),
])
def test_ocr_layer_unsupported_resources_and_contents(base, match):
    for method in (E(base).plan, E(base).apply):
        with pytest.raises(p.PdfParseError, match=match):
            method([layer()])


@pytest.mark.parametrize('base', [b'', b'not a PDF', b'%PDF-1.7\n'])
def test_ocr_layer_invalid_pdf(base):
    for method in (E(base).plan, E(base).apply):
        with pytest.raises(p.PdfError):
            method([])


@pytest.mark.parametrize('make', [lambda: P(-1, 'en', []),
                                 lambda: F('x', [0., 0., 1., 1.], 1., -1),
                                 lambda: F('x', [0., 0., 1., 1.], 1., 2**32)])
def test_ocr_layer_unsigned_boundaries(make):
    with pytest.raises(OverflowError):
        make()
