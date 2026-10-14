"""Public BatchOptions contract and real executor behavior (#257)."""
import subprocess
import sys

import pytest
import oxidize_pdf as op


def test_defaults_and_explicit_options():
    default = op.BatchOptions()
    assert 1 <= default.parallelism <= 8
    assert default.stop_on_error is False
    assert default.memory_limit_per_worker == 512 * 1024 * 1024
    assert default.progress_interval == 0.1
    assert default.job_timeout == 300.0
    assert default.progress_callback is None
    callback = lambda info: None
    custom = op.BatchOptions(2, True, memory_limit_per_worker=123,
                             progress_interval=0.025, job_timeout=None,
                             progress_callback=callback)
    assert custom.parallelism == 2
    assert custom.stop_on_error is True
    assert custom.memory_limit_per_worker == 123
    assert custom.progress_interval == 0.025
    assert custom.job_timeout is None
    assert custom.progress_callback is callback
    assert op.BatchOptions(job_timeout=1.25).job_timeout == 1.25
    with pytest.raises(AttributeError):
        custom.parallelism = 3


@pytest.mark.parametrize('field', ['parallelism', 'memory_limit_per_worker'])
@pytest.mark.parametrize('value', [0, -1, 2**100])
def test_invalid_counts(field, value):
    with pytest.raises((ValueError, OverflowError)):
        op.BatchOptions(**{field: value})


@pytest.mark.parametrize('field', ['progress_interval', 'job_timeout'])
@pytest.mark.parametrize('value', [0, -1, float('nan'), float('inf'), 1e100, 1e-20])
def test_invalid_durations(field, value):
    with pytest.raises(ValueError):
        op.BatchOptions(**{field: value})


def test_invalid_callback():
    with pytest.raises(TypeError, match='callable'):
        op.BatchOptions(progress_callback=42)


def test_executor_callbacks_errors_and_limits(tmp_path):
    # A retained GIL deadlocks the native progress thread. Bound the entire real
    # execution, including callback exceptions, reuse and cancellation.
    script = r'''
import sys
from pathlib import Path
import oxidize_pdf as op
root = Path(sys.argv[1])
doc = op.Document()
page = op.Page.a4()
page.set_font(op.Font.HELVETICA, 12)
page.text_at(50, 750, 'Batch execution')
doc.add_page(page)
source = root / 'input.pdf'
doc.save(str(source))
seen = []
def callback(info):
    assert isinstance(info, op.ProgressInfo)
    seen.append(info)
options = op.BatchOptions(1, False, memory_limit_per_worker=1,
    job_timeout=1e-9, progress_interval=0.001, progress_callback=callback)
processor = op.BatchProcessor(options)
processor.add_job(op.BatchJob.split(str(source), str(root / 'part_{n}.pdf'), 1))
processor.add_job(op.BatchJob.split(str(root / 'missing.pdf'), str(root / 'bad_{n}.pdf'), 1))
summary = processor.execute()
assert (summary.total_jobs, summary.successful, summary.failed) == (2, 1, 1)
assert (root / 'part_1.pdf').read_bytes().startswith(b'%PDF-')
assert summary.results[0].duration_secs > options.job_timeout
assert summary.results[1].error
assert seen[-1].is_complete()
assert (seen[-1].total_jobs, seen[-1].completed_jobs, seen[-1].failed_jobs) == (2, 1, 1)
assert seen[-1].running_jobs == 0
assert seen[-1].elapsed_secs() >= 0
# The snapshots remain usable after the native executor has been consumed.
assert seen[0].total_jobs == 2
try:
    processor.execute()
except RuntimeError:
    pass
else:
    raise AssertionError('processor reused')
class CallbackFailure(Exception): pass
error = CallbackFailure('callback sentinel')
calls = []
def failing(info):
    calls.append(info)
    raise error
options = op.BatchOptions(progress_callback=failing, progress_interval=0.001)
for run in range(2):
    processor = op.BatchProcessor(options)
    processor.add_job(op.BatchJob.split(str(source), str(root / f'error{run}_{{n}}.pdf'), 1))
    try:
        processor.execute()
    except CallbackFailure as caught:
        assert caught is error
    else:
        raise AssertionError('callback error swallowed')
    assert (root / f'error{run}_1.pdf').exists()
assert len(calls) == 2  # independent error state and no repeated callbacks after error
assert op.BatchProcessor(options).execute().total_jobs == 0
processor = op.BatchProcessor(op.BatchOptions(stop_on_error=True, progress_callback=callback, progress_interval=0.001))
processor.add_job(op.BatchJob.split(str(root / 'missing.pdf'), str(root / 'stop_{n}.pdf'), 1))
summary = processor.execute()
assert summary.failed == 1 and summary.cancelled
processor = op.BatchProcessor(op.BatchOptions(progress_callback=callback))
processor.add_job(op.BatchJob.split(str(source), str(root / 'cancel_{n}.pdf'), 1))
processor.cancel()
summary = processor.execute()
assert summary.cancelled and summary.results[0].status == 'cancelled'
assert not (root / 'cancel_1.pdf').exists()
'''
    result = subprocess.run([sys.executable, '-c', script, str(tmp_path)],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('with_processor', [False, True])
def test_callback_reference_cycles_are_collected(with_processor):
    import gc
    import weakref

    class Callback:
        def __call__(self, info):
            pass

    callback = Callback()
    reference = weakref.ref(callback)
    options = op.BatchOptions(progress_callback=callback)
    callback.owner = op.BatchProcessor(options) if with_processor else options
    del callback, options
    gc.collect()
    assert reference() is None
