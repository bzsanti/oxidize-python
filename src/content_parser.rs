use pyo3::prelude::*;

use oxidize_pdf::parser::content::{ContentOperation, ContentParser, TextElement};
use oxidize_pdf::parser::xref::{XRefEntry, XRefTable};

// ── PyContentOperation ─────────────────────────────────────────────────────

/// A single PDF content stream operation (tagged union).
///
/// Use ``op_type`` to identify the operation, then access typed data via
/// ``operands``, ``name``, ``font_name``, ``font_size``, ``text_bytes``,
/// or ``text_array_elements`` depending on the operation type.
#[pyclass(name = "ContentOperation", frozen, from_py_object, eq)]
#[derive(Clone, PartialEq)]
pub struct PyContentOperation {
    pub inner: ContentOperation,
}

#[pymethods]
impl PyContentOperation {
    #[getter]
    fn op_type(&self) -> &str {
        match &self.inner {
            ContentOperation::BeginText => "BeginText",
            ContentOperation::EndText => "EndText",
            ContentOperation::SetCharSpacing(_) => "SetCharSpacing",
            ContentOperation::SetWordSpacing(_) => "SetWordSpacing",
            ContentOperation::SetHorizontalScaling(_) => "SetHorizontalScaling",
            ContentOperation::SetLeading(_) => "SetLeading",
            ContentOperation::SetFont(_, _) => "SetFont",
            ContentOperation::SetTextRenderMode(_) => "SetTextRenderMode",
            ContentOperation::SetTextRise(_) => "SetTextRise",
            ContentOperation::MoveText(_, _) => "MoveText",
            ContentOperation::MoveTextSetLeading(_, _) => "MoveTextSetLeading",
            ContentOperation::SetTextMatrix(_, _, _, _, _, _) => "SetTextMatrix",
            ContentOperation::NextLine => "NextLine",
            ContentOperation::ShowText(_) => "ShowText",
            ContentOperation::ShowTextArray(_) => "ShowTextArray",
            ContentOperation::NextLineShowText(_) => "NextLineShowText",
            ContentOperation::SetSpacingNextLineShowText(_, _, _) => "SetSpacingNextLineShowText",
            ContentOperation::SaveGraphicsState => "SaveGraphicsState",
            ContentOperation::RestoreGraphicsState => "RestoreGraphicsState",
            ContentOperation::SetTransformMatrix(_, _, _, _, _, _) => "SetTransformMatrix",
            ContentOperation::SetLineWidth(_) => "SetLineWidth",
            ContentOperation::SetLineCap(_) => "SetLineCap",
            ContentOperation::SetLineJoin(_) => "SetLineJoin",
            ContentOperation::SetMiterLimit(_) => "SetMiterLimit",
            ContentOperation::SetDashPattern(_, _) => "SetDashPattern",
            ContentOperation::SetIntent(_) => "SetIntent",
            ContentOperation::SetFlatness(_) => "SetFlatness",
            ContentOperation::SetGraphicsStateParams(_) => "SetGraphicsStateParams",
            ContentOperation::MoveTo(_, _) => "MoveTo",
            ContentOperation::LineTo(_, _) => "LineTo",
            ContentOperation::CurveTo(_, _, _, _, _, _) => "CurveTo",
            ContentOperation::CurveToV(_, _, _, _) => "CurveToV",
            ContentOperation::CurveToY(_, _, _, _) => "CurveToY",
            ContentOperation::ClosePath => "ClosePath",
            ContentOperation::Rectangle(_, _, _, _) => "Rectangle",
            ContentOperation::Stroke => "Stroke",
            ContentOperation::CloseStroke => "CloseStroke",
            ContentOperation::Fill => "Fill",
            ContentOperation::FillEvenOdd => "FillEvenOdd",
            ContentOperation::FillStroke => "FillStroke",
            ContentOperation::FillStrokeEvenOdd => "FillStrokeEvenOdd",
            ContentOperation::CloseFillStroke => "CloseFillStroke",
            ContentOperation::CloseFillStrokeEvenOdd => "CloseFillStrokeEvenOdd",
            ContentOperation::EndPath => "EndPath",
            ContentOperation::Clip => "Clip",
            ContentOperation::ClipEvenOdd => "ClipEvenOdd",
            ContentOperation::SetStrokingColorSpace(_) => "SetStrokingColorSpace",
            ContentOperation::SetNonStrokingColorSpace(_) => "SetNonStrokingColorSpace",
            ContentOperation::SetStrokingColor(_) => "SetStrokingColor",
            ContentOperation::SetNonStrokingColor(_) => "SetNonStrokingColor",
            ContentOperation::SetStrokingGray(_) => "SetStrokingGray",
            ContentOperation::SetNonStrokingGray(_) => "SetNonStrokingGray",
            ContentOperation::SetStrokingRGB(_, _, _) => "SetStrokingRGB",
            ContentOperation::SetNonStrokingRGB(_, _, _) => "SetNonStrokingRGB",
            ContentOperation::SetStrokingCMYK(_, _, _, _) => "SetStrokingCMYK",
            ContentOperation::SetNonStrokingCMYK(_, _, _, _) => "SetNonStrokingCMYK",
            ContentOperation::ShadingFill(_) => "ShadingFill",
            ContentOperation::BeginInlineImage => "BeginInlineImage",
            ContentOperation::InlineImage { .. } => "InlineImage",
            ContentOperation::PaintXObject(_) => "PaintXObject",
            ContentOperation::BeginMarkedContent(_) => "BeginMarkedContent",
            ContentOperation::BeginMarkedContentWithProps(_, _) => "BeginMarkedContentWithProps",
            ContentOperation::EndMarkedContent => "EndMarkedContent",
            ContentOperation::DefineMarkedContentPoint(_) => "DefineMarkedContentPoint",
            ContentOperation::DefineMarkedContentPointWithProps(_, _) => {
                "DefineMarkedContentPointWithProps"
            }
            ContentOperation::BeginCompatibility => "BeginCompatibility",
            ContentOperation::EndCompatibility => "EndCompatibility",
        }
    }

