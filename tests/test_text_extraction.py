"""Tests for Tier 14 (F71-F74) — Text Extraction Deep module."""

import pytest
import oxidize_pdf as op


# ── Helpers ────────────────────────────────────────────────────────────────

def _create_sample_pdf() -> bytes:
    """Create a sample contract-like PDF with recognisable text."""
    doc = op.Document()
    page = op.Page.a4()
    page.set_font(op.Font.HELVETICA, 12.0)
    page.text_at(50.0, 750.0, "Contract #12345")
    page.text_at(50.0, 720.0, "Date: 2026-01-15")
    page.text_at(50.0, 700.0, "Party: Acme Corporation")
    page.text_at(50.0, 680.0, "Amount: $50,000.00")
    page.text_at(50.0, 660.0, "Location: New York, NY")
    doc.add_page(page)
    return doc.save_to_bytes()


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    return _create_sample_pdf()


@pytest.fixture
def sample_reader(sample_pdf_bytes) -> op.PdfReader:
    return op.PdfReader.from_bytes(sample_pdf_bytes)


# ── F71: ExtractionOptions ─────────────────────────────────────────────────

class TestExtractionOptions:
    def test_default_constructor(self):
        opts = op.ExtractionOptions()
        assert opts is not None

    def test_default_values(self):
        opts = op.ExtractionOptions()
        assert opts.preserve_layout is False
        assert opts.space_threshold == pytest.approx(0.3)
        assert opts.newline_threshold == pytest.approx(10.0)
        assert opts.sort_by_position is True
        assert opts.detect_columns is False
        assert opts.column_threshold == pytest.approx(50.0)
        assert opts.merge_hyphenated is True
        assert opts.track_space_decisions is False
        # New in oxidize-pdf 2.10.0
        assert opts.tj_space_threshold == pytest.approx(0.2)
        assert opts.reconstruct_paragraphs is False
        assert opts.include_artifacts is False

    def test_custom_values(self):
        opts = op.ExtractionOptions(
            preserve_layout=True,
            space_threshold=0.5,
            newline_threshold=15.0,
            sort_by_position=False,
            detect_columns=True,
            column_threshold=75.0,
            merge_hyphenated=False,
            track_space_decisions=True,
            tj_space_threshold=0.35,
            reconstruct_paragraphs=True,
            include_artifacts=True,
        )
        assert opts.preserve_layout is True
        assert opts.space_threshold == pytest.approx(0.5)
        assert opts.newline_threshold == pytest.approx(15.0)
        assert opts.sort_by_position is False
        assert opts.detect_columns is True
        assert opts.column_threshold == pytest.approx(75.0)
        assert opts.merge_hyphenated is False
        assert opts.track_space_decisions is True
        assert opts.tj_space_threshold == pytest.approx(0.35)
        assert opts.reconstruct_paragraphs is True
        assert opts.include_artifacts is True

    def test_repr(self):
        opts = op.ExtractionOptions()
        r = repr(opts)
        assert "ExtractionOptions" in r
        # New 2.10.0 fields surface in repr
        assert "tj_space_threshold" in r
        assert "reconstruct_paragraphs" in r
        assert "include_artifacts" in r


# ── F72: LineBreakMode ─────────────────────────────────────────────────────

class TestLineBreakMode:
    def test_auto_variant(self):
        mode = op.LineBreakMode.AUTO
        assert mode is not None
        assert "AUTO" in repr(mode)

    def test_preserve_all_variant(self):
        mode = op.LineBreakMode.PRESERVE_ALL
        assert mode is not None
        assert "PRESERVE_ALL" in repr(mode)

    def test_normalize_variant(self):
        mode = op.LineBreakMode.NORMALIZE
        assert mode is not None
        assert "NORMALIZE" in repr(mode)


# ── F72: PlainTextConfig ───────────────────────────────────────────────────

