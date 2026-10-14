"""Options audited against published core 5.4.2, including its limitations."""
import pytest
import oxidize_pdf as pdf


PARSE_DEFAULTS = dict(strict_mode=True, recover_from_stream_errors=False,
    ignore_corrupt_streams=False, partial_content_allowed=False,
    lenient_streams=False, lenient_encoding=True, lenient_syntax=False,
    max_recovery_attempts=3, max_recovery_bytes=1000, collect_warnings=False,
    preferred_encoding=None, log_recovery_details=False)
RECOVERY_DEFAULTS = dict(aggressive_recovery=False, partial_content=True,
    max_errors=100, rebuild_xref=True, recover_embedded=False,
    skip_validation=False, memory_limit=524288000)


def test_parse_defaults_and_presets():
    assert {k: getattr(pdf.ParseOptions(), k) for k in PARSE_DEFAULTS} == PARSE_DEFAULTS
    strict = dict(PARSE_DEFAULTS, max_recovery_attempts=0, max_recovery_bytes=0,
                  lenient_encoding=False)
    tolerant = dict(PARSE_DEFAULTS, strict_mode=False, recover_from_stream_errors=True,
        partial_content_allowed=True, lenient_streams=True, lenient_syntax=True,
        max_recovery_attempts=5, max_recovery_bytes=5000, collect_warnings=True,
        log_recovery_details=True)
    skip = dict(tolerant, max_recovery_attempts=1, ignore_corrupt_streams=True,
                collect_warnings=False, log_recovery_details=False)
    for factory, expected in ((pdf.ParseOptions.strict, strict),
            (pdf.ParseOptions.tolerant, tolerant), (pdf.ParseOptions.lenient, tolerant),
            (pdf.ParseOptions.skip_errors, skip)):
        assert {k: getattr(factory(), k) for k in PARSE_DEFAULTS} == expected


@pytest.mark.parametrize('encoding', [None, 'utf-8', 'latin-1', 'windows-1252',
                                     'mac-roman', 'pdf-doc', 'mixed'])
def test_encoding_configuration_is_round_tripped(encoding):
    options = pdf.ParseOptions(preferred_encoding=encoding, log_recovery_details=True)
    assert options.preferred_encoding == encoding
    assert options.log_recovery_details is True
    with pytest.raises(AttributeError):
        options.preferred_encoding = None


def test_option_errors_and_unsigned_boundaries():
    with pytest.raises(ValueError, match='preferred_encoding'):
        pdf.ParseOptions(preferred_encoding='guess')
    with pytest.raises(TypeError):
        pdf.ParseOptions(preferred_encoding=12)
    for cls, fields in ((pdf.ParseOptions, ('max_recovery_attempts', 'max_recovery_bytes')),
                        (pdf.RecoveryOptions, ('max_errors', 'memory_limit'))):
        for field in fields:
            for value in (-1, 2**100):
                with pytest.raises(OverflowError):
                    cls(**{field: value})
            assert getattr(cls(**{field: 0}), field) == 0


def test_recovery_options_defaults_and_readonly_fields():
    options = pdf.RecoveryOptions()
    assert {k: getattr(options, k) for k in RECOVERY_DEFAULTS} == RECOVERY_DEFAULTS
    custom = dict(aggressive_recovery=True, partial_content=False, max_errors=7,
                  rebuild_xref=False, recover_embedded=True, skip_validation=True,
                  memory_limit=1)
    changed = pdf.RecoveryOptions(**custom)
    assert {k: getattr(changed, k) for k in custom} == custom
    for field in custom:
        with pytest.raises(AttributeError):
            setattr(changed, field, custom[field])


