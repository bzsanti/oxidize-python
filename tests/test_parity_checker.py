"""Negative controls: removing an option/result/test must fail the parity gate."""
import importlib.util
from pathlib import Path
import shutil
import pytest

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('kind', ['option', 'result', 'test', 'export', 'core', 'event-field', 'error-code', 'error-field'])
def test_parity_checker_rejects_contract_regressions(tmp_path, kind):
    spec = importlib.util.spec_from_file_location('parity_checker', ROOT / 'scripts/check_parity.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    for relative in ['Cargo.toml', 'docs/parity-contract.json', 'python/oxidize_pdf/_oxidize_pdf.pyi', 'tests/test_existing_document.py', 'tests/test_incremental_signing.py', 'tests/test_extraction_options_parity.py', 'tests/test_incremental_annotations.py', 'tests/test_incremental_ink.py', 'tests/test_incremental_geometric.py', 'tests/test_rag_reader_parity.py', 'tests/test_page_streamer.py', 'tests/test_incremental_parser_payloads.py', 'tests/test_batch_options.py', 'tests/test_signature_errors.py', 'tests/test_outline_read.py', 'tests/test_parser_recovery_options.py', 'tests/test_parser_recovery_options.py', 'python/oxidize_pdf/signature_errors.py', 'python/oxidize_pdf/parse_events.py']:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    checker.REPO_ROOT = tmp_path
    exports = checker.parse_init_exports((ROOT / 'python/oxidize_pdf/__init__.py').read_text(encoding="utf-8"))
    assert checker.check_contract(exports) == []
    if kind == 'export':
        exports.remove('plan_merge_existing_pdfs')
    else:
        path = tmp_path / ('python/oxidize_pdf/signature_errors.py' if kind in ('error-code', 'error-field') else 'python/oxidize_pdf/parse_events.py' if kind == 'event-field' else 'Cargo.toml' if kind == 'core' else 'tests/test_existing_document.py' if kind == 'test' else 'python/oxidize_pdf/_oxidize_pdf.pyi')
        source = path.read_text(encoding="utf-8")
        before, after = {
            'core': ('=5.4.2', '=5.4.3'),
            'error-code': ("'unsupported_algorithm'", "'removed_algorithm'"),
            'error-field': ('offset: int', 'offset: str'),
            'event-field': ('    data: bytes', '    lost_data: bytes'),
            'option': ('page_labels_first_input_wins: bool = False', 'removed_option: bool = False'),
            'result': ('def unreachable_objects(self)', 'def missing_objects(self)'),
            'test': ('def test_extract_preserves_prefix_and_full_plan(', 'def removed_behavior('),
        }[kind]
        assert before in source
        path.write_text(source.replace(before, after, 1), encoding="utf-8")
    assert checker.check_contract(exports), kind