class TestPlainTextConfig:
    def test_default_constructor(self):
        cfg = op.PlainTextConfig()
        assert cfg is not None

    def test_default_getters(self):
        cfg = op.PlainTextConfig()
        assert cfg.space_threshold == pytest.approx(0.3)
        assert cfg.newline_threshold == pytest.approx(10.0)
        assert cfg.preserve_layout_flag is False
        # New in oxidize-pdf 2.10.0
        assert cfg.tj_space_threshold == pytest.approx(0.2)

    def test_dense_preset(self):
        cfg = op.PlainTextConfig.dense()
        assert cfg.space_threshold == pytest.approx(0.1)
        assert cfg.newline_threshold == pytest.approx(8.0)
        assert cfg.preserve_layout_flag is False
        # Locks the upstream 2.10.0 dense preset against silent drift
        assert cfg.tj_space_threshold == pytest.approx(0.1)

    def test_loose_preset(self):
        cfg = op.PlainTextConfig.loose()
        assert cfg.space_threshold == pytest.approx(0.4)
        assert cfg.newline_threshold == pytest.approx(15.0)
        # Locks the upstream 2.10.0 loose preset against silent drift
        assert cfg.tj_space_threshold == pytest.approx(0.25)

    def test_preserve_layout_preset(self):
        cfg = op.PlainTextConfig.preserve_layout()
        assert cfg.preserve_layout_flag is True
        assert "PRESERVE_ALL" in repr(cfg.line_break_mode)

    def test_custom_values(self):
        cfg = op.PlainTextConfig(
            space_threshold=0.2,
            newline_threshold=12.0,
            preserve_layout=True,
            tj_space_threshold=0.4,
        )
        assert cfg.space_threshold == pytest.approx(0.2)
        assert cfg.newline_threshold == pytest.approx(12.0)
        assert cfg.preserve_layout_flag is True
        assert cfg.tj_space_threshold == pytest.approx(0.4)

    def test_repr(self):
        cfg = op.PlainTextConfig()
        assert "PlainTextConfig" in repr(cfg)

    def test_line_break_mode_getter(self):
        cfg = op.PlainTextConfig()
        mode = cfg.line_break_mode
        assert "AUTO" in repr(mode)


# ── F72: PlainTextResult ───────────────────────────────────────────────────

class TestPlainTextResult:
    def test_extract_plain_text_returns_result(self, sample_reader):
        result = sample_reader.extract_plain_text(0)
        assert isinstance(result, op.PlainTextResult)

    def test_text_property(self, sample_reader):
        result = sample_reader.extract_plain_text(0)
        assert isinstance(result.text, str)

    def test_line_count_property(self, sample_reader):
        result = sample_reader.extract_plain_text(0)
        assert isinstance(result.line_count, int)
        assert result.line_count >= 0

    def test_char_count_property(self, sample_reader):
        result = sample_reader.extract_plain_text(0)
        assert isinstance(result.char_count, int)
        assert result.char_count >= 0

    def test_with_dense_config(self, sample_reader):
        cfg = op.PlainTextConfig.dense()
        result = sample_reader.extract_plain_text(0, cfg)
        assert isinstance(result, op.PlainTextResult)

    def test_repr(self, sample_reader):
        result = sample_reader.extract_plain_text(0)
        assert "PlainTextResult" in repr(result)


# ── F73: ColumnLayout ─────────────────────────────────────────────────────

class TestColumnLayout:
    def test_constructor(self):
        layout = op.ColumnLayout(2, 500.0, 10.0)
        assert layout is not None

    def test_column_count(self):
        layout = op.ColumnLayout(3, 450.0, 15.0)
        assert layout.column_count == 3

    def test_total_width(self):
        layout = op.ColumnLayout(2, 500.0, 10.0)
        assert layout.total_width == pytest.approx(500.0)

    def test_column_width_equal(self):
        layout = op.ColumnLayout(2, 500.0, 10.0)
        # Two columns with 10pt gap: each = (500 - 10) / 2 = 245
        w = layout.column_width(0)
        assert w is not None
        assert w == pytest.approx(245.0)

    def test_column_width_out_of_range(self):
        layout = op.ColumnLayout(2, 500.0, 10.0)
        assert layout.column_width(5) is None

    def test_with_custom_widths(self):
        layout = op.ColumnLayout.with_custom_widths([200.0, 300.0], 10.0)
        assert layout.column_count == 2
        assert layout.column_width(0) == pytest.approx(200.0)
        assert layout.column_width(1) == pytest.approx(300.0)

    def test_total_width_custom(self):
        layout = op.ColumnLayout.with_custom_widths([100.0, 200.0, 150.0], 5.0)
        # total = 100 + 200 + 150 + 2*5 = 460
        assert layout.total_width == pytest.approx(460.0)

    def test_repr(self):
        layout = op.ColumnLayout(2, 500.0, 10.0)
        assert "ColumnLayout" in repr(layout)


