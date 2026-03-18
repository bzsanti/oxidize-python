use pyo3::prelude::*;

use oxidize_pdf::text::{HeaderFooter, HeaderFooterOptions};

use crate::errors;

// ── Font ───────────────────────────────────────────────────────────────────

/// PDF fonts — standard 14 or custom.
///
/// Standard fonts as class attributes: ``Font.HELVETICA``, ``Font.TIMES_ROMAN``, etc.
/// Custom fonts: ``Font.custom("MyFont")``, ``Font.from_file("Name", "path.ttf")``,
/// or ``Font.from_bytes("Name", data)``.
#[pyclass(name = "Font", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyFont {
    pub inner: oxidize_pdf::Font,
}

#[pymethods]
impl PyFont {
    #[classattr]
    const HELVETICA: PyFont = PyFont {
        inner: oxidize_pdf::Font::Helvetica,
    };
    #[classattr]
    const HELVETICA_BOLD: PyFont = PyFont {
        inner: oxidize_pdf::Font::HelveticaBold,
    };
    #[classattr]
    const HELVETICA_OBLIQUE: PyFont = PyFont {
        inner: oxidize_pdf::Font::HelveticaOblique,
    };
    #[classattr]
    const HELVETICA_BOLD_OBLIQUE: PyFont = PyFont {
        inner: oxidize_pdf::Font::HelveticaBoldOblique,
    };
    #[classattr]
    const TIMES_ROMAN: PyFont = PyFont {
        inner: oxidize_pdf::Font::TimesRoman,
    };
    #[classattr]
    const TIMES_BOLD: PyFont = PyFont {
        inner: oxidize_pdf::Font::TimesBold,
    };
    #[classattr]
    const TIMES_ITALIC: PyFont = PyFont {
        inner: oxidize_pdf::Font::TimesItalic,
    };
    #[classattr]
    const TIMES_BOLD_ITALIC: PyFont = PyFont {
        inner: oxidize_pdf::Font::TimesBoldItalic,
    };
    #[classattr]
    const COURIER: PyFont = PyFont {
        inner: oxidize_pdf::Font::Courier,
    };
    #[classattr]
    const COURIER_BOLD: PyFont = PyFont {
        inner: oxidize_pdf::Font::CourierBold,
    };
    #[classattr]
    const COURIER_OBLIQUE: PyFont = PyFont {
        inner: oxidize_pdf::Font::CourierOblique,
    };
    #[classattr]
    const COURIER_BOLD_OBLIQUE: PyFont = PyFont {
        inner: oxidize_pdf::Font::CourierBoldOblique,
    };
    #[classattr]
    const SYMBOL: PyFont = PyFont {
        inner: oxidize_pdf::Font::Symbol,
    };
    #[classattr]
    const ZAPF_DINGBATS: PyFont = PyFont {
        inner: oxidize_pdf::Font::ZapfDingbats,
    };

    /// Create a custom font reference by name.
    ///
    /// The font name is used as a PDF resource name. For pre-registered
    /// or system fonts this is sufficient. For fonts loaded from files,
    /// use ``from_file`` or ``from_bytes`` instead.
    #[staticmethod]
    fn custom(name: &str) -> Self {
        Self {
            inner: oxidize_pdf::Font::custom(name),
        }
    }

    /// Load a custom font from a TrueType/OpenType file.
    ///
    /// Validates the font data and returns a ``Font`` reference.
    ///
    /// Raises:
    ///     PdfError: If the file cannot be read or is not a valid font.
    #[staticmethod]
    fn from_file(name: &str, path: &str) -> PyResult<Self> {
        // Validate the font data by loading it.
        oxidize_pdf::fonts::Font::from_file(name, path).map_err(errors::to_py_err)?;
        Ok(Self {
            inner: oxidize_pdf::Font::custom(name),
        })
    }

