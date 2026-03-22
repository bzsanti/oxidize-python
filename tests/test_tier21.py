"""Tests for Tier 21 — Deepen Existing Wrappers (F84, F85, F86)."""

import pytest
from oxidize_pdf import (
    DashboardBuilder,
    DashboardTheme,
    Document,
    Font,
    KpiCard,
    Page,
    PdfAConformance,
    PdfALevel,
    PdfAValidationResult,
    PdfAValidator,
    Placeholder,
    TemplateAnalysis,
    TemplateContext,
    TemplateParser,
    TemplateRenderer,
    TrendDirection,
)


# ── F84: Templates Deep ─────────────────────────────────────────────────


class TestTemplateContextDeep:
    def test_set_number(self):
        ctx = TemplateContext()
        ctx.set_number("price", 19.99)
        result = TemplateRenderer().render("Price: {{price}}", ctx)
        assert "19.99" in result

    def test_set_integer(self):
        ctx = TemplateContext()
        ctx.set_integer("count", 42)
        result = TemplateRenderer().render("Count: {{count}}", ctx)
        assert "42" in result

    def test_set_boolean(self):
        ctx = TemplateContext()
        ctx.set_boolean("active", True)
        result = TemplateRenderer().render("Active: {{active}}", ctx)
        assert "true" in result

    def test_has(self):
        ctx = TemplateContext()
        ctx.set("name", "World")
        assert ctx.has("name") is True
        assert ctx.has("missing") is False

    def test_keys(self):
        ctx = TemplateContext()
        ctx.set("a", "1")
        ctx.set("b", "2")
        keys = ctx.keys()
        assert "a" in keys
        assert "b" in keys

    def test_clear(self):
        ctx = TemplateContext()
        ctx.set("x", "y")
        assert ctx.has("x") is True
        ctx.clear()
        assert ctx.has("x") is False

    def test_repr(self):
        ctx = TemplateContext()
        ctx.set("x", "y")
        assert "TemplateContext" in repr(ctx)


class TestTemplateRendererDeep:
    def test_get_required_variables(self):
        renderer = TemplateRenderer()
        vars = renderer.get_required_variables("Hello {{name}} at {{date}}")
        assert "name" in vars
        assert "date" in vars

    def test_validate_template_ok(self):
        TemplateRenderer().validate_template("Hello {{name}}")

    def test_validate_template_invalid_raises(self):
        with pytest.raises(ValueError):
            TemplateRenderer().validate_template("Hello {{}")

    def test_has_placeholders_true(self):
        assert TemplateRenderer().has_placeholders("{{x}}") is True

    def test_has_placeholders_false(self):
        assert TemplateRenderer().has_placeholders("no placeholders") is False

    def test_analyze_template(self):
        analysis = TemplateRenderer().analyze_template("{{a}} {{b}} {{a}}")
        assert isinstance(analysis, TemplateAnalysis)
        assert analysis.total_placeholders == 3
        assert analysis.unique_variables == 2
        assert "a" in analysis.variable_names
        assert "b" in analysis.variable_names

    def test_repr(self):
        assert "TemplateRenderer" in repr(TemplateRenderer())


class TestTemplateParser:
    def test_parse(self):
        parser = TemplateParser()
        placeholders = parser.parse("Hello {{name}} at {{date}}")
        assert len(placeholders) == 2
        assert isinstance(placeholders[0], Placeholder)
        assert placeholders[0].variable_name == "name"
        assert placeholders[1].variable_name == "date"

    def test_placeholder_positions(self):
        parser = TemplateParser()
        placeholders = parser.parse("A {{x}} B")
        assert placeholders[0].start == 2
        assert placeholders[0].full_text == "{{x}}"

    def test_count_placeholders(self):
        assert TemplateParser().count_placeholders("{{a}} {{b}} {{c}}") == 3

    def test_get_variable_names(self):
        names = TemplateParser().get_variable_names("{{a}} {{b}} {{a}}")
        assert sorted(names) == ["a", "b"]

    def test_has_placeholders(self):
        assert TemplateParser().has_placeholders("{{x}}") is True
        assert TemplateParser().has_placeholders("plain") is False

    def test_repr(self):
        assert "TemplateParser" in repr(TemplateParser())


class TestTemplateAnalysis:
    def test_fields(self):
        a = TemplateRenderer().analyze_template("{{x}} {{y}}")
        assert a.total_placeholders == 2
        assert a.unique_variables == 2
        assert len(a.variable_names) == 2
        assert len(a.placeholders) == 2

    def test_repr(self):
        a = TemplateRenderer().analyze_template("{{x}}")
        assert "TemplateAnalysis" in repr(a)


