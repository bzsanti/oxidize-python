"""Composed extraction policies tested on independently encoded PDF content."""
import zlib

import pytest
import oxidize_pdf as op
from test_upstream_4_3_0 import TWO_COLUMNS_RIGHT_FIRST


def pdf(content, damaged=False):
    def stream(data, extra=b''):
        return b'<< /Length %d %s >>\nstream\n' % (len(data), extra) + data + b'\nendstream'
    payload = zlib.compress(content)
    if damaged:
        payload = payload[:-4]
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /ToUnicode 6 0 R >>',
        stream(payload, b'/Filter /FlateDecode'),
        stream(b'begincmap\n1 begincodespacerange\n<00> <FF>\nendcodespacerange\n1 beginbfrange\n<00> <7F> <0000>\nendbfrange\nendcmap'),
    ]
    result = b'%PDF-1.4\n'
    offsets = []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result += b'%d 0 obj\n' % i + obj + b'\nendobj\n'
    start = len(result)
    result += b'xref\n0 7\n0000000000 65535 f \n'
    result += b''.join(b'%010d 00000 n \n' % off for off in offsets)
    return result + b'trailer\n<< /Size 7 /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % start


@pytest.mark.parametrize('policy,expected', [
    (op.CarriageReturnHandling.REMOVE, 'AB\nC'),
    (op.CarriageReturnHandling.REPLACE_WITH_SPACE, 'A B\nC'),
    (op.CarriageReturnHandling.NORMALIZE_LINE_ENDING, 'A\rB\nC'),
])
def test_carriage_return_policy_reaches_all_extraction_paths(policy, expected):
    content = b'BT /F1 12 Tf 40 700 Td (A\\015B\\012C) Tj ET'
    reader = op.PdfReader.from_bytes(pdf(content))
    opts = op.ExtractionOptions(carriage_return_handling=policy)
    assert opts.carriage_return_handling == policy
    assert reader.extract_text_with_options(opts) == [expected]
    assert reader.extract_page_text(0, opts).text == expected
    layout = op.ExtractionOptions(preserve_layout=True, carriage_return_handling=policy)
    assert ''.join(f.text for f in reader.extract_fragments_from_page(0, layout)) == expected
    assert ''.join(f.text for f in reader.extract_fragments_with_options(layout)[0]) == expected
    recovered = op.PdfReader.from_bytes(pdf(content, damaged=True))
    page = recovered.extract_page_text_with_recovery(0, max_stream_bytes=4096, options=opts)
    assert page.text.text == expected
    assert page.diagnostics
    assert recovered.extract_text_with_recovery(max_stream_bytes=4096, options=opts)[0].text.text == expected


@pytest.mark.parametrize('damaged', [False, True])
def test_reading_order_composes_with_recovery_and_text_budget(damaged):
    reader = op.PdfReader.from_bytes(pdf(TWO_COLUMNS_RIGHT_FIRST, damaged))
    opts = op.ExtractionOptions(reading_order=True, max_extracted_bytes=1000)
    assert opts.reading_order
    expected = 'Left top\nLeft bottom\nRight top\nRight bottom'
    if damaged:
        result = reader.extract_page_text_with_recovery(0, max_stream_bytes=4096, options=opts)
        assert result.text.text == expected
        assert result.diagnostics
    else:
        assert reader.extract_page_text(0, opts).text == expected
        assert reader.extract_text_with_options(opts) == [expected]
    zero = op.ExtractionOptions(reading_order=True, max_extracted_bytes=0)
    result = reader.extract_page_text_with_recovery(0, max_stream_bytes=4096, options=zero)
    assert result.text.text == ''
    assert result.text.truncated


def test_column_reordering_and_policy_defaults():
    default = op.ExtractionOptions()
    assert not default.reorder_columns
    assert not default.reading_order
    assert default.carriage_return_handling == op.CarriageReturnHandling.REMOVE
    content = b'BT /F1 10 Tf 1 0 0 1 50 700 Tm (Left top) Tj 1 0 0 1 350 700 Tm (Right top) Tj 1 0 0 1 50 680 Tm (Left bottom) Tj 1 0 0 1 350 680 Tm (Right bottom) Tj ET'
    reader = op.PdfReader.from_bytes(pdf(content))
    opts = op.ExtractionOptions(reorder_columns=True)
    assert opts.reorder_columns
    text = reader.extract_page_text(0, opts).text
    assert text.index('Left top') < text.index('Right top')
    assert text.index('Left bottom') < text.index('Right top')
    assert reader.extract_page_text(0, default).text.index('Right top') < reader.extract_page_text(0, default).text.index('Left bottom')
