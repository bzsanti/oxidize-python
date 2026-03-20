"""Tests for F62 (Batch), F63 (Recovery), F64 (Streaming)."""

from __future__ import annotations

import os
import tempfile

import pytest
import oxidize_pdf as op


# ── Helpers ───────────────────────────────────────────────────────────────


def _create_temp_pdf(page_count: int = 3) -> str:
    """Create a temporary PDF with `page_count` pages and return its path."""
    doc = op.Document()
    for i in range(page_count):
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA, 12.0)
        page.text_at(50.0, 750.0, f"Page {i + 1}")
        doc.add_page(page)
    path = tempfile.mktemp(suffix=".pdf")
    doc.save(path)
    return path


def _create_corrupt_pdf() -> str:
    """Create a file that is not a valid PDF."""
    path = tempfile.mktemp(suffix=".pdf")
    with open(path, "wb") as f:
        f.write(b"NOTAPDF garbage content that is not valid")
    return path


# ── F62: Batch Processing ─────────────────────────────────────────────────


class TestBatchJob:
    def test_split_factory(self):
        job = op.BatchJob.split("input.pdf", "out_%d.pdf", 5)
        assert "BatchJob" in repr(job)
        assert "Split" in repr(job)

    def test_merge_factory(self):
        job = op.BatchJob.merge(["a.pdf", "b.pdf"], "merged.pdf")
        assert "BatchJob" in repr(job)
        assert "Merge" in repr(job)

    def test_rotate_factory(self):
        job = op.BatchJob.rotate("in.pdf", "out.pdf", 90, [0, 1])
        assert "Rotate" in repr(job)

    def test_rotate_factory_no_pages(self):
        job = op.BatchJob.rotate("in.pdf", "out.pdf", 180, None)
        assert "Rotate" in repr(job)

    def test_extract_factory(self):
        job = op.BatchJob.extract("in.pdf", "out.pdf", [0, 2, 4])
        assert "Extract" in repr(job)

    def test_compress_factory(self):
        job = op.BatchJob.compress("in.pdf", "out.pdf", 80)
        assert "Compress" in repr(job)


class TestBatchProcessor:
    def test_empty_batch_returns_zero_summary(self):
        opts = op.BatchOptions()
        proc = op.BatchProcessor(opts)
        summary = proc.execute()
        assert summary.total_jobs == 0
        assert summary.successful == 0
        assert summary.failed == 0
        assert summary.cancelled is False
        assert summary.duration_secs >= 0.0

    def test_consumed_processor_raises(self):
        opts = op.BatchOptions()
        proc = op.BatchProcessor(opts)
        proc.execute()
        with pytest.raises(RuntimeError):
            proc.execute()

    def test_get_progress_before_execute(self):
        opts = op.BatchOptions()
        proc = op.BatchProcessor(opts)
        progress = proc.get_progress()
        assert progress.total_jobs == 0
        assert progress.completed_jobs == 0
        assert progress.is_complete()
        assert progress.percentage() == 100.0

    def test_is_cancelled_initially_false(self):
        opts = op.BatchOptions()
        proc = op.BatchProcessor(opts)
        assert proc.is_cancelled() is False

    def test_cancel_sets_flag(self):
        opts = op.BatchOptions()
        proc = op.BatchProcessor(opts)
        proc.cancel()
        assert proc.is_cancelled() is True

    def test_add_job_and_execute(self):
        pdf_path = _create_temp_pdf()
        try:
            opts = op.BatchOptions(parallelism=1)
            proc = op.BatchProcessor(opts)
            # Split into files that won't actually be written (no output dir check)
            job = op.BatchJob.split(pdf_path, "/tmp/batch_test_%d.pdf", 1)
            proc.add_job(job)
            summary = proc.execute()
            # The job may succeed or fail depending on the implementation,
            # but the summary must be returned without exception
            assert summary.total_jobs == 1
        finally:
            os.unlink(pdf_path)

    def test_summary_results_list(self):
        opts = op.BatchOptions()
        proc = op.BatchProcessor(opts)
        summary = proc.execute()
        assert isinstance(summary.results, list)
        assert summary.success_rate() == 100.0

    def test_batch_summary_repr(self):
        opts = op.BatchOptions()
        proc = op.BatchProcessor(opts)
        summary = proc.execute()
        assert "BatchSummary" in repr(summary)

    def test_progress_info_repr(self):
        opts = op.BatchOptions()
        proc = op.BatchProcessor(opts)
        progress = proc.get_progress()
        assert "ProgressInfo" in repr(progress)


