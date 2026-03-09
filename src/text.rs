use pyo3::prelude::*;

// ── Font ───────────────────────────────────────────────────────────────────

/// Standard PDF fonts.
///
/// Access as class attributes: ``Font.HELVETICA``, ``Font.TIMES_ROMAN``, etc.
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