    #[getter]
    fn operands(&self) -> Vec<f64> {
        match &self.inner {
            ContentOperation::SetCharSpacing(v)
            | ContentOperation::SetWordSpacing(v)
            | ContentOperation::SetHorizontalScaling(v)
            | ContentOperation::SetLeading(v)
            | ContentOperation::SetTextRise(v)
            | ContentOperation::SetLineWidth(v)
            | ContentOperation::SetMiterLimit(v)
            | ContentOperation::SetFlatness(v)
            | ContentOperation::SetStrokingGray(v)
            | ContentOperation::SetNonStrokingGray(v) => vec![*v as f64],
            ContentOperation::SetLineCap(v) | ContentOperation::SetLineJoin(v) => {
                vec![*v as f64]
            }
            ContentOperation::SetTextRenderMode(v) => vec![*v as f64],
            ContentOperation::MoveText(x, y)
            | ContentOperation::MoveTextSetLeading(x, y)
            | ContentOperation::MoveTo(x, y)
            | ContentOperation::LineTo(x, y) => vec![*x as f64, *y as f64],
            ContentOperation::SetFont(_, size) => vec![*size as f64],
            ContentOperation::SetTextMatrix(a, b, c, d, e, f)
            | ContentOperation::SetTransformMatrix(a, b, c, d, e, f)
            | ContentOperation::CurveTo(a, b, c, d, e, f) => {
                vec![*a as f64, *b as f64, *c as f64, *d as f64, *e as f64, *f as f64]
            }
            ContentOperation::CurveToV(a, b, c, d)
            | ContentOperation::CurveToY(a, b, c, d)
            | ContentOperation::Rectangle(a, b, c, d)
            | ContentOperation::SetStrokingCMYK(a, b, c, d)
            | ContentOperation::SetNonStrokingCMYK(a, b, c, d) => {
                vec![*a as f64, *b as f64, *c as f64, *d as f64]
            }
            ContentOperation::SetStrokingRGB(r, g, b)
            | ContentOperation::SetNonStrokingRGB(r, g, b) => {
                vec![*r as f64, *g as f64, *b as f64]
            }
            ContentOperation::SetStrokingColor(v) | ContentOperation::SetNonStrokingColor(v) => {
                v.iter().map(|x| *x as f64).collect()
            }
            ContentOperation::SetSpacingNextLineShowText(a, b, _) => {
                vec![*a as f64, *b as f64]
            }
            ContentOperation::SetDashPattern(pattern, phase) => {
                let mut result: Vec<f64> = pattern.iter().map(|x| *x as f64).collect();
                result.push(*phase as f64);
                result
            }
            _ => vec![],
        }
    }

