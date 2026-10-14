from typing import Callable
from oxidize_pdf import BatchOptions, BatchProcessor, ProgressInfo

def progress(info: ProgressInfo) -> None:
    total: int = info.total_jobs
    elapsed: float = info.elapsed_secs()
    print(total, elapsed, info.is_complete())

options = BatchOptions(2, True, memory_limit_per_worker=1024,
                       progress_interval=0.05, progress_callback=progress,
                       job_timeout=None)
callback: Callable[[ProgressInfo], None] | None = options.progress_callback
seconds: float | None = options.job_timeout
bytes_per_worker: int = options.memory_limit_per_worker
parallelism: int = options.parallelism
stop: bool = options.stop_on_error
interval: float = options.progress_interval
summary = BatchProcessor(options).execute()
print(summary.total_jobs)