# ── F73: ColumnOptions ────────────────────────────────────────────────────

class TestColumnOptions:
    def test_default_constructor(self):
        opts = op.ColumnOptions()
        assert opts is not None

    def test_with_kwargs(self):
        opts = op.ColumnOptions(
            font_size=12.0,
            line_height=1.5,
            balance_columns=False,
            show_separators=True,
            separator_width=1.0,
        )
        assert opts is not None

    def test_repr(self):
        opts = op.ColumnOptions()
        assert "ColumnOptions" in repr(opts)


# ── F73: ColumnContent ────────────────────────────────────────────────────

class TestColumnContent:
    def test_constructor(self):
        content = op.ColumnContent("Hello, world!")
        assert content is not None

    def test_empty_string(self):
        content = op.ColumnContent("")
        assert content is not None

    def test_repr(self):
        content = op.ColumnContent("text")
        assert "ColumnContent" in repr(content)


# ── F74: MatchType ────────────────────────────────────────────────────────

class TestMatchType:
    def test_date_variant(self):
        mt = op.MatchType.DATE
        assert mt is not None
        assert "DATE" in repr(mt)

    def test_contract_number_variant(self):
        mt = op.MatchType.CONTRACT_NUMBER
        assert "CONTRACT_NUMBER" in repr(mt)

    def test_party_name_variant(self):
        mt = op.MatchType.PARTY_NAME
        assert "PARTY_NAME" in repr(mt)

    def test_monetary_amount_variant(self):
        mt = op.MatchType.MONETARY_AMOUNT
        assert "MONETARY_AMOUNT" in repr(mt)

    def test_location_variant(self):
        mt = op.MatchType.LOCATION
        assert "LOCATION" in repr(mt)

    def test_custom_variant(self):
        mt = op.MatchType.custom("my_type")
        assert mt is not None
        assert "my_type" in repr(mt)


# ── F74: TextValidator ────────────────────────────────────────────────────

CONTRACT_TEXT = (
    "Contract #12345 signed on 30 September 2026 by Acme Corporation "
    "for the amount of $50,000.00 in New York, NY."
)

DATE_TEXT = "The agreement dated 2026-01-15 is hereby effective."


class TestTextValidator:
    def test_constructor(self):
        v = op.TextValidator()
        assert v is not None

    def test_repr(self):
        v = op.TextValidator()
        assert "TextValidator" in repr(v)

    def test_search_for_target_found(self):
        v = op.TextValidator()
        result = v.search_for_target(DATE_TEXT, "2026-01-15")
        assert result.found is True
        assert len(result.matches) >= 1

    def test_search_for_target_not_found(self):
        v = op.TextValidator()
        result = v.search_for_target("some random text", "nonexistent phrase xyz")
        assert result.found is False
        assert result.matches == []
        assert result.confidence == pytest.approx(0.0)

    def test_search_for_target_case_insensitive(self):
        v = op.TextValidator()
        result = v.search_for_target("Hello World", "hello")
        assert result.found is True

    def test_validate_contract_text_with_dates(self):
        v = op.TextValidator()
        text = "This agreement is dated 30 September 2026 and expires 31/12/2030."
        result = v.validate_contract_text(text)
        assert result.found is True
        date_matches = [m for m in result.matches if repr(m.match_type) == "MatchType.DATE"]
        assert len(date_matches) > 0

    def test_validate_contract_text_with_amounts(self):
        v = op.TextValidator()
        result = v.validate_contract_text(CONTRACT_TEXT)
        assert result.found is True

    def test_validate_contract_text_no_matches(self):
        v = op.TextValidator()
        result = v.validate_contract_text("plain text without any special elements here")
        assert result.found is False
        assert result.confidence == pytest.approx(0.0)

    def test_extract_key_info_returns_dict(self):
        v = op.TextValidator()
        info = v.extract_key_info(CONTRACT_TEXT)
        assert isinstance(info, dict)

    def test_extract_key_info_has_dates(self):
        v = op.TextValidator()
        info = v.extract_key_info(CONTRACT_TEXT)
        assert "dates" in info
        assert len(info["dates"]) > 0

    def test_extract_key_info_has_amounts(self):
        v = op.TextValidator()
        info = v.extract_key_info(CONTRACT_TEXT)
        assert "monetary_amounts" in info
        assert len(info["monetary_amounts"]) > 0

    def test_extract_key_info_empty_text(self):
        v = op.TextValidator()
        info = v.extract_key_info("no matches here at all")
        assert isinstance(info, dict)