    #[getter]
    fn name(&self) -> Option<String> {
        match &self.inner {
            ContentOperation::SetFont(name, _) => Some(name.clone()),
            ContentOperation::SetGraphicsStateParams(name)
            | ContentOperation::PaintXObject(name)
            | ContentOperation::ShadingFill(name)
            | ContentOperation::SetIntent(name)
            | ContentOperation::SetStrokingColorSpace(name)
            | ContentOperation::SetNonStrokingColorSpace(name)
            | ContentOperation::BeginMarkedContent(name)
            | ContentOperation::DefineMarkedContentPoint(name) => Some(name.clone()),
            ContentOperation::BeginMarkedContentWithProps(name, _)
            | ContentOperation::DefineMarkedContentPointWithProps(name, _) => Some(name.clone()),
            _ => None,
        }
    }

    #[getter]
    fn font_name(&self) -> Option<String> {
        match &self.inner {
            ContentOperation::SetFont(name, _) => Some(name.clone()),
            _ => None,
        }
    }

    #[getter]
    fn font_size(&self) -> Option<f64> {
        match &self.inner {
            ContentOperation::SetFont(_, size) => Some(*size as f64),
            _ => None,
        }
    }

    #[getter]
    fn text_bytes(&self) -> Option<Vec<u8>> {
        match &self.inner {
            ContentOperation::ShowText(bytes) | ContentOperation::NextLineShowText(bytes) => {
                Some(bytes.clone())
            }
            ContentOperation::SetSpacingNextLineShowText(_, _, bytes) => Some(bytes.clone()),
            _ => None,
        }
    }

    /// For ShowTextArray (TJ operator): returns the list of TextElement items.
    #[getter]
    fn text_array_elements(&self) -> Option<Vec<PyTextElement>> {
        match &self.inner {
            ContentOperation::ShowTextArray(elems) => Some(
                elems.iter().map(|e| PyTextElement { inner: e.clone() }).collect()
            ),
            _ => None,
        }
    }

    fn __repr__(&self) -> String {
        let ops = self.operands();
        if ops.is_empty() {
            if let Some(name) = self.name() {
                format!("ContentOperation({}, name={:?})", self.op_type(), name)
            } else {
                format!("ContentOperation({})", self.op_type())
            }
        } else {
            format!("ContentOperation({}, {:?})", self.op_type(), ops)
        }
    }
}

// ── PyTextElement ──────────────────────────────────────────────────────────

/// An element in a TJ (ShowTextArray) operation.
///
/// Either a text segment (``is_text``, ``text_bytes``) or a kerning
/// adjustment (``is_spacing``, ``spacing``).
#[pyclass(name = "TextElement", frozen, from_py_object, eq)]
#[derive(Clone, PartialEq)]
pub struct PyTextElement {
    pub inner: TextElement,
}

#[pymethods]
impl PyTextElement {
    #[getter]
    fn is_text(&self) -> bool {
        matches!(self.inner, TextElement::Text(_))
    }

    #[getter]
    fn is_spacing(&self) -> bool {
        matches!(self.inner, TextElement::Spacing(_))
    }

    #[getter]
    fn text_bytes(&self) -> Option<Vec<u8>> {
        match &self.inner {
            TextElement::Text(v) => Some(v.clone()),
            _ => None,
        }
    }

    #[getter]
    fn spacing(&self) -> Option<f64> {
        match &self.inner {
            TextElement::Spacing(v) => Some(*v as f64),
            _ => None,
        }
    }

    fn __repr__(&self) -> String {
        format!("TextElement({:?})", self.inner)
    }
}

