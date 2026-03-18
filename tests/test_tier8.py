"""Tests for Tier 8 — Enterprise / Advanced (Features 30-41)."""

import pytest


# ── Feature 30: Tagged PDF ─────────────────────────────────────────────────


class TestStandardStructureType:
    def test_key_variants(self):
        from oxidize_pdf import StandardStructureType as SST

        assert SST.DOCUMENT is not None
        assert SST.P is not None
        assert SST.H1 is not None
        assert SST.H2 is not None
        assert SST.TABLE is not None
        assert SST.TR is not None
        assert SST.TD is not None
        assert SST.FIGURE is not None
        assert SST.SPAN is not None
        assert SST.LINK is not None
        assert SST.DIV is not None
        assert SST.SECT is not None


class TestStructureElement:
    def test_create_standard(self):
        from oxidize_pdf import StandardStructureType, StructureElement

        el = StructureElement(StandardStructureType.P)
        assert isinstance(el, StructureElement)

    def test_create_custom(self):
        from oxidize_pdf import StructureElement

        el = StructureElement.custom("MyWidget")
        assert isinstance(el, StructureElement)

    def test_builder(self):
        from oxidize_pdf import StandardStructureType, StructureElement

        el = (
            StructureElement(StandardStructureType.P)
            .with_language("en")
            .with_alt_text("A paragraph")
        )
        assert isinstance(el, StructureElement)

    def test_add_mcid(self):
        from oxidize_pdf import StandardStructureType, StructureElement

        el = StructureElement(StandardStructureType.P)
        el.add_mcid(0, 1)


class TestStructTree:
    def test_create_and_set_root(self):
        from oxidize_pdf import StandardStructureType, StructTree, StructureElement

        tree = StructTree()
        root = StructureElement(StandardStructureType.DOCUMENT)
        idx = tree.set_root(root)
        assert isinstance(idx, int)

    def test_add_child(self):
        from oxidize_pdf import StandardStructureType, StructTree, StructureElement

        tree = StructTree()
        root_idx = tree.set_root(StructureElement(StandardStructureType.DOCUMENT))
        child_idx = tree.add_child(root_idx, StructureElement(StandardStructureType.P))
        assert child_idx > root_idx

    def test_length(self):
        from oxidize_pdf import StandardStructureType, StructTree, StructureElement

        tree = StructTree()
        tree.set_root(StructureElement(StandardStructureType.DOCUMENT))
        assert tree.length == 1

    def test_document_set_struct_tree(self):
        from oxidize_pdf import (
            Document, Font, Page, StandardStructureType, StructTree, StructureElement,
        )

        tree = StructTree()
        root_idx = tree.set_root(StructureElement(StandardStructureType.DOCUMENT))
        tree.add_child(root_idx, StructureElement(StandardStructureType.H1).with_language("en"))
        tree.add_child(root_idx, StructureElement(StandardStructureType.P))

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Tagged content")
        doc.add_page(page)
        doc.set_struct_tree(tree)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


# ── Feature 31: Coordinate Systems ────────────────────────────────────────


class TestCoordinateSystem:
    def test_variants(self):
        from oxidize_pdf import CoordinateSystem

        assert CoordinateSystem.PDF_STANDARD is not None
        assert CoordinateSystem.SCREEN_SPACE is not None

    def test_set_coordinate_system(self):
        from oxidize_pdf import CoordinateSystem, Document, Font, Page

        page = Page.a4()
        page.set_coordinate_system(CoordinateSystem.SCREEN_SPACE)
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 50.0, "Top-left origin")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


# ── Feature 32: Calibrated Colors ─────────────────────────────────────────


class TestLabColor:
    def test_lab_color_space(self):
        from oxidize_pdf import LabColorSpace

        lab = LabColorSpace.d50()
        assert isinstance(lab, LabColorSpace)

    def test_lab_color_space_d65(self):
        from oxidize_pdf import LabColorSpace

        lab = LabColorSpace.d65()
        assert isinstance(lab, LabColorSpace)


# ── Feature 33: Templates ─────────────────────────────────────────────────