# ── F74: TextValidationResult ─────────────────────────────────────────────

class TestTextValidationResult:
    def test_found_property(self):
        v = op.TextValidator()
        result = v.search_for_target("hello world", "hello")
        assert isinstance(result.found, bool)

    def test_matches_property(self):
        v = op.TextValidator()
        result = v.search_for_target("hello world", "hello")
        assert isinstance(result.matches, list)

    def test_confidence_property(self):
        v = op.TextValidator()
        result = v.search_for_target("hello world", "hello")
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0

    def test_metadata_property(self):
        v = op.TextValidator()
        result = v.validate_contract_text("Signed on 01/01/2026")
        assert isinstance(result.metadata, dict)

    def test_repr(self):
        v = op.TextValidator()
        result = v.search_for_target("hello", "hello")
        assert "TextValidationResult" in repr(result)

    def test_text_match_properties(self):
        v = op.TextValidator()
        result = v.search_for_target("hello world", "hello")
        assert result.found
        match = result.matches[0]
        assert isinstance(match.text, str)
        assert isinstance(match.position, int)
        assert isinstance(match.length, int)
        assert isinstance(match.confidence, float)
        match_type = match.match_type
        assert match_type is not None


# ── PdfReader new methods ─────────────────────────────────────────────────

class TestPdfReaderTextExtraction:
    def test_extract_text_with_options_default(self, sample_reader):
        opts = op.ExtractionOptions()
        texts = sample_reader.extract_text_with_options(opts)
        assert isinstance(texts, list)
        assert len(texts) == 1
        assert isinstance(texts[0], str)

    def test_extract_text_with_options_preserve_layout(self, sample_reader):
        opts = op.ExtractionOptions(preserve_layout=True)
        texts = sample_reader.extract_text_with_options(opts)
        assert isinstance(texts, list)
        assert len(texts) >= 1

    def test_extract_plain_text_no_config(self, sample_reader):
        result = sample_reader.extract_plain_text(0)
        assert isinstance(result, op.PlainTextResult)
        assert isinstance(result.text, str)

    def test_extract_plain_text_with_config(self, sample_reader):
        cfg = op.PlainTextConfig.loose()
        result = sample_reader.extract_plain_text(0, cfg)
        assert isinstance(result, op.PlainTextResult)

    def test_extract_plain_text_lines_no_config(self, sample_reader):
        lines = sample_reader.extract_plain_text_lines(0)
        assert isinstance(lines, list)
        for line in lines:
            assert isinstance(line, str)

    def test_extract_plain_text_lines_with_config(self, sample_reader):
        cfg = op.PlainTextConfig.dense()
        lines = sample_reader.extract_plain_text_lines(0, cfg)
        assert isinstance(lines, list)

    def test_extract_plain_text_char_count_consistent(self, sample_reader):
        result = sample_reader.extract_plain_text(0)
        assert result.char_count == len(result.text)


# ── F71 (2.10.0): TextFragment + extract_fragments_* ──────────────────────

