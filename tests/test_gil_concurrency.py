"""#115 Capa C: heavy standalone ops must release the GIL so concurrent calls
run in parallel instead of serializing on a single core.

These tests are behavioral, not smoke: they assert that running the same total
amount of work across a thread pool is meaningfully faster than running it
serially, with CPU consumption demonstrating actual multicore execution.
Wall-time speedup alone can be caused by scheduling noise; both signals are
required. Rust operations release the GIL with ``Python::detach``.
"""

import os
import sys
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter, process_time

import pytest

pytestmark = pytest.mark.skipif(
    (os.cpu_count() or 1) < 2,
    reason="GIL-release parallelism is unobservable on a single core",
)

# Total work units per measurement and concurrent workers. Comparing
# parallel-of-N against serial-of-N is self-calibrating: it cancels out the
# machine's absolute speed and isolates the concurrency factor.
_TASKS = 8
_WORKERS = 4
# Conservative: with the GIL released and 4 workers, parallel should be well
# under half the serial time; 0.7 leaves wide margin for scheduling noise while
# still failing decisively when the op holds the GIL (ratio ~1.0).
_MAX_PARALLEL_RATIO = 0.7
# #247: wall speedup alone can reflect a scheduling pause in the serial sample.
# A GIL-bound CPU loop cannot consume more than one CPU-second per wall-second.
# Require multicore CPU use as well, with margin for timer resolution/overhead.
_MIN_CPU_PARALLELISM = 1.2
# #150: a single noisy pair on a shared runner is not a regression. Keep the
# same threshold, but give the operation up to three independent pairs.
_MAX_ATTEMPTS = 3


@pytest.fixture(scope="module")
def large_pdf(tmp_path_factory):
    """A PDF heavy enough that one validate pass is not instantaneous."""
    from oxidize_pdf import Document, Font, Page

    path = tmp_path_factory.mktemp("gil") / "large.pdf"
    doc = Document()
    doc.set_title("GIL concurrency fixture")
    for p in range(300):
        page = Page.a4()
        page.set_font(Font.HELVETICA, 9.0)
        for row in range(60):
            page.text_at(40.0, float(800 - row * 12), f"page {p} row {row} " * 4)
        doc.add_page(page)
    doc.save(str(path))
    return str(path)


def _measure_serial(op, n):
    start = perf_counter()
    for _ in range(n):
        op()
    return perf_counter() - start


def _measure_parallel(op, n, workers):
    start = perf_counter()
    cpu_start = process_time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(lambda _: op(), range(n)))
    cpu = process_time() - cpu_start
    return perf_counter() - start, cpu


def _assert_parallel_speedup(op):
    op()  # warm up caches / one-time init outside the measurement
    samples = []
    for attempt in range(_MAX_ATTEMPTS):
        # Alternate order so warm caches or a changing runner load do not
        # systematically favour either serial or parallel execution.
        if attempt % 2 == 0:
            serial = _measure_serial(op, _TASKS)
            parallel, cpu = _measure_parallel(op, _TASKS, _WORKERS)
        else:
            parallel, cpu = _measure_parallel(op, _TASKS, _WORKERS)
            serial = _measure_serial(op, _TASKS)
        samples.append((serial, parallel, cpu))
        if parallel < serial * _MAX_PARALLEL_RATIO and cpu > parallel * _MIN_CPU_PARALLELISM:
            return
    detail = "; ".join(
        f"parallel={parallel:.3f}s serial={serial:.3f}s ratio={parallel / serial:.2f} cpu/wall={cpu / parallel:.2f}"
        for serial, parallel, cpu in samples
    )
    pytest.fail(
        f"no GIL-release parallelism in {_MAX_ATTEMPTS} attempts: {detail} "
        f"(expected < {_MAX_PARALLEL_RATIO}; cpu/wall > {_MIN_CPU_PARALLELISM})"
    )


