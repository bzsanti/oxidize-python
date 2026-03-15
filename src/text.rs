use pyo3::prelude::*;

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

fn font_name(font: &oxidize_pdf::Font) -> &'static str {
    match font {
        oxidize_pdf::Font::Helvetica => "HELVETICA",
        oxidize_pdf::Font::HelveticaBold => "HELVETICA_BOLD",
        oxidize_pdf::Font::HelveticaOblique => "HELVETICA_OBLIQUE",
        oxidize_pdf::Font::HelveticaBoldOblique => "HELVETICA_BOLD_OBLIQUE",
        oxidize_pdf::Font::TimesRoman => "TIMES_ROMAN",
        oxidize_pdf::Font::TimesBold => "TIMES_BOLD",
        oxidize_pdf::Font::TimesItalic => "TIMES_ITALIC",
        oxidize_pdf::Font::TimesBoldItalic => "TIMES_BOLD_ITALIC",
        oxidize_pdf::Font::Courier => "COURIER",
        oxidize_pdf::Font::CourierBold => "COURIER_BOLD",
        oxidize_pdf::Font::CourierOblique => "COURIER_OBLIQUE",
        oxidize_pdf::Font::CourierBoldOblique => "COURIER_BOLD_OBLIQUE",
        oxidize_pdf::Font::Symbol => "SYMBOL",
        oxidize_pdf::Font::ZapfDingbats => "ZAPF_DINGBATS",
        oxidize_pdf::Font::Custom(name) => {
            Box::leak(format!("CUSTOM({name})").into_boxed_str())
        }
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

// ── Registration ───────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyFont>()?;
    m.add_class::<PyTextAlign>()?;
    Ok(())
}