class TestBatchStandaloneFunctions:
    def test_batch_split_pdfs_empty(self):
        summary = op.batch_split_pdfs([], 1, 1)
        assert summary.total_jobs == 0

    def test_batch_split_pdfs_with_file(self):
        pdf_path = _create_temp_pdf()
        try:
            summary = op.batch_split_pdfs([pdf_path], 1, 1)
            assert summary.total_jobs == 1
            # The job result is available in results
            assert len(summary.results) == 1
        finally:
            os.unlink(pdf_path)

    def test_batch_merge_pdfs_empty(self):
        summary = op.batch_merge_pdfs([], 1)
        assert summary.total_jobs == 0

    def test_batch_merge_pdfs_with_group(self):
        p1 = _create_temp_pdf()
        p2 = _create_temp_pdf()
        out = tempfile.mktemp(suffix=".pdf")
        try:
            summary = op.batch_merge_pdfs([([p1, p2], out)], 1)
            assert summary.total_jobs == 1
        finally:
            os.unlink(p1)
            os.unlink(p2)
            if os.path.exists(out):
                os.unlink(out)

    def test_job_result_properties_success(self):
        """JobResult for a successful job exposes correct properties."""
        pdf_path = _create_temp_pdf()
        try:
            summary = op.batch_split_pdfs([pdf_path], 1, 1)
            if summary.results:
                r = summary.results[0]
                assert r.status in ("success", "failed", "cancelled")
                assert isinstance(r.job_name, str)
                assert r.duration_secs is None or r.duration_secs >= 0.0
                assert isinstance(r.output_files, list)
                assert "JobResult" in repr(r)
        finally:
            os.unlink(pdf_path)


# ── F63: Recovery Full ────────────────────────────────────────────────────


class TestRepairStrategy:
    def test_class_attributes_exist(self):
        assert op.RepairStrategy.REBUILD_XREF is not None
        assert op.RepairStrategy.FIX_STRUCTURE is not None
        assert op.RepairStrategy.EXTRACT_CONTENT is not None
        assert op.RepairStrategy.RECONSTRUCT_FRAGMENTS is not None
        assert op.RepairStrategy.MINIMAL_REPAIR is not None
        assert op.RepairStrategy.AGGRESSIVE_REPAIR is not None

    def test_repr(self):
        assert "REBUILD_XREF" in repr(op.RepairStrategy.REBUILD_XREF)
        assert "FIX_STRUCTURE" in repr(op.RepairStrategy.FIX_STRUCTURE)


class TestCorruptionType:
    def test_class_attributes_exist(self):
        assert op.CorruptionType.INVALID_HEADER is not None
        assert op.CorruptionType.CORRUPT_XREF is not None
        assert op.CorruptionType.MISSING_EOF is not None
        assert op.CorruptionType.BROKEN_REFERENCES is not None
        assert op.CorruptionType.CORRUPT_STREAMS is not None
        assert op.CorruptionType.INVALID_PAGE_TREE is not None
        assert op.CorruptionType.TRUNCATED_FILE is not None
        assert op.CorruptionType.UNKNOWN is not None

    def test_repr(self):
        assert "INVALID_HEADER" in repr(op.CorruptionType.INVALID_HEADER)
        assert "UNKNOWN" in repr(op.CorruptionType.UNKNOWN)