    /// Load a custom font from byte data (TrueType/OpenType).
    ///
    /// Validates the font data and returns a ``Font`` reference.
    ///
    /// Raises:
    ///     PdfError: If the data is not a valid font.
    #[staticmethod]
    fn from_bytes(name: &str, data: &[u8]) -> PyResult<Self> {
        // Validate the font data by loading it.
        oxidize_pdf::fonts::Font::from_bytes(name, data.to_vec()).map_err(errors::to_py_err)?;
        Ok(Self {
            inner: oxidize_pdf::Font::custom(name),
        })
    }

    fn __repr__(&self) -> String {
        format!("Font.{}", font_name(&self.inner))
    }
}

fn font_name(font: &oxidize_pdf::Font) -> String {
    match font {
        oxidize_pdf::Font::Helvetica => "HELVETICA".into(),
        oxidize_pdf::Font::HelveticaBold => "HELVETICA_BOLD".into(),
        oxidize_pdf::Font::HelveticaOblique => "HELVETICA_OBLIQUE".into(),
        oxidize_pdf::Font::HelveticaBoldOblique => "HELVETICA_BOLD_OBLIQUE".into(),
        oxidize_pdf::Font::TimesRoman => "TIMES_ROMAN".into(),
        oxidize_pdf::Font::TimesBold => "TIMES_BOLD".into(),
        oxidize_pdf::Font::TimesItalic => "TIMES_ITALIC".into(),
        oxidize_pdf::Font::TimesBoldItalic => "TIMES_BOLD_ITALIC".into(),
        oxidize_pdf::Font::Courier => "COURIER".into(),
        oxidize_pdf::Font::CourierBold => "COURIER_BOLD".into(),
        oxidize_pdf::Font::CourierOblique => "COURIER_OBLIQUE".into(),
        oxidize_pdf::Font::CourierBoldOblique => "COURIER_BOLD_OBLIQUE".into(),
        oxidize_pdf::Font::Symbol => "SYMBOL".into(),
        oxidize_pdf::Font::ZapfDingbats => "ZAPF_DINGBATS".into(),
        oxidize_pdf::Font::Custom(name) => format!("CUSTOM({name})"),
    }
}

// ── TextAlign ──────────────────────────────────────────────────────────────

#[pyclass(name = "TextAlign", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTextAlign {
    pub inner: oxidize_pdf::TextAlign,
}

#[pymethods]
impl PyTextAlign {
    #[classattr]
    const LEFT: PyTextAlign = PyTextAlign {
        inner: oxidize_pdf::TextAlign::Left,
    };
    #[classattr]
    const RIGHT: PyTextAlign = PyTextAlign {
        inner: oxidize_pdf::TextAlign::Right,
    };
    #[classattr]
    const CENTER: PyTextAlign = PyTextAlign {
        inner: oxidize_pdf::TextAlign::Center,
    };
    #[classattr]
    const JUSTIFIED: PyTextAlign = PyTextAlign {
        inner: oxidize_pdf::TextAlign::Justified,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            oxidize_pdf::TextAlign::Left => "LEFT",
            oxidize_pdf::TextAlign::Right => "RIGHT",
            oxidize_pdf::TextAlign::Center => "CENTER",
            oxidize_pdf::TextAlign::Justified => "JUSTIFIED",
        };
        format!("TextAlign.{name}")
    }
}

// ── HeaderFooterOptions ────────────────────────────────────────────────────

#[pyclass(name = "HeaderFooterOptions", from_py_object)]
#[derive(Clone)]
pub struct PyHeaderFooterOptions {
    pub inner: HeaderFooterOptions,
}

