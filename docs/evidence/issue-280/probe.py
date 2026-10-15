"""Run with .venv/bin/python docs/evidence/issue-280/probe.py; requires qpdf."""
from pathlib import Path
import importlib.util
import json
import subprocess
import tempfile

root = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('tagged_fixture', root / 'tests/test_tagged_validation.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix='tagged-validation-') as tmp:
    path = Path(tmp) / 'source.pdf'
    path.write_bytes(module.tagged_pdf())
    subprocess.run(['qpdf', '--check', str(path)], check=True)
    graph = json.loads(subprocess.check_output(['qpdf', '--json', str(path)]))
    objects = graph['qpdf'][1]
    element = objects['obj:6 7 R']['value']
    assert element['/S'] == '/CustomP'
    assert element['/Vendor']['/Raw'] == 'b:00ff'
    assert objects['obj:7 0 R']['value']['/Nums'] == [0, ['6 7 R']]
    report = module.validate_tagged_pdf(path.read_bytes())
    assert report.elements[0].object.generation == 7
    assert report.elements[0].dictionary['Vendor'].value['Raw'].value == bytes.fromhex('00ff')
    print('qpdf independently confirms generation 7, parent ownership and opaque bytes; report agrees.')
