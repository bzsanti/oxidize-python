"""Execution contracts changed by registry core 5.5.3 adoption."""
import subprocess
import sys

import pytest


@pytest.mark.parametrize("mode", ["rotate", "compress_new", "compress_existing"])
def test_batch_core_553_execution(tmp_path, mode):
    # Run the real executor in a child so a retained GIL cannot hang the suite.
    script = r"""
import sys
from pathlib import Path
import oxidize_pdf as op
root, mode = Path(sys.argv[1]), sys.argv[2]
source, output = root / 'source.pdf', root / 'result.pdf'
document = op.Document()
for rotation in [90, 0]:
    page = op.Page.a4()
    page.set_rotation(rotation)
    page.set_font(op.Font.HELVETICA, 12)
    page.text_at(50, 700, 'Batch adoption')
    document.add_page(page)
document.save(str(source))
original = source.read_bytes()
processor = op.BatchProcessor(op.BatchOptions(parallelism=1))
if mode == 'rotate':
    processor.add_job(op.BatchJob.rotate(str(source), str(output), 90, [0]))
    summary = processor.execute()
    assert (summary.successful, summary.failed) == (1, 0)
    reader = op.PdfReader.open(str(output))
    assert reader.page_count == 2
    assert [reader.get_page(i).rotation for i in range(2)] == [180, 0]
else:
    sentinel = b'existing destination must survive'
    if mode == 'compress_existing':
        output.write_bytes(sentinel)
    processor.add_job(op.BatchJob.compress(str(source), str(output), 80))
    summary = processor.execute()
    assert (summary.successful, summary.failed) == (0, 1)
    assert summary.results[0].error
    if mode == 'compress_existing':
        assert output.read_bytes() == sentinel
    else:
        assert not output.exists()
assert source.read_bytes() == original
"""
    subprocess.run([sys.executable, "-c", script, str(tmp_path), mode],
                   check=True, timeout=30)