class TestTextFragmentExtraction:
    """Positional fragment extraction wired in oxidize-python 0.6.0 to
    surface oxidize-pdf 2.10.0's TextFragment.mcid / struct_tag.

    The sample PDF emits five single-line `Tj` operators at known
    coordinates via `Page.text_at`, so we can assert exact contents and
    positions rather than relying on counts only.
    """

    def test_extract_fragments_with_options_returns_per_page_lists(
        self, sample_reader
    ):
        opts = op.ExtractionOptions(preserve_layout=True)
        pages = sample_reader.extract_fragments_with_options(opts)
        assert isinstance(pages, list)
        assert len(pages) == 1
        assert isinstance(pages[0], list)
        # Five text_at() calls in _create_sample_pdf
        assert len(pages[0]) >= 5

    def test_extract_fragments_from_page_sorted_by_y_descending(self, sample_reader):
        """Fragments come back sorted top-to-bottom (Y descending in PDF space).

        The sample PDF places its five `text_at` lines at exactly
        y = 750, 720, 700, 680, 660. With default `sort_by_position = True`,
        the extractor must surface them in that exact order: first fragment
        anchored near y=750, last near y=660, and every step monotonically
        non-increasing. A regression that broke `sort_by_position`, swapped
        Y semantics, or dropped fragments would fail this test.
        """
        opts = op.ExtractionOptions(preserve_layout=True)
        fragments = sample_reader.extract_fragments_from_page(0, opts)
        assert len(fragments) >= 5
        ys = [f.y for f in fragments]
        assert ys[0] == pytest.approx(750.0, abs=1.0)
        assert ys[-1] == pytest.approx(660.0, abs=1.0)
        for prev, nxt in zip(ys, ys[1:]):
            assert prev >= nxt, f"Y not monotonically non-increasing: {prev} -> {nxt}"

    def test_fragment_exposes_position_and_font_metadata(self, sample_reader):
        opts = op.ExtractionOptions(preserve_layout=True)
        fragments = sample_reader.extract_fragments_from_page(0, opts)
        contract_frag = next(
            f for f in fragments if "Contract #12345" in f.text
        )
        # text_at(50.0, 750.0, "Contract #12345") with Helvetica 12pt
        assert contract_frag.x == pytest.approx(50.0, abs=0.5)
        assert contract_frag.y == pytest.approx(750.0, abs=0.5)
        assert contract_frag.font_size == pytest.approx(12.0)
        assert contract_frag.width > 0.0
        assert contract_frag.height > 0.0
        # Helvetica is not bold/italic
        assert contract_frag.is_bold is False
        assert contract_frag.is_italic is False
        assert isinstance(contract_frag.font_name, (str, type(None)))

    def test_fragment_mcid_and_struct_tag_none_for_untagged_pdf(
        self, sample_reader
    ):
        """Untagged PDFs (no BDC/EMC structure) leave mcid/struct_tag empty.

        The 2.10.0 contract is: mcid and struct_tag are populated only when
        the content stream wraps text in `/MCID … BDC … EMC`. The sample
        PDF emits plain Tj operators, so both fields must be None.
        """
        opts = op.ExtractionOptions(preserve_layout=True)
        fragments = sample_reader.extract_fragments_from_page(0, opts)
        for fragment in fragments:
            assert fragment.mcid is None
            assert fragment.struct_tag is None

    def test_fragment_repr_includes_text_and_position(self, sample_reader):
        opts = op.ExtractionOptions(preserve_layout=True)
        fragments = sample_reader.extract_fragments_from_page(0, opts)
        rendered = repr(fragments[0])
        assert "TextFragment" in rendered
        assert "x=" in rendered
        assert "y=" in rendered
        assert "mcid=" in rendered
        assert "struct_tag=" in rendered

    def test_extract_fragments_without_preserve_layout_yields_empty(
        self, sample_reader
    ):
        """Without preserve_layout, upstream returns no fragments — only
        the concatenated `text` field. This bridge exposes that contract
        verbatim instead of synthesising fragments.
        """
        opts = op.ExtractionOptions(preserve_layout=False)
        fragments = sample_reader.extract_fragments_from_page(0, opts)
        assert fragments == []

    def test_extract_fragments_from_invalid_page_raises(self, sample_reader):
        opts = op.ExtractionOptions(preserve_layout=True)
        # parse_err_to_py wildcard maps to PdfParseError; ensure the bridge
        # surfaces a typed PDF exception, not a stray generic Exception
        # (which would silently mask a panic or a type-system regression).
        with pytest.raises(op.PdfParseError):
            sample_reader.extract_fragments_from_page(99, opts)

    def test_fragment_eq_is_structural(self, sample_reader):
        """``__eq__`` compares content + position + font + tagging.

        Two independent extractions of the same fixture must produce
        pair-wise equal fragments. A different fragment from the same
        page must compare unequal.
        """
        opts = op.ExtractionOptions(preserve_layout=True)
        first = sample_reader.extract_fragments_from_page(0, opts)
        # Re-open the same bytes to force a fresh extraction with no
        # object identity overlap.
        second_reader = op.PdfReader.from_bytes(_create_sample_pdf())
        second = second_reader.extract_fragments_from_page(0, opts)
        assert len(first) == len(second)
        for a, b in zip(first, second):
            assert a == b
        # Distinct fragments from the same page differ on at least one
        # identity field (here: text + y position).
        assert first[0] != first[-1]

    def test_space_decisions_returns_list_with_or_without_flag(self, sample_reader):
        """``TextFragment.space_decisions`` is always a list, never None.

        oxidize-pdf 2.10.0 declares the ``track_space_decisions`` flag
        and the ``SpaceDecision`` type, but no extractor path currently
        pushes onto the vector — it is empty in both modes. This test
        locks the observable contract of the binding (always a list,
        possibly empty) and intentionally asserts the no-producer
        invariant so that when upstream wires the producer this test
        will fail loudly, signalling that it must be replaced by one
        demanding non-empty output under ``track_space_decisions=True``.
        """
        for flag in (False, True):
            opts = op.ExtractionOptions(
                preserve_layout=True,
                track_space_decisions=flag,
            )
            fragments = sample_reader.extract_fragments_from_page(0, opts)
            for fragment in fragments:
                # Must be a list, not None, regardless of the flag.
                assert isinstance(fragment.space_decisions, list)
                # Each call returns an independent list, not a shared
                # reference to the same Vec on the Rust side.
                assert fragment.space_decisions is not fragment.space_decisions
            # Upstream 2.10.0 ships no producer; both modes yield empty.
            assert all(
                f.space_decisions == [] for f in fragments
            ), (
                "All fragments expected to carry empty space_decisions in "
                f"upstream 2.10.0 (flag={flag}). If this test fails, "
                "upstream now emits SpaceDecisions and this test should be "
                "replaced by one asserting the SpaceDecision contract."
            )

    def test_fragment_color_reflects_set_fill_color(self):
        """``TextFragment.color`` round-trips through the graphics state.

        Reproduces the upstream issue #57 fix flow: pre-existing fill
        colour from a graphics op (rectangle fill) is overridden by a
        second ``set_fill_color`` call before ``text_at``. The producer
        emits ``rg`` for both colours; the extractor must surface the
        second one — the text colour — on the resulting fragment.

        Just calling ``set_fill_color`` + ``text_at`` is not sufficient
        because the writer suppresses the implied ``rg`` when no
        intervening graphics op forces a flush; the intervening fill
        below mirrors the issue #57 reproducer exactly.
        """
        doc = op.Document()
        page = op.Page.a4()
        # First fill: opaque magenta band (graphics-state preamble).
        page.set_fill_color(op.Color.rgb(0.851, 0.275, 0.937))
        page.draw_rect(0.0, 600.0, 595.0, 200.0)
        page.fill()
        # Switch to pure red and write text on top.
        page.set_fill_color(op.Color.rgb(1.0, 0.0, 0.0))
        page.set_font(op.Font.HELVETICA_BOLD, 14.0)
        page.text_at(80.0, 700.0, "Red marker")
        doc.add_page(page)

        reader = op.PdfReader.from_bytes(doc.save_to_bytes())
        opts = op.ExtractionOptions(preserve_layout=True)
        fragments = reader.extract_fragments_from_page(0, opts)
        marker = next(f for f in fragments if "Red marker" in f.text)

        assert marker.color is not None, (
            "Expected fragment.color to surface the graphics-state fill "
            "colour set via Page.set_fill_color; got None instead."
        )
        # The text was written after a switch to red; the extractor must
        # carry that red onto the fragment, not the prior magenta.
        assert marker.color.r == pytest.approx(1.0, abs=1e-6)
        assert marker.color.g == pytest.approx(0.0, abs=1e-6)
        assert marker.color.b == pytest.approx(0.0, abs=1e-6)