#[pymethods]
impl PyHeaderFooterOptions {
    #[new]
    #[pyo3(signature = (font=None, font_size=None, alignment=None, margin=None, show_page_numbers=None))]
    fn new(
        font: Option<&PyFont>,
        font_size: Option<f64>,
        alignment: Option<&PyTextAlign>,
        margin: Option<f64>,
        show_page_numbers: Option<bool>,
    ) -> Self {
        let mut opts = HeaderFooterOptions::default();
        if let Some(f) = font {
            opts.font = f.inner.clone();
        }
        if let Some(s) = font_size {
            opts.font_size = s;
        }
        if let Some(a) = alignment {
            opts.alignment = a.inner;
        }
        if let Some(m) = margin {
            opts.margin = m;
        }
        if let Some(s) = show_page_numbers {
            opts.show_page_numbers = s;
        }
        Self { inner: opts }
    }

    fn __repr__(&self) -> String {
        format!(
            "HeaderFooterOptions(font_size={}, margin={})",
            self.inner.font_size, self.inner.margin
        )
    }
}

// ── HeaderFooter ──────────────────────────────────────────────────────────

#[pyclass(name = "HeaderFooter", from_py_object)]
#[derive(Clone)]
pub struct PyHeaderFooter {
    pub inner: HeaderFooter,
}

#[pymethods]
impl PyHeaderFooter {
    #[staticmethod]
    fn new_header(content: &str) -> Self {
        Self {
            inner: HeaderFooter::new_header(content),
        }
    }

    #[staticmethod]
    fn new_footer(content: &str) -> Self {
        Self {
            inner: HeaderFooter::new_footer(content),
        }
    }

    fn with_options(self_: PyRef<'_, Self>, options: &PyHeaderFooterOptions) -> Self {
        Self {
            inner: self_.inner.clone().with_options(options.inner.clone()),
        }
    }

    fn with_font(self_: PyRef<'_, Self>, font: &PyFont, size: f64) -> Self {
        Self {
            inner: self_.inner.clone().with_font(font.inner.clone(), size),
        }
    }

    fn with_alignment(self_: PyRef<'_, Self>, alignment: &PyTextAlign) -> Self {
        Self {
            inner: self_.inner.clone().with_alignment(alignment.inner),
        }
    }

    fn with_margin(self_: PyRef<'_, Self>, margin: f64) -> Self {
        Self {
            inner: self_.inner.clone().with_margin(margin),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "HeaderFooter({:?}, content={:?})",
            self.inner.position(),
            self.inner.content()
        )
    }
}

// ── Text measurement ──────────────────────────────────────────────────────

#[pyfunction]
#[pyo3(name = "measure_text")]
pub fn py_measure_text(text: &str, font: &PyFont, size: f64) -> f64 {
    oxidize_pdf::measure_text(text, font.inner.clone(), size)
}

#[pyfunction]
#[pyo3(name = "measure_char")]
pub fn py_measure_char(ch: &str, font: &PyFont, size: f64) -> PyResult<f64> {
    let mut chars = ch.chars();
    let c = chars.next().ok_or_else(|| {
        pyo3::exceptions::PyValueError::new_err("Expected a single character, got empty string")
    })?;
    if chars.next().is_some() {
        return Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Expected a single character, got string of length {}",
            ch.len()
        )));
    }
    Ok(oxidize_pdf::text::metrics::measure_char(
        c,
        font.inner.clone(),
        size,
    ))
}

// ── TextRenderingMode ─────────────────────────────────────────────────────

#[pyclass(name = "TextRenderingMode", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTextRenderingMode {
    pub inner: oxidize_pdf::text::TextRenderingMode,
}

