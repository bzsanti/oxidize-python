"""Negative controls: removing an option/result/test must fail the parity gate."""
import importlib.util
from pathlib import Path
import shutil
import pytest

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('kind', ['option', 'result', 'test', 'export'])
def test_parity_checker_rejects_contract_regressions(tmp_path, kind):
    spec = importlib.util.spec_from_file_location('parity_checker', ROOT / 'scripts/check_parity.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    for relative in ['docs/parity-contract.json', 'python/oxidize_pdf/_oxidize_pdf.pyi', 'tests/test_existing_document.py']:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    checker.REPO_ROOT = tmp_path
    exports = checker.parse_init_exports((ROOT / 'python/oxidize_pdf/__init__.py').read_text())
    assert checker.check_contract(exports) == []
    if kind == 'export':
        exports.remove('plan_merge_existing_pdfs')
    else:
        path = tmp_path / ('tests/test_existing_document.py' if kind == 'test' else 'python/oxidize_pdf/_oxidize_pdf.pyi')
        source = path.read_text()
        before, after = {
            'option': ('page_labels_first_input_wins: bool = False', 'removed_option: bool = False'),
            'result': ('def unreachable_objects(self)', 'def missing_objects(self)'),
            'test': ('def test_extract_preserves_prefix_and_full_plan(', 'def removed_behavior('),
        }[kind]
        assert before in source
        path.write_text(source.replace(before, after, 1))
    assert checker.check_contract(exports), kind