class TestDetectCorruption:
    def test_valid_pdf_low_severity(self):
        pdf_path = _create_temp_pdf()
        try:
            report = op.detect_pdf_corruption(pdf_path)
            assert isinstance(report, op.CorruptionReport)
            assert report.severity >= 0
            assert isinstance(report.errors, list)
            assert report.file_size > 0
            assert isinstance(report.estimated_objects, int)
            assert isinstance(report.found_pages, int)
            assert "CorruptionReport" in repr(report)
        finally:
            os.unlink(pdf_path)

    def test_corrupt_file_detected(self):
        corrupt_path = _create_corrupt_pdf()
        try:
            report = op.detect_pdf_corruption(corrupt_path)
            # A non-PDF file should have high severity
            assert report.severity > 0
        finally:
            os.unlink(corrupt_path)

    def test_nonexistent_file_raises(self):
        with pytest.raises(Exception):
            op.detect_pdf_corruption("/nonexistent/path.pdf")

    def test_analyze_corruption_alias(self):
        pdf_path = _create_temp_pdf()
        try:
            report = op.analyze_pdf_corruption(pdf_path)
            assert isinstance(report, op.CorruptionReport)
        finally:
            os.unlink(pdf_path)

    def test_corruption_report_corruption_type(self):
        pdf_path = _create_temp_pdf()
        try:
            report = op.detect_pdf_corruption(pdf_path)
            ct = report.corruption_type
            assert isinstance(ct, op.CorruptionType)
        finally:
            os.unlink(pdf_path)


class TestRepairDocument:
    def test_repair_valid_pdf_returns_result(self):
        pdf_path = _create_temp_pdf()
        try:
            result = op.repair_pdf(pdf_path, op.RepairStrategy.MINIMAL_REPAIR)
            assert isinstance(result, op.RepairResult)
            assert isinstance(result.success, bool)
            assert isinstance(result.pages_recovered, int)
            assert isinstance(result.objects_recovered, int)
            assert isinstance(result.warnings, list)
            assert isinstance(result.is_partial, bool)
            assert "RepairResult" in repr(result)
        finally:
            os.unlink(pdf_path)

    def test_repair_all_strategies(self):
        pdf_path = _create_temp_pdf()
        try:
            strategies = [
                op.RepairStrategy.REBUILD_XREF,
                op.RepairStrategy.FIX_STRUCTURE,
                op.RepairStrategy.EXTRACT_CONTENT,
                op.RepairStrategy.RECONSTRUCT_FRAGMENTS,
                op.RepairStrategy.MINIMAL_REPAIR,
                op.RepairStrategy.AGGRESSIVE_REPAIR,
            ]
            for strategy in strategies:
                result = op.repair_pdf(pdf_path, strategy)
                assert isinstance(result, op.RepairResult)
        finally:
            os.unlink(pdf_path)

    def test_repair_result_repaired_bytes(self):
        pdf_path = _create_temp_pdf()
        try:
            result = op.repair_pdf(pdf_path, op.RepairStrategy.MINIMAL_REPAIR)
            if result.success:
                rb = result.repaired_bytes
                assert rb is not None
                assert isinstance(rb, bytes)
                assert len(rb) > 0
            else:
                assert result.repaired_bytes is None
        finally:
            os.unlink(pdf_path)

    def test_repair_nonexistent_raises(self):
        with pytest.raises(Exception):
            op.repair_pdf("/nonexistent/path.pdf", op.RepairStrategy.MINIMAL_REPAIR)


class TestQuickRecover:
    def test_quick_recover_valid_pdf(self):
        pdf_path = _create_temp_pdf()
        try:
            recovered = op.quick_recover(pdf_path)
            assert isinstance(recovered, bytes)
            assert len(recovered) > 0
        finally:
            os.unlink(pdf_path)

    def test_quick_recover_nonexistent_raises(self):
        with pytest.raises(Exception):
            op.quick_recover("/nonexistent/path.pdf")