#[pymethods]
impl PyTextRenderingMode {
    #[classattr]
    const FILL: PyTextRenderingMode = PyTextRenderingMode {
        inner: oxidize_pdf::text::TextRenderingMode::Fill,
    };
    #[classattr]
    const STROKE: PyTextRenderingMode = PyTextRenderingMode {
        inner: oxidize_pdf::text::TextRenderingMode::Stroke,
    };
    #[classattr]
    const FILL_STROKE: PyTextRenderingMode = PyTextRenderingMode {
        inner: oxidize_pdf::text::TextRenderingMode::FillStroke,
    };
    #[classattr]
    const INVISIBLE: PyTextRenderingMode = PyTextRenderingMode {
        inner: oxidize_pdf::text::TextRenderingMode::Invisible,
    };
    #[classattr]
    const FILL_CLIP: PyTextRenderingMode = PyTextRenderingMode {
        inner: oxidize_pdf::text::TextRenderingMode::FillClip,
    };
    #[classattr]
    const STROKE_CLIP: PyTextRenderingMode = PyTextRenderingMode {
        inner: oxidize_pdf::text::TextRenderingMode::StrokeClip,
    };
    #[classattr]
    const FILL_STROKE_CLIP: PyTextRenderingMode = PyTextRenderingMode {
        inner: oxidize_pdf::text::TextRenderingMode::FillStrokeClip,
    };
    #[classattr]
    const CLIP: PyTextRenderingMode = PyTextRenderingMode {
        inner: oxidize_pdf::text::TextRenderingMode::Clip,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            oxidize_pdf::text::TextRenderingMode::Fill => "FILL",
            oxidize_pdf::text::TextRenderingMode::Stroke => "STROKE",
            oxidize_pdf::text::TextRenderingMode::FillStroke => "FILL_STROKE",
            oxidize_pdf::text::TextRenderingMode::Invisible => "INVISIBLE",
            oxidize_pdf::text::TextRenderingMode::FillClip => "FILL_CLIP",
            oxidize_pdf::text::TextRenderingMode::StrokeClip => "STROKE_CLIP",
            oxidize_pdf::text::TextRenderingMode::FillStrokeClip => "FILL_STROKE_CLIP",
            oxidize_pdf::text::TextRenderingMode::Clip => "CLIP",
        };
        format!("TextRenderingMode.{name}")
    }
}

// ── FontEncoding ───────────────────────────────────────────────────────────

#[pyclass(name = "FontEncoding", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyFontEncoding {
    pub inner: oxidize_pdf::text::FontEncoding,
}

#[pymethods]
impl PyFontEncoding {
    #[classattr]
    const WIN_ANSI: PyFontEncoding = PyFontEncoding {
        inner: oxidize_pdf::text::FontEncoding::WinAnsiEncoding,
    };
    #[classattr]
    const MAC_ROMAN: PyFontEncoding = PyFontEncoding {
        inner: oxidize_pdf::text::FontEncoding::MacRomanEncoding,
    };
    #[classattr]
    const STANDARD: PyFontEncoding = PyFontEncoding {
        inner: oxidize_pdf::text::FontEncoding::StandardEncoding,
    };
    #[classattr]
    const MAC_EXPERT: PyFontEncoding = PyFontEncoding {
        inner: oxidize_pdf::text::FontEncoding::MacExpertEncoding,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            oxidize_pdf::text::FontEncoding::WinAnsiEncoding => "WIN_ANSI",
            oxidize_pdf::text::FontEncoding::MacRomanEncoding => "MAC_ROMAN",
            oxidize_pdf::text::FontEncoding::StandardEncoding => "STANDARD",
            oxidize_pdf::text::FontEncoding::MacExpertEncoding => "MAC_EXPERT",
            oxidize_pdf::text::FontEncoding::Custom(_) => "CUSTOM",
        };
        format!("FontEncoding.{name}")
    }
}

// ── Registration ───────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyFont>()?;
    m.add_class::<PyTextAlign>()?;
    m.add_class::<PyHeaderFooterOptions>()?;
    m.add_class::<PyHeaderFooter>()?;
    m.add_class::<PyTextRenderingMode>()?;
    m.add_class::<PyFontEncoding>()?;
    m.add_function(wrap_pyfunction!(py_measure_text, m)?)?;
    m.add_function(wrap_pyfunction!(py_measure_char, m)?)?;
    Ok(())
}
