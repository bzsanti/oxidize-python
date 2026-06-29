"""#115 Capa C: heavy standalone ops must release the GIL so concurrent calls
run in parallel instead of serializing on a single core.

These tests are behavioral, not smoke: they assert that running the same total
amount of work across a thread pool is meaningfully faster than running it
serially. That speedup only exists when the Rust op releases the GIL via
``Python::allow_threads``. Before that change the wall-clock is ~serial.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

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
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(lambda _: op(), range(n)))
    return perf_counter() - start


def _assert_parallel_speedup(op):
    op()  # warm up caches / one-time init outside the measurement
    serial = _measure_serial(op, _TASKS)
    parallel = _measure_parallel(op, _TASKS, _WORKERS)
    assert parallel < serial * _MAX_PARALLEL_RATIO, (
        f"no GIL-release parallelism: parallel={parallel:.3f}s "
        f"serial={serial:.3f}s ratio={parallel / serial:.2f} "
        f"(expected < {_MAX_PARALLEL_RATIO})"
    )


def test_validate_pdf_releases_gil(large_pdf):
    from oxidize_pdf import validate_pdf

    _assert_parallel_speedup(lambda: validate_pdf(large_pdf))


def test_detect_corruption_releases_gil(large_pdf):
    from oxidize_pdf import detect_pdf_corruption

    _assert_parallel_speedup(lambda: detect_pdf_corruption(large_pdf))
