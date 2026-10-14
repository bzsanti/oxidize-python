"""Read existing outline trees from independently assembled PDF objects."""
import pytest
import oxidize_pdf as pdf


def outlined_pdf(*, catalog=None, root=None, item=None, names=None, extra=None):
    objects = {
        1: catalog or b'<< /Type /Catalog /Pages 2 0 R /Outlines 5 0 R /Names << /Dests 8 0 R >> >>',
        2: b'<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>',
        3: b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 400] /Resources << >> >>',
        4: b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 500 600] /Resources << >> >>',
        5: root or b'<< /Type /Outlines /First 6 0 R /Last 6 0 R /Count 1 >>',
        6: item or b'<< /Title <FEFF0043006800610070007400650072002000C1> /Parent 5 0 R /First 7 0 R /Last 7 0 R /Count -1 /F 3 /C [0.1 0.2 0.3] /Dest [4 0 R /XYZ null 42 1.25] >>',
        7: b'<< /Title (Child) /Parent 6 0 R /Dest (chapter) >>',
        8: names or b'<< /Names [(chapter) [3 0 R /FitH null]] >>',
    }
    objects.update(extra or {})
    data = bytearray(b'%PDF-1.7\n')
    offsets = [0]
    for number in range(1, max(objects) + 1):
        offsets.append(len(data))
        data.extend(f'{number} 0 obj\n'.encode() + objects[number] + b'\nendobj\n')
    xref = len(data)
    data.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:
        data.extend(f'{offset:010} 00000 n \n'.encode())
    data.extend(f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    return bytes(data)


def test_outline_options_defaults_and_validation():
    options = pdf.OutlineReadOptions()
    assert (options.max_items, options.max_depth, options.max_named_destinations,
            options.max_name_tree_nodes) == (100000, 256, 100000, 100000)
    with pytest.raises(AttributeError):
        options.max_items = 1
    for field in ('max_items', 'max_depth', 'max_named_destinations', 'max_name_tree_nodes'):
        for invalid in (-1, 2**100):
            with pytest.raises(OverflowError):
                pdf.OutlineReadOptions(**{field: invalid})
        assert getattr(pdf.OutlineReadOptions(**{field: 0}), field) == 0


def test_absent_and_empty_outlines_are_distinct():
    absent = pdf.PdfReader.from_bytes(outlined_pdf(catalog=b'<< /Type /Catalog /Pages 2 0 R >>'))
    assert absent.outline() is None
    assert absent.outline_with_options(pdf.OutlineReadOptions(max_items=0, max_depth=0,
        max_named_destinations=0, max_name_tree_nodes=0)) is None
    empty = pdf.PdfReader.from_bytes(outlined_pdf(root=b'<< /Type /Outlines >>')).outline()
    assert isinstance(empty, pdf.ReadOutline)
    assert empty.items == []


def test_hierarchy_styles_resolved_destinations_and_owned_results(tmp_path):
    data = outlined_pdf()
    path = tmp_path / 'outline.pdf'
    path.write_bytes(data)
    for reader in (pdf.PdfReader.from_bytes(data), pdf.PdfReader.open(str(path))):
        outline = reader.outline()
        assert isinstance(outline, pdf.ReadOutline)
        item = outline.items[0]
        assert item.title == 'Chapter Á'
        assert item.is_bold and item.is_italic and not item.is_open
        assert item.color == pytest.approx((0.1, 0.2, 0.3))
        assert item.destination.page_index == 1
        assert item.destination.kind == 'XYZ'
        assert item.destination.parameters == [None, 42.0, 1.25]
        child = item.children[0]
        assert child.title == 'Child' and child.children == []
        assert not child.is_bold and not child.is_italic and child.is_open
        assert child.color is None
        assert child.destination.page_index == 0
        assert child.destination.kind == 'FitH'
        assert child.destination.parameters == [None]
        outline.items.clear()
        item.children.clear()
        assert len(outline.items) == 1 and len(item.children) == 1
        assert reader.page_count == 2
        with pytest.raises(AttributeError):
            item.title = 'changed'
    del reader, outline
    assert child.destination.page_index == 0 and item.title == 'Chapter Á'


@pytest.mark.parametrize('view,kind,parameters', [
    (b'/XYZ 12 null 0', 'XYZ', [12.0, None, 0.0]),
    (b'/Fit', 'Fit', []), (b'/FitH 8', 'FitH', [8.0]),
    (b'/FitV null', 'FitV', [None]), (b'/FitR 1 2 30 40', 'FitR', [1., 2., 30., 40.]),
    (b'/FitB', 'FitB', []), (b'/FitBH null', 'FitBH', [None]),
    (b'/FitBV 9', 'FitBV', [9.0]),
])
def test_all_destination_views(view, kind, parameters):
    item = b'<< /Title (View) /Parent 5 0 R /A << /S /GoTo /D [3 0 R ' + view + b'] >> >>'
    result = pdf.PdfReader.from_bytes(outlined_pdf(item=item)).outline().items[0].destination
    assert result.page_index == 0
    assert result.kind == kind
    assert result.parameters == parameters


@pytest.mark.parametrize('field,limit', [('max_items', 1), ('max_depth', 0),
    ('max_named_destinations', 0), ('max_name_tree_nodes', 0)])
def test_each_budget_is_enforced_and_reader_can_retry(field, limit):
    reader = pdf.PdfReader.from_bytes(outlined_pdf())
    with pytest.raises(pdf.PdfParseError, match='limit'):
        reader.outline_with_options(pdf.OutlineReadOptions(**{field: limit}))
    result = reader.outline_with_options(pdf.OutlineReadOptions(max_items=2, max_depth=1,
        max_named_destinations=1, max_name_tree_nodes=1))
    assert result.items[0].children[0].title == 'Child'


def test_empty_name_tree_nodes_consume_budget():
    data = outlined_pdf(names=b'<< /Kids [9 0 R] >>', extra={9: b'<< /Names [(chapter) [3 0 R /Fit]] >>'})
    reader = pdf.PdfReader.from_bytes(data)
    with pytest.raises(pdf.PdfParseError, match='limit'):
        reader.outline_with_options(pdf.OutlineReadOptions(max_name_tree_nodes=1))
    assert reader.outline_with_options(pdf.OutlineReadOptions(max_name_tree_nodes=2)).items[0].children[0].destination.kind == 'Fit'


@pytest.mark.parametrize('item', [
    b'<< /Title (Cycle) /Parent 5 0 R /Next 6 0 R >>',
    b'<< /Title (Bad parent) /Parent 4 0 R >>',
    b'<< /Title (Missing name) /Parent 5 0 R /Dest (unknown) >>',
    b'<< /Title (Invalid page) /Parent 5 0 R /Dest [9 /Fit] >>',
    b'<< /Title (Invalid flags) /Parent 5 0 R /F 8 >>',
    b'<< /Title (Incomplete child) /Parent 5 0 R /First 7 0 R >>',
])
def test_malformed_outline_is_an_error_not_partial_success(item):
    with pytest.raises(pdf.PdfParseError):
        pdf.PdfReader.from_bytes(outlined_pdf(item=item)).outline()


def test_non_goto_action_has_no_page_destination():
    item = b'<< /Title (Link) /Parent 5 0 R /A << /S /URI /URI (https://example.invalid) >> >>'
    result = pdf.PdfReader.from_bytes(outlined_pdf(item=item)).outline().items[0]
    assert result.title == 'Link' and result.destination is None


def test_legacy_named_destination_and_indirect_dictionary():
    catalog = b'<< /Type /Catalog /Pages 2 0 R /Outlines 5 0 R /Dests << /chapter 9 0 R >> >>'
    item = b'<< /Title (Legacy) /Parent 5 0 R /Dest /chapter >>'
    data = outlined_pdf(catalog=catalog, item=item, extra={9: b'<< /D [4 0 R /FitBV 8] >>'})
    destination = pdf.PdfReader.from_bytes(data).outline().items[0].destination
    assert (destination.page_index, destination.kind, destination.parameters) == (1, 'FitBV', [8.0])


@pytest.mark.parametrize('names,extra', [
    (b'<< /Names [(chapter) (chapter)] >>', {}),
    (b'<< /Kids [8 0 R] >>', {}),
])
def test_named_destination_and_name_tree_cycles_are_rejected(names, extra):
    with pytest.raises(pdf.PdfParseError):
        pdf.PdfReader.from_bytes(outlined_pdf(names=names, extra=extra)).outline()
