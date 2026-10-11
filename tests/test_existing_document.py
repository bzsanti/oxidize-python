"""Preservation is checked against hand-authored PDFs, including catalog data."""
import pytest
import oxidize_pdf as pdf


def fixture_pdf(path, labels=False):
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R /Lang (es-ES)' +
        (b' /PageLabels << /Nums [0 << /S /D >>] >>' if labels else b'') + b' >>',
        b'<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 300] /Resources << >> >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 400 500] /Resources << >> >>',
        b'<< /Title (Preservation contract) >>',
    ]
    data = bytearray(b'%PDF-1.7\n'); offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(data)); data += f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n'
    start = len(data)
    data += b'xref\n0 6\n0000000000 65535 f \n'
    for offset in offsets[1:]:
        data += f'{offset:010} 00000 n \n'.encode()
    data += f'trailer\n<< /Size 6 /Root 1 0 R /Info 5 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode()
    path.write_bytes(data)
    return str(path), bytes(data)


def test_extract_preserves_prefix_and_full_plan(tmp_path):
    source, original = fixture_pdf(tmp_path / 'input.pdf')
    output = tmp_path / 'output.pdf'
    policy = pdf.ExistingDocumentPolicy.preserve_base()
    plan = pdf.plan_extract_existing_pdf_pages(source, [1], policy)
    assert not output.exists()
    assert plan.engine == pdf.ExistingDocumentEngine.PreserveBase
    assert plan.inputs[0].role == pdf.InputSemanticRole.PreservedBase
    assert plan.inputs[0].path == source
    assert plan.inputs[0].selected_pages == [1]
    report = pdf.extract_existing_pdf_pages(source, [1], str(output), policy)
    assert output.read_bytes().startswith(original)
    assert report.plan.page_count == 1
    assert report.plan.incremental.replaced_objects == plan.plan.incremental.replaced_objects
    assert report.plan.incremental.added_objects == plan.plan.incremental.added_objects
    assert report.plan.incremental.unreachable_objects == plan.plan.incremental.unreachable_objects
    assert pdf.PdfReader.open(str(output)).page_count == 1


def test_merge_selection_and_secondary_labels_policy(tmp_path):
    base, original = fixture_pdf(tmp_path / 'base.pdf')
    secondary, _ = fixture_pdf(tmp_path / 'secondary.pdf', True)
    inputs = [pdf.ExistingDocumentMergeInput(base),
              pdf.ExistingDocumentMergeInput(secondary, pdf.PageRange.single(1))]
    output = tmp_path / 'merged.pdf'
    with pytest.raises(pdf.PdfError):
        pdf.merge_existing_pdfs(inputs, str(output), pdf.ExistingDocumentPolicy.preserve_base())
    assert not output.exists()
    policy = pdf.ExistingDocumentPolicy.preserve_base(page_labels_first_input_wins=True)
    plan = pdf.plan_merge_existing_pdfs(inputs, policy)
    report = pdf.merge_existing_pdfs(inputs, str(output), policy)
    assert output.read_bytes().startswith(original)
    assert report.plan.page_count == plan.plan.page_count == 3
    assert report.inputs[1].selected_pages == [1]
    assert report.inputs[1].role == pdf.InputSemanticRole.ImportedPages
    labels = [s for s in report.inputs[1].structures if s.structure == pdf.DocumentStructure.PageLabels]
    assert len(labels) == 1
    assert labels[0].disposition == pdf.StructureDisposition.FirstInputWins


@pytest.mark.parametrize('metadata', [False, True])
def test_reconstruct_policy_is_explicit_and_reported(tmp_path, metadata):
    source, original = fixture_pdf(tmp_path / 'input.pdf')
    output = tmp_path / 'output.pdf'
    policy = pdf.ExistingDocumentPolicy.reconstruct(metadata_from_first=metadata)
    report = pdf.extract_existing_pdf_pages(source, [0], str(output), policy)
    assert not output.read_bytes().startswith(original)
    assert report.engine == pdf.ExistingDocumentEngine.Reconstruct
    assert report.plan.incremental is None
    assert report.plan.page_count == 1
    info = [s for s in report.inputs[0].structures if s.structure == pdf.DocumentStructure.DocumentInfo]
    assert len(info) == 1
    assert info[0].disposition == (pdf.StructureDisposition.FirstInputWins if metadata else pdf.StructureDisposition.Discarded)