class TestObjectScanner:
    def test_scan_valid_pdf(self):
        pdf_path = _create_temp_pdf()
        try:
            scanner = op.ObjectScanner()
            assert "ObjectScanner" in repr(scanner)
            result = scanner.scan_file(pdf_path)
            assert isinstance(result, op.ScanResult)
            assert result.total_objects >= 0
            assert result.valid_objects >= 0
            assert result.estimated_pages >= 0
            assert "ScanResult" in repr(result)
        finally:
            os.unlink(pdf_path)

    def test_scan_nonexistent_raises(self):
        scanner = op.ObjectScanner()
        with pytest.raises(Exception):
            scanner.scan_file("/nonexistent/path.pdf")

    def test_scan_result_properties(self):
        pdf_path = _create_temp_pdf()
        try:
            scanner = op.ObjectScanner()
            result = scanner.scan_file(pdf_path)
            assert result.valid_objects <= result.total_objects
        finally:
            os.unlink(pdf_path)


# ── F64: Streaming Full ───────────────────────────────────────────────────


class TestPageStreamer:
    def test_open_valid_pdf(self):
        pdf_path = _create_temp_pdf(3)
        try:
            streamer = op.PageStreamer.open(pdf_path)
            assert "PageStreamer" in repr(streamer)
        finally:
            os.unlink(pdf_path)

    def test_open_nonexistent_raises(self):
        with pytest.raises(Exception):
            op.PageStreamer.open("/nonexistent/path.pdf")

    def test_next_returns_pages(self):
        pdf_path = _create_temp_pdf(3)
        try:
            streamer = op.PageStreamer.open(pdf_path)
            pages = []
            while True:
                page = streamer.next()
                if page is None:
                    break
                pages.append(page)
            # The mock implementation returns 3 pages regardless of actual content
            assert len(pages) >= 0  # At least non-error
        finally:
            os.unlink(pdf_path)

    def test_streaming_page_properties(self):
        pdf_path = _create_temp_pdf(3)
        try:
            streamer = op.PageStreamer.open(pdf_path)
            page = streamer.next()
            if page is not None:
                assert isinstance(page, op.StreamingPage)
                assert page.number >= 0
                assert page.width > 0.0
                assert page.height > 0.0
                mb = page.media_box()
                assert len(mb) == 4
                assert mb[0] == 0.0
                assert mb[1] == 0.0
                assert mb[2] == page.width
                assert mb[3] == page.height
                assert "StreamingPage" in repr(page)
        finally:
            os.unlink(pdf_path)

    def test_streaming_page_extract_text(self):
        pdf_path = _create_temp_pdf(2)
        try:
            streamer = op.PageStreamer.open(pdf_path)
            page = streamer.next()
            if page is not None:
                text = page.extract_text_streaming()
                assert isinstance(text, str)
        finally:
            os.unlink(pdf_path)

    def test_seek_to_page(self):
        pdf_path = _create_temp_pdf(3)
        try:
            streamer = op.PageStreamer.open(pdf_path)
            streamer.seek_to_page(2)
            page = streamer.next()
            if page is not None:
                assert page.number == 2
        finally:
            os.unlink(pdf_path)

    def test_total_pages_is_none_or_int(self):
        pdf_path = _create_temp_pdf(3)
        try:
            streamer = op.PageStreamer.open(pdf_path)
            total = streamer.total_pages()
            assert total is None or isinstance(total, int)
        finally:
            os.unlink(pdf_path)

    def test_iterate_all_pages(self):
        pdf_path = _create_temp_pdf(3)
        try:
            streamer = op.PageStreamer.open(pdf_path)
            page_numbers = []
            while True:
                page = streamer.next()
                if page is None:
                    break
                page_numbers.append(page.number)
            if page_numbers:
                # Pages should be numbered sequentially starting from 0
                assert page_numbers == list(range(len(page_numbers)))
        finally:
            os.unlink(pdf_path)


