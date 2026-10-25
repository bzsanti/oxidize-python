"""Strict consumer for parser/recovery configuration and repair results."""
from typing import Literal
from oxidize_pdf import ParseOptions, RecoveryOptions, RepairStrategy, RepairResult, repair_pdf

options = ParseOptions(preferred_encoding='windows-1252', log_recovery_details=True)
encoding: Literal['utf-8', 'latin-1', 'windows-1252', 'mac-roman', 'pdf-doc', 'mixed'] | None = options.preferred_encoding
logging: bool = ParseOptions.tolerant().log_recovery_details
recovery = RecoveryOptions(partial_content=False, memory_limit=0, max_errors=0)
partial: bool = recovery.partial_content
limit: int = recovery.memory_limit
result: RepairResult = repair_pdf('input.pdf', RepairStrategy.EXTRACT_CONTENT, recovery)
success: bool = result.success
pages: int = result.pages_recovered
objects: int = result.objects_recovered
warnings: list[str] = result.warnings
is_partial: bool = result.is_partial
content: bytes | None = result.repaired_bytes