// ── PyContentParser ────────────────────────────────────────────────────────

/// Low-level PDF content stream parser.
///
/// Parses raw PDF page content bytes into a sequence of ContentOperation objects.
/// Returns an empty list on parse errors instead of raising exceptions.
#[pyclass(name = "ContentParser")]
pub struct PyContentParser;

#[pymethods]
impl PyContentParser {
    /// Parse a PDF content stream into a list of operations.
    ///
    /// Returns an empty list if the content cannot be parsed.
    #[staticmethod]
    fn parse(content: &[u8]) -> PyResult<Vec<PyContentOperation>> {
        match ContentParser::parse_content(content) {
            Ok(ops) => Ok(ops
                .into_iter()
                .map(|o| PyContentOperation { inner: o })
                .collect()),
            Err(_) => Ok(vec![]),
        }
    }

    /// Alias for ``parse()``. Matches the Rust core API name ``ContentParser::parse_content()``.
    #[staticmethod]
    fn parse_content(content: &[u8]) -> PyResult<Vec<PyContentOperation>> {
        PyContentParser::parse(content)
    }

    /// Parse a content stream, raising on errors instead of returning empty.
    ///
    /// Use this when you need to distinguish "empty stream" from "invalid stream".
    #[staticmethod]
    fn parse_strict(content: &[u8]) -> PyResult<Vec<PyContentOperation>> {
        ContentParser::parse_content(content)
            .map(|ops| ops.into_iter().map(|o| PyContentOperation { inner: o }).collect())
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }
}

// ── PyXRefEntry ────────────────────────────────────────────────────────────

/// A single entry in a PDF cross-reference table.
#[pyclass(name = "XRefEntry", from_py_object)]
#[derive(Clone)]
pub struct PyXRefEntry {
    pub inner: XRefEntry,
}

#[pymethods]
impl PyXRefEntry {
    #[new]
    fn new(offset: u64, generation: u16, in_use: bool) -> Self {
        Self {
            inner: XRefEntry {
                offset,
                generation,
                in_use,
            },
        }
    }

    #[getter]
    fn offset(&self) -> u64 {
        self.inner.offset
    }

    #[getter]
    fn generation(&self) -> u16 {
        self.inner.generation
    }

    #[getter]
    fn in_use(&self) -> bool {
        self.inner.in_use
    }

    fn __repr__(&self) -> String {
        format!(
            "XRefEntry(offset={}, gen={}, in_use={})",
            self.inner.offset, self.inner.generation, self.inner.in_use
        )
    }
}

// ── PyXRefTable ────────────────────────────────────────────────────────────

/// PDF cross-reference table mapping object numbers to file offsets.
#[pyclass(name = "XRefTable")]
pub struct PyXRefTable {
    pub inner: XRefTable,
}

#[pymethods]
impl PyXRefTable {
    #[new]
    fn new() -> Self {
        Self {
            inner: XRefTable::new(),
        }
    }

    fn add_entry(&mut self, obj_num: u32, entry: &PyXRefEntry) {
        self.inner.add_entry(obj_num, entry.inner.clone());
    }

    fn get_entry(&self, obj_num: u32) -> Option<PyXRefEntry> {
        self.inner
            .get_entry(obj_num)
            .map(|e| PyXRefEntry { inner: *e })
    }

    #[getter]
    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    fn __len__(&self) -> usize {
        self.inner.len()
    }

    /// Return all entries as a list of (object_number, XRefEntry) tuples.
    fn entries(&self) -> Vec<(u32, PyXRefEntry)> {
        self.inner
            .iter()
            .map(|(num, entry)| (*num, PyXRefEntry { inner: *entry }))
            .collect()
    }

    fn __repr__(&self) -> String {
        format!("XRefTable(entries={})", self.inner.len())
    }
}

// ── Register ───────────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyContentParser>()?;
    m.add_class::<PyContentOperation>()?;
    m.add_class::<PyTextElement>()?;
    m.add_class::<PyXRefTable>()?;
    m.add_class::<PyXRefEntry>()?;
    Ok(())
}