class TestPlaceholder:
    def test_fields(self):
        p = TemplateParser().parse("{{name}}")[0]
        assert p.variable_name == "name"
        assert p.full_text == "{{name}}"
        assert p.start == 0
        assert p.end > 0

    def test_repr(self):
        p = TemplateParser().parse("{{x}}")[0]
        assert "Placeholder" in repr(p)


# ── F85: PdfA Validation Deep ────────────────────────────────────────────


class TestPdfALevelDeep:
    def test_all_8_variants(self):
        assert PdfALevel.A1A is not None
        assert PdfALevel.A1B is not None
        assert PdfALevel.A2A is not None
        assert PdfALevel.A2B is not None
        assert PdfALevel.A2U is not None
        assert PdfALevel.A3A is not None
        assert PdfALevel.A3B is not None
        assert PdfALevel.A3U is not None

    def test_repr_shows_level(self):
        r = repr(PdfALevel.A1B)
        assert "PdfALevel" in r
        assert "A1" in r or "1" in r


class TestPdfAConformance:
    def test_variants(self):
        assert PdfAConformance.A is not None
        assert PdfAConformance.B is not None
        assert PdfAConformance.U is not None

    def test_repr(self):
        assert "PdfAConformance" in repr(PdfAConformance.A)


class TestPdfAValidationResult:
    def test_validate_bytes(self):
        doc = Document()
        page = Page(612.0, 792.0)
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "PDF/A test")
        doc.add_page(page)
        data = doc.save_to_bytes()

        validator = PdfAValidator(PdfALevel.A1B)
        result = validator.validate_bytes(data)
        assert isinstance(result, PdfAValidationResult)
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.error_count, int)
        assert isinstance(result.warning_count, int)

    def test_errors_are_strings(self):
        doc = Document()
        doc.add_page(Page(612.0, 792.0))
        data = doc.save_to_bytes()

        result = PdfAValidator(PdfALevel.A1B).validate_bytes(data)
        for err in result.errors:
            assert isinstance(err, str)

    def test_repr(self):
        doc = Document()
        doc.add_page(Page(612.0, 792.0))
        data = doc.save_to_bytes()

        result = PdfAValidator(PdfALevel.A1B).validate_bytes(data)
        assert "PdfAValidationResult" in repr(result)


class TestPdfAValidatorDeep:
    def test_collect_all_errors(self):
        v = PdfAValidator(PdfALevel.A1B).collect_all_errors(True)
        assert isinstance(v, PdfAValidator)

    def test_level_getter(self):
        v = PdfAValidator(PdfALevel.A2B)
        assert v.level is not None

    def test_repr_shows_level(self):
        assert "PdfAValidator" in repr(PdfAValidator(PdfALevel.A3B))


# ── F86: Dashboard Deep ──────────────────────────────────────────────────


class TestTrendDirection:
    def test_variants(self):
        assert TrendDirection.UP is not None
        assert TrendDirection.DOWN is not None
        assert TrendDirection.FLAT is not None

    def test_repr(self):
        assert "TrendDirection" in repr(TrendDirection.UP)


class TestKpiCardDeep:
    def test_with_trend(self):
        card = KpiCard("Revenue", "$1.2M").with_trend(12.5, TrendDirection.UP)
        assert isinstance(card, KpiCard)

    def test_with_subtitle(self):
        card = KpiCard("Revenue", "$1.2M").with_subtitle("vs Q3")
        assert isinstance(card, KpiCard)

    def test_with_sparkline(self):
        card = KpiCard("Revenue", "$1.2M").with_sparkline([100.0, 120.0, 115.0, 130.0])
        assert isinstance(card, KpiCard)

    def test_with_icon(self):
        card = KpiCard("Revenue", "$1.2M").with_icon("chart")
        assert isinstance(card, KpiCard)

    def test_repr(self):
        assert "KpiCard" in repr(KpiCard("Revenue", "$1.2M"))


class TestDashboardThemeDeep:
    def test_dark_theme(self):
        theme = DashboardTheme.dark()
        assert isinstance(theme, DashboardTheme)

    def test_colorful_theme(self):
        theme = DashboardTheme.colorful()
        assert isinstance(theme, DashboardTheme)

    def test_repr(self):
        assert "DashboardTheme" in repr(DashboardTheme.corporate())


