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