def test_validate_pdf_releases_gil(large_pdf):
    from oxidize_pdf import validate_pdf

    _assert_parallel_speedup(lambda: validate_pdf(large_pdf))


def test_detect_corruption_releases_gil(large_pdf):
    from oxidize_pdf import detect_pdf_corruption

    _assert_parallel_speedup(lambda: detect_pdf_corruption(large_pdf))


def test_extract_text_releases_gil(large_pdf):
    """Reader method: extract_text over all pages must release the GIL.

    Requires oxidize-pdf core >= 3.0.4, where PdfDocument is Send and the
    binding can wrap the extraction in Python::detach. Each task opens its own
    reader because PdfReader is unsendable (one per worker thread).
    """
    from oxidize_pdf import PdfReader

    def op():
        PdfReader.open(large_pdf).extract_text()

    _assert_parallel_speedup(op)


@pytest.mark.parametrize("ratios", [(0.60,), (0.78, 0.65), (0.90, 0.78, 0.65)])
def test_speedup_guard_retries_only_noisy_samples(monkeypatch, ratios):
    """#150's reported 0.78 must get another measurement, not a wider threshold."""
    remaining = iter(ratios)
    calls = []

    def serial(op, n):
        calls.append("serial")
        return 10.0

    def parallel(op, n, workers):
        calls.append("parallel")
        wall = 10.0 * next(remaining)
        return wall, wall * 2.0

    monkeypatch.setattr(sys.modules[__name__], "_measure_serial", serial)
    monkeypatch.setattr(sys.modules[__name__], "_measure_parallel", parallel)
    _assert_parallel_speedup(lambda: None)
    assert calls == ["serial", "parallel", "parallel", "serial", "serial", "parallel"][:2 * len(ratios)]


@pytest.mark.parametrize("ratio", [0.70, 0.78, 1.0])
def test_speedup_guard_rejects_sustained_slowdown(monkeypatch, ratio):
    monkeypatch.setattr(sys.modules[__name__], "_measure_serial", lambda op, n: 10.0)
    monkeypatch.setattr(
        sys.modules[__name__], "_measure_parallel", lambda op, n, workers: (10.0 * ratio, 20.0 * ratio),
    )
    with pytest.raises(pytest.fail.Exception, match="in 3 attempts") as failure:
        _assert_parallel_speedup(lambda: None)
    assert str(failure.value).count(f"ratio={ratio:.2f}") == 3
    assert "expected < 0.7" in str(failure.value)


def test_speedup_guard_propagates_operation_failure():
    def broken():
        raise RuntimeError("operation failed")

    with pytest.raises(RuntimeError, match="operation failed"):
        _assert_parallel_speedup(broken)


@pytest.mark.skipif(
    sys.implementation.name != "cpython"
    or (hasattr(sys, "_is_gil_enabled") and not sys._is_gil_enabled()),
    reason="the negative control requires CPython with the GIL enabled",
)
def test_speedup_guard_rejects_real_gil_bound_work():
    """Real negative control: CPython's integer sum loop does not release the GIL.

    It must still fail after all retries; this guards against turning a noise
    mitigation into an unconditional pass. No mocked timers or PDF operations.
    """
    with pytest.raises(pytest.fail.Exception, match="no GIL-release parallelism in 3 attempts"):
        _assert_parallel_speedup(lambda: sum(range(4_000_000)))


@pytest.mark.parametrize("cpu_ratio", [0.8, 1.0, 1.2])
def test_speedup_guard_rejects_wall_only_speedup(monkeypatch, cpu_ratio):
    """A paused serial sample cannot certify parallelism for a single-core loop."""
    monkeypatch.setattr(sys.modules[__name__], "_measure_serial", lambda op, n: 10.0)
    monkeypatch.setattr(sys.modules[__name__], "_measure_parallel", lambda op, n, workers: (6.0, 6.0 * cpu_ratio))
    with pytest.raises(pytest.fail.Exception, match="cpu/wall"):
        _assert_parallel_speedup(lambda: None)