def test_split_reports_and_outputs(tmp_path):
    source, original = fixture_pdf(tmp_path / 'input.pdf')
    outputs = [str(tmp_path / f'part{i}.pdf') for i in range(2)]
    ranges = [pdf.PageRange.single(1), pdf.PageRange.single(0)]
    policy = pdf.ExistingDocumentPolicy.preserve_base()
    plans = pdf.plan_split_existing_pdf(source, ranges, policy)
    reports = pdf.split_existing_pdf(source, ranges, outputs, policy)
    for i, report in enumerate(reports):
        assert report.inputs[0].selected_pages == plans[i].inputs[0].selected_pages == [1-i]
        assert report.plan.page_count == 1
        assert (tmp_path / f'part{i}.pdf').read_bytes().startswith(original)


def test_failure_does_not_publish_or_replace_input(tmp_path):
    source, original = fixture_pdf(tmp_path / 'input.pdf')
    output = tmp_path / 'output.pdf'
    policy = pdf.ExistingDocumentPolicy.preserve_base()
    with pytest.raises(pdf.PdfError):
        pdf.extract_existing_pdf_pages(source, [2], str(output), policy)
    assert not output.exists()
    with pytest.raises(pdf.PdfError):
        pdf.extract_existing_pdf_pages(source, [0], source, policy)
    assert (tmp_path / 'input.pdf').read_bytes() == original
    with pytest.raises(TypeError):
        pdf.extract_existing_pdf_pages(source, [0], str(output))


def test_mutation_batch_preserves_source_and_executes_all_operations(tmp_path):
    source, original = fixture_pdf(tmp_path / 'input.pdf')
    imported, _ = fixture_pdf(tmp_path / 'import.pdf')
    output = tmp_path / 'output.pdf'
    operations = [
        pdf.PageMutation.move_page(1, 0),
        pdf.PageMutation.rotate(0, 90),
        pdf.PageMutation.duplicate(0, 2),
        pdf.PageMutation.delete(1),
        pdf.PageMutation.insert(imported, 0, 1),
    ]
    plan = pdf.plan_pdf_page_mutations(source, operations)
    report = pdf.mutate_pdf_pages_lossless(source, str(output), operations)
    assert output.read_bytes().startswith(original)
    assert report.page_count == plan.page_count == 3
    assert report.replaced_objects == plan.replaced_objects
    assert report.added_objects == plan.added_objects
    assert report.unreachable_objects == plan.unreachable_objects
    reader = pdf.PdfReader.open(str(output))
    assert reader.page_count == 3
    # Order reflects sequential indexes: rotated second, imported first, clone.
    assert [reader.get_page(i).width for i in range(3)] == [500, 200, 500]


def test_invalid_mutation_preserves_existing_destination(tmp_path):
    source, _ = fixture_pdf(tmp_path / 'input.pdf')
    output = tmp_path / 'output.pdf'
    output.write_bytes(b'keep existing destination')
    with pytest.raises(pdf.PdfError):
        pdf.mutate_pdf_pages_lossless(source, str(output), [pdf.PageMutation.rotate(0, 45)])
    assert output.read_bytes() == b'keep existing destination'


def test_base_page_labels_remapping_is_rejected_like_core(tmp_path):
    source, original = fixture_pdf(tmp_path / 'input.pdf', True)
    output = tmp_path / 'output.pdf'
    with pytest.raises(pdf.PdfError, match="PageLabels"):
        pdf.extract_existing_pdf_pages(source, [1], str(output), pdf.ExistingDocumentPolicy.preserve_base(page_labels_first_input_wins=True))
    assert not output.exists()
    assert (tmp_path / 'input.pdf').read_bytes() == original