class TestTemplates:
    def test_template_context(self):
        from oxidize_pdf import TemplateContext

        ctx = TemplateContext()
        ctx.set("name", "World")
        assert isinstance(ctx, TemplateContext)

    def test_template_renderer(self):
        from oxidize_pdf import TemplateContext, TemplateRenderer

        ctx = TemplateContext()
        ctx.set("name", "World")
        renderer = TemplateRenderer()
        result = renderer.render("Hello {{name}}", ctx)
        assert "World" in result


# ── Feature 34: OCR ───────────────────────────────────────────────────────


class TestOcr:
    def test_mock_ocr_provider(self):
        from oxidize_pdf import MockOcrProvider

        p = MockOcrProvider()
        assert isinstance(p, MockOcrProvider)

    def test_ocr_engine_variants(self):
        from oxidize_pdf import OcrEngine

        assert OcrEngine.TESSERACT is not None
        assert OcrEngine.MOCK is not None


# ── Feature 35: Batch Processing ──────────────────────────────────────────


class TestBatchProcessing:
    def test_batch_options(self):
        from oxidize_pdf import BatchOptions

        opts = BatchOptions()
        assert isinstance(opts, BatchOptions)

    def test_batch_options_custom(self):
        from oxidize_pdf import BatchOptions

        opts = BatchOptions(parallelism=2, stop_on_error=True)
        assert isinstance(opts, BatchOptions)


# ── Feature 36: Streaming/Lazy ────────────────────────────────────────────


class TestStreaming:
    def test_streaming_options(self):
        from oxidize_pdf import StreamingOptions

        opts = StreamingOptions.minimal_memory()
        assert isinstance(opts, StreamingOptions)

    def test_lazy_document(self, tmp_dir):
        from oxidize_pdf import Document, Font, LazyDocument, Page

        path = tmp_dir / "lazy_test.pdf"
        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Lazy load")
        doc.add_page(page)
        doc.add_page(Page.a4())
        doc.save(str(path))

        lazy = LazyDocument.open(str(path))
        assert isinstance(lazy.page_count, int)


# ── Feature 37: PDF Recovery ──────────────────────────────────────────────


class TestPdfRecovery:
    def test_validate_pdf(self, tmp_dir):
        from oxidize_pdf import Document, Font, Page, validate_pdf

        path = tmp_dir / "valid.pdf"
        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Valid")
        doc.add_page(page)
        doc.save(str(path))

        result = validate_pdf(str(path))
        assert isinstance(result, dict)


# ── Feature 38: PDF/A Validation ──────────────────────────────────────────


class TestPdfAValidation:
    def test_pdfa_level_variants(self):
        from oxidize_pdf import PdfALevel

        assert PdfALevel.A1B is not None
        assert PdfALevel.A2B is not None
        assert PdfALevel.A3B is not None

    def test_pdfa_validator(self):
        from oxidize_pdf import PdfALevel, PdfAValidator

        v = PdfAValidator(PdfALevel.A1B)
        assert isinstance(v, PdfAValidator)


# ── Feature 39: PDF Comparison ────────────────────────────────────────────


class TestPdfComparison:
    def test_compare_identical(self):
        from oxidize_pdf import Document, Font, Page, compare_pdfs

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Same content")
        doc.add_page(page)
        data = doc.save_to_bytes()

        result = compare_pdfs(data, data)
        assert isinstance(result, dict)
        assert result["structurally_equivalent"] is True


# ── Feature 40: Semantic Marking ──────────────────────────────────────────


class TestSemanticMarking:
    def test_entity_type_variants(self):
        from oxidize_pdf import EntityType

        # Verify at least some common entity types exist
        assert EntityType is not None


# ── Feature 41: Dashboards/Charts ─────────────────────────────────────────


class TestDashboard:
    def test_dashboard_builder(self):
        from oxidize_pdf import DashboardBuilder

        builder = DashboardBuilder()
        assert isinstance(builder, DashboardBuilder)

    def test_dashboard_theme(self):
        from oxidize_pdf import DashboardTheme

        theme = DashboardTheme.corporate()
        assert isinstance(theme, DashboardTheme)

    def test_kpi_card(self):
        from oxidize_pdf import KpiCard

        card = KpiCard("Revenue", "$1.2M")
        assert isinstance(card, KpiCard)
