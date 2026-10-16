"""Page-local marking, inspected independently in serialized PDF streams."""
import re
import shutil
import subprocess
import zlib

import pytest
import oxidize_pdf as p


def content(page):
    document = p.Document()
    document.add_page(page)
    pdf = bytes(document.save_to_bytes())
    streams = []
    for match in re.finditer(rb'\d+ 0 obj\s*(.*?)\s*endobj', pdf, re.S):
        if b'\nstream\n' not in match[1]:
            continue
        header, data = match[1].split(b'\nstream\n', 1)
        length = int(re.search(rb'/Length\s+(\d+)', header)[1])
        data = data[:length]
        streams.append(zlib.decompress(data) if b'/FlateDecode' in header else data)
    return pdf, b'\n'.join(streams)


def test_nested_marks_and_page_local_ids():
    page = p.Page.a4()
    assert (page.next_mcid(), page.marked_content_depth()) == (0, 0)
    assert page.begin_marked_content('P') == 0
    assert page.begin_marked_content('Span') == 1
    assert (page.next_mcid(), page.marked_content_depth()) == (2, 2)
    page.set_font(p.Font.HELVETICA, 12)
    page.text_at(20, 50, 'nested')
    page.end_marked_content()
    assert page.marked_content_depth() == 1
    page.end_marked_content()
    assert (page.next_mcid(), page.marked_content_depth()) == (2, 0)
    assert p.Page.a4().begin_marked_content('P') == 0
    _, stream = content(page)
    outer = stream.index(b'/P <</MCID 0>> BDC')
    inner = stream.index(b'/Span <</MCID 1>> BDC')
    text = stream.index(b'nested')
    end = stream.index(b'EMC')
    assert outer < inner < text < end
    assert stream.count(b'EMC') == 2


@pytest.mark.parametrize('tag,encoded', [
    ('P', b'P'), ('a b/#\x00\n', b'a#20b#2F#23#00#0A'),
    ('é', b'#C3#A9'), ('x> BDC EMC /Injected', b'x#3E#20BDC#20EMC#20#2FInjected'),
])
def test_tag_is_one_pdf_name(tag, encoded):
    page = p.Page.a4()
    page.begin_marked_content(tag)
    page.end_marked_content()
    _, stream = content(page)
    assert b'/' + encoded + b' <</MCID 0>> BDC\nEMC' in stream


def test_errors_leave_marking_state_unchanged():
    page = p.Page.a4()
    with pytest.raises(p.PdfError):
        page.end_marked_content()
    for begin in [lambda: page.begin_marked_content(''),
                  lambda: page.begin_marked_content_with_actual_text('', 'logical')]:
        with pytest.raises(ValueError, match='must not be empty'):
            begin()
        assert (page.next_mcid(), page.marked_content_depth()) == (0, 0)
    assert page.begin_marked_content('P') == 0
    page.end_marked_content()


@pytest.mark.parametrize('logical,hex_text', [
    ('', b'FEFF'), ('A(\\)\n', b'FEFF00410028005C0029000A'),
    ('café 😀', b'FEFF00630061006600E90020D83DDE00'),
])
def test_actual_text_utf16(logical, hex_text):
    page = p.Page.a4()
    assert page.begin_marked_content_with_actual_text('Span', logical) == 0
    page.set_font(p.Font.HELVETICA, 12)
    page.text_at(20, 50, 'painted')
    page.end_marked_content()
    _, stream = content(page)
    assert b'/ActualText <' + hex_text + b'>' in stream
    assert stream.index(b'BDC') < stream.index(b'painted') < stream.index(b'EMC')


def test_poppler_uses_logical_text(tmp_path):
    if not shutil.which('pdftotext') or not shutil.which('qpdf'):
        pytest.skip('Poppler and qpdf required (installed in Linux CI)')
    page = p.Page.a4()
    page.set_font(p.Font.HELVETICA, 12)
    page.begin_marked_content_with_actual_text('Span', 'café 😀')
    page.text_at(20, 50, 'painted')
    page.end_marked_content()
    pdf, _ = content(page)
    path = tmp_path / 'marked.pdf'
    path.write_bytes(pdf)
    subprocess.run(['qpdf', '--check', str(path)], check=True, capture_output=True)
    result = subprocess.run(['pdftotext', str(path), '-'], check=True, capture_output=True).stdout.decode()
    assert 'café 😀' in result
    assert 'painted' not in result


def test_mcid_connects_to_structure_tree():
    page = p.Page.a4()
    mcid = page.begin_marked_content('P')
    page.set_font(p.Font.HELVETICA, 12)
    page.text_at(20, 50, 'paragraph')
    page.end_marked_content()
    tree = p.StructTree()
    root = tree.set_root(p.StructureElement(p.StandardStructureType.DOCUMENT))
    paragraph = p.StructureElement(p.StandardStructureType.P)
    paragraph.add_mcid(0, mcid)
    tree.add_child(root, paragraph)
    doc = p.Document()
    doc.add_page(page)
    doc.set_struct_tree(tree)
    pdf = bytes(doc.save_to_bytes())
    assert re.search(rb'/StructParents\s+0\b', pdf)
    assert b'/ParentTree' in pdf
    report = p.validate_tagged_pdf(pdf)
    assert not any(f.code == p.TaggedPdfFindingCode.InvalidMarkedContentReference for f in report.findings)
    assert list(report.content_mcids.values()) == [[0]]
    assert any(element.marked_content_count == 1 for element in report.elements)
