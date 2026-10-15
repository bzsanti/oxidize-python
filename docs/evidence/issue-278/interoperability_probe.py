"""Discriminating output probes; modifies only disposable PDFs, never core/binding."""
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tests'))
from test_incremental_ocr_layer import E, make_pdf, layer

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    for label, text in [('ascii', 'searchable'), ('unicode', 'café 世界 😀')]:
        output = E(make_pdf()).apply([layer(text=text)]).pdf_bytes
        path = root / (label + '.pdf')
        path.write_bytes(output)
        extracted = subprocess.check_output(['pdftotext', str(path), '-']).decode()
        print(label, 'original:', repr(extracted))
        subprocess.run(['qpdf', '--qdf', '--object-streams=disable', str(path), str(root / 'output.qdf')], check=True)
        source = (root / 'output.qdf').read_bytes()
        for variant, replacements in [
            ('tag', [(b'/OCR << /ActualText', b'/Span << /ActualText')]),
            ('scale', [(b'1000.000000 Tz', b'100.000000 Tz')]),
            ('both', [(b'/OCR << /ActualText', b'/Span << /ActualText'), (b'1000.000000 Tz', b'100.000000 Tz')]),
        ]:
            data = source
            for old, new in replacements:
                assert old in data
                data = data.replace(old, new)
            raw = root / 'changed.qdf'
            raw.write_bytes(data)
            fixed = root / 'changed.pdf'
            fixed.write_bytes(subprocess.check_output(['fix-qdf', str(raw)]))
            result = subprocess.check_output(['pdftotext', str(fixed), '-']).decode()
            print(label, variant, repr(result))
            if variant in ('tag', 'both'):
                assert text in result
            if label == 'unicode' and variant == 'scale':
                assert text not in result