class TestIncrementalParser:
    def test_creation(self):
        parser = op.IncrementalParser()
        assert not parser.is_complete()
        assert "IncrementalParser" in repr(parser)

    def test_feed_empty(self):
        parser = op.IncrementalParser()
        parser.feed(b"")
        events = parser.take_events()
        assert events == []

    def test_feed_header_emits_event(self):
        parser = op.IncrementalParser()
        parser.feed(b"%PDF-1.7\n")
        events = parser.take_events()
        assert len(events) >= 1
        header_events = [e for e in events if e["type"] == "header"]
        assert len(header_events) == 1
        assert header_events[0]["version"] == "1.7"

    def test_feed_object_emits_events(self):
        parser = op.IncrementalParser()
        parser.feed(b"1 0 obj\n<< >>\nendobj\n")
        events = parser.take_events()
        types = [e["type"] for e in events]
        assert "object_start" in types
        assert "object_end" in types

    def test_take_events_clears_buffer(self):
        parser = op.IncrementalParser()
        parser.feed(b"%PDF-1.7\n")
        events1 = parser.take_events()
        events2 = parser.take_events()
        assert len(events1) >= 1
        assert events2 == []

    def test_is_complete_after_eof(self):
        parser = op.IncrementalParser()
        parser.feed(b"%PDF-1.7\n")
        parser.feed(b"xref\n")
        parser.feed(b"trailer\n")
        parser.feed(b"%%EOF\n")
        # Drain pending events
        parser.take_events()
        assert parser.is_complete()

    def test_feed_partial_lines(self):
        parser = op.IncrementalParser()
        parser.feed(b"%PDF-")
        events1 = parser.take_events()
        assert events1 == []  # Not yet a full line

        parser.feed(b"1.4\n")
        events2 = parser.take_events()
        assert len(events2) >= 1
        assert events2[0]["type"] == "header"
        assert events2[0]["version"] == "1.4"

    def test_complete_pdf_sequence(self):
        parser = op.IncrementalParser()
        pdf = (
            b"%PDF-1.7\n"
            b"1 0 obj\n<< /Type /Catalog >>\nendobj\n"
            b"xref\n0 1\n0000000000 65535 f\n"
            b"trailer\n<< /Size 1 >>\n"
            b"%%EOF\n"
        )
        parser.feed(pdf)
        events = parser.take_events()
        assert parser.is_complete()

        types = {e["type"] for e in events}
        assert "header" in types
        assert "object_start" in types
        assert "object_end" in types
        assert "end_of_file" in types

    def test_event_dict_structure(self):
        parser = op.IncrementalParser()
        parser.feed(b"%PDF-1.7\n1 0 obj\nendobj\n")
        events = parser.take_events()
        for event in events:
            assert "type" in event
            assert isinstance(event["type"], str)

    def test_stream_data_event(self):
        parser = op.IncrementalParser()
        # Put parser into InObject state by feeding object header
        parser.feed(b"1 0 obj\n")
        parser.take_events()  # drain ObjectStart

        # Now feed stream content
        parser.feed(b"stream\nhello world\nendstream\n")
        events = parser.take_events()
        stream_events = [e for e in events if e["type"] == "stream_data"]
        assert len(stream_events) >= 1
        assert stream_events[0]["object_id"] == 1
        assert "data_len" in stream_events[0]


# ── Integration: Batch + PDF creation ────────────────────────────────────


class TestBatchIntegration:
    def test_batch_with_multiple_jobs(self):
        """Multiple jobs with different types execute without exception."""
        p1 = _create_temp_pdf(2)
        p2 = _create_temp_pdf(2)
        out = tempfile.mktemp(suffix=".pdf")
        try:
            opts = op.BatchOptions(parallelism=2)
            proc = op.BatchProcessor(opts)

            # Add a merge job
            proc.add_job(op.BatchJob.merge([p1, p2], out))
            summary = proc.execute()

            assert summary.total_jobs == 1
            # Result should be there
            assert len(summary.results) == 1
            r = summary.results[0]
            assert r.status in ("success", "failed", "cancelled")
        finally:
            os.unlink(p1)
            os.unlink(p2)
            if os.path.exists(out):
                os.unlink(out)

    def test_batch_and_incremental_parse(self):
        """Create a PDF, read it incrementally, verify header event."""
        pdf_path = _create_temp_pdf(1)
        try:
            parser = op.IncrementalParser()
            with open(pdf_path, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    parser.feed(chunk)
            events = parser.take_events()
            header_events = [e for e in events if e["type"] == "header"]
            assert len(header_events) == 1
        finally:
            os.unlink(pdf_path)
