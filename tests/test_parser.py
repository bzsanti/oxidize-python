"""Tests for PDF parsing: PdfReader, reading pages, extracting text."""

import pytest


@pytest.fixture
def sample_pdf(tmp_dir):
    """Generate a sample PDF with known content for parsing tests."""
    from oxidize_pdf import Color, Document, Font, Page

    path = tmp_dir / "sample.pdf"

    doc = Document()
    doc.set_title("Test Document")
    doc.set_author("Test Author")

    page1 = Page.a4()
    page1.set_font(Font.HELVETICA, 12.0)
    page1.text_at(100.0, 700.0, "Hello from page 1")
    doc.add_page(page1)

    page2 = Page.letter()
    page2.set_font(Font.COURIER, 14.0)
    page2.text_at(100.0, 700.0, "Page two content")
    doc.add_page(page2)

    page3 = Page.a4()
    page3.set_fill_color(Color.red())
    page3.draw_rect(50.0, 50.0, 200.0, 100.0)
    page3.fill()
    doc.add_page(page3)

    doc.save(str(path))
    return path


class TestPdfReaderOpen:
    """Test opening PDF files."""

    def test_open_valid_pdf(self, sample_pdf):
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(sample_pdf))
        assert reader is not None

    def test_open_nonexistent_file(self):
        from oxidize_pdf import PdfIoError, PdfReader

        with pytest.raises(PdfIoError):
            PdfReader.open("/nonexistent/path/fake.pdf")

    def test_page_count(self, sample_pdf):
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(sample_pdf))
        assert reader.page_count == 3

    def test_version(self, sample_pdf):
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(sample_pdf))
        version = reader.version
        assert isinstance(version, str)
        assert version.startswith("1.")


class TestParsedPage:
    """Test accessing parsed page properties."""

    def test_get_page(self, sample_pdf):
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(sample_pdf))
        page = reader.get_page(0)
        assert page is not None

    def test_page_dimensions(self, sample_pdf):
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(sample_pdf))

        page0 = reader.get_page(0)
        assert abs(page0.width - 595.0) < 1.0  # A4
        assert abs(page0.height - 842.0) < 1.0

        page1 = reader.get_page(1)
        assert abs(page1.width - 612.0) < 1.0  # Letter
        assert abs(page1.height - 792.0) < 1.0

    def test_invalid_page_index(self, sample_pdf):
        from oxidize_pdf import PdfError, PdfReader

        reader = PdfReader.open(str(sample_pdf))
        with pytest.raises(PdfError):
            reader.get_page(999)


class TestTextExtraction:
    """Test extracting text from parsed PDFs."""

    def test_extract_text_from_page(self, sample_pdf):
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(sample_pdf))
        text = reader.extract_text_from_page(0)
        assert isinstance(text, str)
        assert "Hello" in text or "page 1" in text

    def test_extract_all_text(self, sample_pdf):
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(sample_pdf))
        texts = reader.extract_text()
        assert isinstance(texts, list)
        assert len(texts) == 3
        # Page 3 has only graphics, so its text should be empty or minimal
        assert isinstance(texts[0], str)


class TestReaderLen:
    """Test __len__ protocol."""

    def test_len(self, sample_pdf):
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(sample_pdf))
        assert len(reader) == 3

    def test_repr(self, sample_pdf):
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(sample_pdf))
        assert "PdfReader" in repr(reader)
        assert "3" in repr(reader)