def test_partial_content_reaches_repair_and_results_are_owned(tmp_path):
    path = tmp_path / 'fragments.pdf'
    path.write_bytes(b'BT (Recovered text) Tj ET\n' * 15)
    full = pdf.repair_pdf(str(path), pdf.RepairStrategy.EXTRACT_CONTENT)
    limited = pdf.repair_pdf(str(path), pdf.RepairStrategy.EXTRACT_CONTENT,
                            options=pdf.RecoveryOptions(partial_content=False))
    assert full.pages_recovered == 15
    assert limited.pages_recovered == 10  # Published core's counterintuitive limit.
    for result, count in ((full, 15), (limited, 10)):
        assert result.success and result.is_partial
        assert result.objects_recovered == 0
        assert result.warnings == [f'Extracted {count} pages with content']
        result.warnings.clear()
        assert len(result.warnings) == 1
        assert isinstance(result.repaired_bytes, bytes)
        reader = pdf.PdfReader.from_bytes(result.repaired_bytes)
        assert reader.page_count == count
        # Core reconstructs blank pages: success does not prove content fidelity.
        assert reader.extract_text() == [''] * count
    path.unlink()
    assert pdf.PdfReader.from_bytes(full.repaired_bytes).page_count == 15


def test_inert_recovery_fields_do_not_enforce_limits(tmp_path):
    path = tmp_path / 'fragments.pdf'
    path.write_bytes(b'BT (Text) Tj ET\n' * 15)
    result = pdf.repair_pdf(str(path), pdf.RepairStrategy.EXTRACT_CONTENT,
        options=pdf.RecoveryOptions(memory_limit=0, max_errors=0,
            aggressive_recovery=True, rebuild_xref=False, recover_embedded=True,
            skip_validation=True))
    assert result.pages_recovered == 15  # Neither a memory cap nor validation policy.


def test_unsuccessful_repair_and_io_errors(tmp_path):
    path = tmp_path / 'fragments.pdf'
    path.write_bytes(b'No text blocks')
    result = pdf.repair_pdf(str(path), pdf.RepairStrategy.EXTRACT_CONTENT, options=None)
    assert not result.success
    assert result.repaired_bytes is None
    assert result.pages_recovered == result.objects_recovered == 0
    assert result.warnings == [] and result.is_partial
    with pytest.raises(pdf.PdfIoError):
        pdf.repair_pdf(str(tmp_path / 'missing.pdf'), pdf.RepairStrategy.EXTRACT_CONTENT)
    with pytest.raises(TypeError):
        pdf.repair_pdf(str(path), pdf.RepairStrategy.EXTRACT_CONTENT, options=object())


@pytest.mark.parametrize('source', ['bytes', 'file', 'stream'])
def test_parser_options_reach_each_reader_entrypoint(tmp_path, source):
    import io
    from test_outline_read import outlined_pdf
    # Xref requests object 3 but its header identifies 9. Strict core skips that
    # page; lenient syntax accepts it. Offsets remain unchanged.
    data = outlined_pdf().replace(b'3 0 obj', b'9 0 obj')
    path = tmp_path / 'mismatched-object.pdf'
    path.write_bytes(data)

    def open_reader(options):
        if source == 'bytes':
            return pdf.PdfReader.from_bytes(data, options)
        if source == 'file':
            return pdf.PdfReader.open(str(path), options)
        return pdf.PdfReader.from_stream(io.BytesIO(data), options)

    strict = open_reader(pdf.ParseOptions.strict())
    lenient = open_reader(pdf.ParseOptions(lenient_syntax=True))
    assert strict.get_page(0).width == 500
    assert lenient.get_page(0).width == 300


def test_preferred_encoding_does_not_override_core_decoding():
    from test_outline_read import outlined_pdf
    for encoding in ('utf-8', 'latin-1', 'windows-1252', 'mac-roman', 'pdf-doc', 'mixed'):
        reader = pdf.PdfReader.from_bytes(outlined_pdf(),
            pdf.ParseOptions(preferred_encoding=encoding, log_recovery_details=True))
        assert reader.outline().items[0].title == 'Chapter Á'
