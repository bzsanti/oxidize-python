"""Run with project venv; requires qpdf and Poppler command-line tools."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tests'))
from test_incremental_ocr_layer import make_pdf, layer, E

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    base = make_pdf()
    output = E(base).apply([layer()]).pdf_bytes
    parsed = []
    for label, data in [('base', base), ('output', output)]:
        path = root / (label + '.pdf')
        path.write_bytes(data)
        subprocess.run(['qpdf', '--check', str(path)], check=True)
        parsed.append(json.loads(subprocess.check_output(['qpdf', '--json', str(path)])))
        subprocess.run(['pdftoppm', '-r', '72', str(path), str(root / label)], check=True)
    for page in (1, 2):
        assert (root / f'base-{page}.ppm').read_bytes() == (root / f'output-{page}.ppm').read_bytes()
    print('Both rendered pages are pixel-identical after adding invisible OCR text')
    text = subprocess.check_output(['pdftotext', str(root / 'output.pdf'), '-']).decode()
    print('Poppler text:', repr(text))
    text_ok = 'ORIGINAL' in text and 'café 世界 😀' in text
    before, after = (data['qpdf'][1] for data in parsed)
    for number in (1, 2, 4, 5, 6, 7, 8, 9):
        assert before[f'obj:{number} 0 R'] == after[f'obj:{number} 0 R'], number
    page = after['obj:3 0 R']['value']
    assert page['/Contents'][0] == '8 0 R' and len(page['/Contents']) == 2
    assert page['/Annots'] == ['7 0 R'] and page['/Rotate'] == 90
    assert page['/Resources']['/Font']['/F1'] == '5 0 R'
    assert page['/Resources']['/XObject']['/Im1'] == '6 0 R'
    assert '/OxidizeOCR' in page['/Resources']['/Font']
    print('qpdf independently confirms preserved catalog, page tree, other page, font, image, annotation, original stream and metadata')
    assert text_ok, 'BLOCKER: Poppler does not recover the complete Unicode OCR text'
