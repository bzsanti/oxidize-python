"""Optional independent validation; run with the project venv and qpdf installed."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tests'))
from test_incremental_geometric import fixture_pdf, E, M, shapes, style

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    _, base = fixture_pdf(root / 'base.pdf')
    added = E(base).apply([M.add(1, geometry, style()) for geometry in shapes()])
    identity = added.annotations[0].id
    updated = E(added.pdf_bytes).apply([M.update(identity, shapes()[0], style())])
    removed = E(updated.pdf_bytes).apply([M.remove(identity)])
    for name, result, count in [('added', added, 5), ('updated', updated, 5), ('removed', removed, 4)]:
        path = root / (name + '.pdf')
        path.write_bytes(result.pdf_bytes)
        subprocess.run(['qpdf', '--check', str(path)], check=True)
        data = json.loads(subprocess.check_output(['qpdf', '--json', str(path)]))
        objects = data['qpdf'][1]
        page = objects['obj:' + data['pages'][1]['object']]['value']
        refs = page['/Annots']
        assert len(refs) == count
        subtypes = [objects['obj:' + ref]['value']['/Subtype'] for ref in refs]
        expected = ['/Line', '/Square', '/Circle', '/Polygon', '/PolyLine']
        assert subtypes == (expected if count == 5 else expected[1:])
        for ref in refs:
            obj = objects['obj:' + ref]['value']
            assert obj['/C'] == [0.25, 0.5, 1] and obj['/IC'] == [0, 0.25, 0.5, 1]
            assert obj['/BS']['/W'] == 2 and obj['/CA'] == 0.5
            assert '/AP' in obj
        print(name, 'independent references, subtypes, color/style and appearance verified')