class TestDashboardBuilderDeep:
    def test_title(self):
        builder = DashboardBuilder().title("Sales Q4")
        assert isinstance(builder, DashboardBuilder)

    def test_subtitle(self):
        builder = DashboardBuilder().title("T").subtitle("Sub")
        assert isinstance(builder, DashboardBuilder)

    def test_theme(self):
        builder = DashboardBuilder().title("T").theme(DashboardTheme.dark())
        assert isinstance(builder, DashboardBuilder)

    def test_add_kpi_row(self):
        cards = [KpiCard("Revenue", "$1M"), KpiCard("Orders", "500")]
        builder = DashboardBuilder().title("T").add_kpi_row(cards)
        assert isinstance(builder, DashboardBuilder)

    def test_author(self):
        builder = DashboardBuilder().title("T").author("Santiago")
        assert isinstance(builder, DashboardBuilder)

    def test_build_to_page(self):
        page = Page(612.0, 792.0)
        DashboardBuilder().title("Test Dashboard").add_kpi_row(
            [KpiCard("Revenue", "$1M")]
        ).build_to_page(page)
        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_repr(self):
        assert "DashboardBuilder" in repr(DashboardBuilder())


# ── Quality: R3 — DashboardBuilder state getters ────────────────────────


class TestDashboardBuilderGetters:
    def test_get_title_none_by_default(self):
        assert DashboardBuilder().get_title is None

    def test_get_title_after_set(self):
        b = DashboardBuilder().title("Revenue Report")
        assert b.get_title == "Revenue Report"

    def test_get_subtitle_after_set(self):
        b = DashboardBuilder().subtitle("Q1 2026")
        assert b.get_subtitle == "Q1 2026"

    def test_get_author_after_set(self):
        b = DashboardBuilder().author("Santiago")
        assert b.get_author == "Santiago"

    def test_kpi_row_count_zero(self):
        assert DashboardBuilder().kpi_row_count == 0

    def test_kpi_row_count_after_add(self):
        b = DashboardBuilder().add_kpi_row([KpiCard("Rev", "$1M")])
        assert b.kpi_row_count == 1


# ── Quality: O1 — DashboardBuilder multi-row accumulation ───────────────


class TestDashboardBuilderMultiRow:
    def test_multiple_kpi_rows_accumulate(self):
        b = (
            DashboardBuilder()
            .add_kpi_row([KpiCard("A", "1")])
            .add_kpi_row([KpiCard("B", "2")])
            .add_kpi_row([KpiCard("C", "3")])
        )
        assert b.kpi_row_count == 3


# ── Quality: R1 — Enum eq/hash in tier8 ─────────────────────────────────


class TestTier8EnumEqHash:
    def test_pdf_a_level_eq(self):
        assert PdfALevel.A1B == PdfALevel.A1B
        assert PdfALevel.A1B != PdfALevel.A2B

    def test_pdf_a_level_hashable(self):
        s = {PdfALevel.A1A, PdfALevel.A1B, PdfALevel.A1A}
        assert len(s) == 2

    def test_pdf_a_conformance_eq(self):
        assert PdfAConformance.A == PdfAConformance.A
        assert PdfAConformance.A != PdfAConformance.B

    def test_pdf_a_conformance_hashable(self):
        s = {PdfAConformance.A, PdfAConformance.B, PdfAConformance.U}
        assert len(s) == 3

    def test_trend_direction_eq(self):
        assert TrendDirection.UP == TrendDirection.UP
        assert TrendDirection.UP != TrendDirection.DOWN

    def test_trend_direction_hashable(self):
        d = {TrendDirection.UP: "up", TrendDirection.DOWN: "down"}
        assert d[TrendDirection.UP] == "up"


# ── Quality: R8 — Improved __repr__ ─────────────────────────────────────


class TestImprovedRepr:
    def test_template_renderer_repr(self):
        assert repr(TemplateRenderer()) == "TemplateRenderer()"

    def test_template_parser_repr(self):
        assert repr(TemplateParser()) == "TemplateParser()"

    def test_template_context_repr_with_keys(self):
        ctx = TemplateContext()
        ctx.set("name", "World")
        ctx.set("age", "30")
        r = repr(ctx)
        assert "keys=2" in r
        assert "name" in r
        assert "age" in r

    def test_template_context_repr_empty(self):
        r = repr(TemplateContext())
        assert "keys=0" in r


# ── Quality: R9 — PdfAConformance docstring ──────────────────────────────


class TestPdfAConformanceDocstring:
    def test_has_docstring(self):
        assert PdfAConformance.__doc__ is not None
        assert "conformance" in PdfAConformance.__doc__.lower()


# ── Quality: O5 — has_placeholders cross-check ──────────────────────────


class TestPlaceholdersCrossCheck:
    def test_agree_with_placeholders(self):
        templates = [
            "Hello {{name}}!",
            "No placeholders here",
            "{{a}} and {{b}}",
            "",
        ]
        renderer = TemplateRenderer()
        parser = TemplateParser()
        for t in templates:
            assert renderer.has_placeholders(t) == parser.has_placeholders(t), (
                f"Disagreement on: {t!r}"
            )