class TestPdfReaderFromBytes:
    """Test opening PDFs from byte buffers (PARSE-002)."""

    @pytest.fixture
    def sample_pdf_bytes(self):
        """Generate a sample PDF as bytes."""
        from oxidize_pdf import Document, Font, Page

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Hello from bytes")
        doc.add_page(page)

        page2 = Page.letter()
        page2.set_font(Font.COURIER, 14.0)
        page2.text_at(100.0, 700.0, "Second page")
        doc.add_page(page2)

        return doc.save_to_bytes()

    def test_from_bytes_returns_reader(self, sample_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(sample_pdf_bytes)
        assert reader is not None

    def test_from_bytes_page_count(self, sample_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(sample_pdf_bytes)
        assert reader.page_count == 2

    def test_from_bytes_version(self, sample_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(sample_pdf_bytes)
        assert reader.version.startswith("1.")

    def test_from_bytes_extract_text(self, sample_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(sample_pdf_bytes)
        text = reader.extract_text_from_page(0)
        assert "Hello" in text or "bytes" in text

    def test_from_bytes_extract_all(self, sample_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(sample_pdf_bytes)
        texts = reader.extract_text()
        assert len(texts) == 2

    def test_from_bytes_get_page(self, sample_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(sample_pdf_bytes)
        page = reader.get_page(0)
        assert abs(page.width - 595.0) < 1.0  # A4

    def test_from_bytes_len(self, sample_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(sample_pdf_bytes)
        assert len(reader) == 2

    def test_from_bytes_repr(self, sample_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(sample_pdf_bytes)
        assert "PdfReader" in repr(reader)
        assert "2" in repr(reader)

    def test_from_bytes_invalid_data(self):
        from oxidize_pdf import PdfParseError, PdfReader

        with pytest.raises(PdfParseError):
            PdfReader.from_bytes(b"not a valid pdf")

    def test_from_bytes_empty(self):
        from oxidize_pdf import PdfParseError, PdfReader

        with pytest.raises(PdfParseError):
            PdfReader.from_bytes(b"")


class TestPdfReaderFromStream:
    """Test opening PDFs from binary streams (READ-003)."""

    @pytest.fixture
    def sample_pdf_bytes(self):
        """Generate a sample PDF as bytes for stream tests."""
        from oxidize_pdf import Document, Font, Page

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Hello from stream")
        doc.add_page(page)

        page2 = Page.letter()
        page2.set_font(Font.COURIER, 14.0)
        page2.text_at(100.0, 700.0, "Stream page two")
        doc.add_page(page2)

        return doc.save_to_bytes()

    def test_from_bytesio_page_count(self, sample_pdf_bytes):
        import io

        from oxidize_pdf import PdfReader

        stream = io.BytesIO(sample_pdf_bytes)
        reader = PdfReader.from_stream(stream)
        assert reader.page_count == 2

    def test_from_bytesio_extract_text(self, sample_pdf_bytes):
        import io

        from oxidize_pdf import PdfReader

        stream = io.BytesIO(sample_pdf_bytes)
        reader = PdfReader.from_stream(stream)
        text = reader.extract_text_from_page(0)
        assert "Hello" in text or "stream" in text

    def test_from_bytesio_version(self, sample_pdf_bytes):
        import io

        from oxidize_pdf import PdfReader

        stream = io.BytesIO(sample_pdf_bytes)
        reader = PdfReader.from_stream(stream)
        assert reader.version.startswith("1.")

    def test_from_bytesio_len(self, sample_pdf_bytes):
        import io

        from oxidize_pdf import PdfReader

        stream = io.BytesIO(sample_pdf_bytes)
        reader = PdfReader.from_stream(stream)
        assert len(reader) == 2

    def test_from_bytesio_get_page_dimensions(self, sample_pdf_bytes):
        import io

        from oxidize_pdf import PdfReader

        stream = io.BytesIO(sample_pdf_bytes)
        reader = PdfReader.from_stream(stream)
        page = reader.get_page(0)
        assert abs(page.width - 595.0) < 1.0  # A4

    def test_from_opened_binary_file(self, sample_pdf_bytes, tmp_dir):
        from oxidize_pdf import PdfReader

        path = tmp_dir / "stream.pdf"
        path.write_bytes(sample_pdf_bytes)

        with open(path, "rb") as fh:
            reader = PdfReader.from_stream(fh)
            assert reader.page_count == 2
            text = reader.extract_text_from_page(1)
            assert "Stream" in text or "page two" in text

    def test_from_stream_with_tolerant_options(self, sample_pdf_bytes):
        """ParseOptions kwarg plumbs through to the underlying reader."""
        import io

        from oxidize_pdf import ParseOptions, PdfReader

        stream = io.BytesIO(sample_pdf_bytes)
        reader = PdfReader.from_stream(stream, options=ParseOptions.tolerant())
        assert reader.page_count == 2

    def test_from_stream_honors_cursor_position(self, sample_pdf_bytes):
        """Reads from current cursor, not from 0 — idiomatic Python stream behaviour.

        A stream pre-seeked past the PDF header must fail parsing, proving we
        do NOT silently rewind.
        """
        import io

        from oxidize_pdf import PdfParseError, PdfReader

        stream = io.BytesIO(sample_pdf_bytes)
        stream.seek(10)
        with pytest.raises(PdfParseError):
            PdfReader.from_stream(stream)

    def test_from_stream_invalid_content(self):
        import io

        from oxidize_pdf import PdfParseError, PdfReader

        stream = io.BytesIO(b"not a valid pdf")
        with pytest.raises(PdfParseError):
            PdfReader.from_stream(stream)

    def test_from_stream_empty(self):
        import io

        from oxidize_pdf import PdfParseError, PdfReader

        stream = io.BytesIO(b"")
        with pytest.raises(PdfParseError):
            PdfReader.from_stream(stream)

    def test_from_stream_rejects_non_stream(self):
        """Passing an object without .read() must raise a clear Python error."""
        from oxidize_pdf import PdfReader

        with pytest.raises((TypeError, AttributeError)):
            PdfReader.from_stream("not a stream")  # type: ignore[arg-type]

    def test_from_stream_consumes_stream(self, sample_pdf_bytes):
        """After from_stream, the cursor is at end-of-stream (fully read)."""
        import io

        from oxidize_pdf import PdfReader

        stream = io.BytesIO(sample_pdf_bytes)
        PdfReader.from_stream(stream)
        assert stream.tell() == len(sample_pdf_bytes)


class TestTextChunking:
    """Test text chunking / positional text extraction (PARSE-010)."""

    @pytest.fixture
    def text_pdf_bytes(self):
        """Generate a PDF with text at known positions."""
        from oxidize_pdf import Document, Font, Page

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "First chunk")
        page.set_font(Font.COURIER, 18.0)
        page.text_at(200.0, 500.0, "Second chunk")
        doc.add_page(page)
        return doc.save_to_bytes()

    def test_extract_text_chunks_returns_list(self, text_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(text_pdf_bytes)
        chunks = reader.extract_text_chunks(0)
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_text_chunk_has_text(self, text_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(text_pdf_bytes)
        chunks = reader.extract_text_chunks(0)
        for chunk in chunks:
            assert isinstance(chunk.text, str)
            assert len(chunk.text) > 0

    def test_text_chunk_has_coordinates(self, text_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(text_pdf_bytes)
        chunks = reader.extract_text_chunks(0)
        for chunk in chunks:
            assert isinstance(chunk.x, float)
            assert isinstance(chunk.y, float)

    def test_text_chunk_has_font_size(self, text_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(text_pdf_bytes)
        chunks = reader.extract_text_chunks(0)
        for chunk in chunks:
            assert isinstance(chunk.font_size, float)
            assert chunk.font_size > 0

    def test_text_chunk_font_name_is_optional(self, text_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(text_pdf_bytes)
        chunks = reader.extract_text_chunks(0)
        for chunk in chunks:
            assert chunk.font_name is None or isinstance(chunk.font_name, str)

    def test_text_chunk_repr(self, text_pdf_bytes):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(text_pdf_bytes)
        chunks = reader.extract_text_chunks(0)
        assert len(chunks) > 0
        r = repr(chunks[0])
        assert "TextChunk" in r
