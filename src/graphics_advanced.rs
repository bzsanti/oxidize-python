//! Advanced graphics bindings — Features 65-70
//!
//! Wraps advanced PDF graphics primitives from `oxidize_pdf::graphics`:
//! - F65: Shadings (axial/radial gradients)
//! - F66: Patterns (tiling)
//! - F67: Form XObjects (reusable content)
//! - F68: ExtGState (extended graphics state)
//! - F69: SoftMask + TransparencyGroup
//! - F70: Advanced Color Spaces (ICC, Separation, SpotColors)

use pyo3::prelude::*;

use oxidize_pdf::graphics::{
    // Shadings (F65)
    AxialShading,
    ColorStop,
    Point as ShadingPointInner,
    RadialShading,
    ShadingDefinition,
    ShadingManager,
    ShadingType,
    // Patterns (F66)
    PaintType,
    PatternManager,
    PatternMatrix,
    TilingPattern,
    TilingType,
    // FormXObject (F67)
    FormTemplates,
    FormXObject,
    FormXObjectBuilder,
    FormXObjectManager,
    // ExtGState (F68)
    ExtGState,
    ExtGStateManager,
    RenderingIntent,
    // SoftMask + TransparencyGroup (F69)
    SoftMask,
    SoftMaskState,
    SoftMaskType,
    TransparencyGroup,
    // Color Profiles (F70)
    IccColorSpace,
    IccProfile,
    IccProfileManager,
    SeparationColor,
    SeparationColorSpace,
    SpotColors,
    StandardIccProfile,
};

use crate::errors::to_py_err;
use crate::types::{PyColor, PyRectangle};

// ── ShadingType ────────────────────────────────────────────────────────────

// (ShadingPointInner is oxidize_pdf::graphics::Point, aliased to avoid conflict with geometry::Point)

#[pyclass(name = "ShadingType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyShadingType {
    pub inner: ShadingType,
}

#[pymethods]
impl PyShadingType {
    #[classattr]
    const FUNCTION_BASED: Self = Self { inner: ShadingType::FunctionBased };
    #[classattr]
    const AXIAL: Self = Self { inner: ShadingType::Axial };
    #[classattr]
    const RADIAL: Self = Self { inner: ShadingType::Radial };
    #[classattr]
    const FREE_FORM_GOURAUD: Self = Self { inner: ShadingType::FreeFormGouraud };
    #[classattr]
    const LATTICE_FORM_GOURAUD: Self = Self { inner: ShadingType::LatticeFormGouraud };
    #[classattr]
    const COONS_PATCH: Self = Self { inner: ShadingType::CoonsPatch };
    #[classattr]
    const TENSOR_PRODUCT_PATCH: Self = Self { inner: ShadingType::TensorProductPatch };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            ShadingType::FunctionBased => "FUNCTION_BASED",
            ShadingType::Axial => "AXIAL",
            ShadingType::Radial => "RADIAL",
            ShadingType::FreeFormGouraud => "FREE_FORM_GOURAUD",
            ShadingType::LatticeFormGouraud => "LATTICE_FORM_GOURAUD",
            ShadingType::CoonsPatch => "COONS_PATCH",
            ShadingType::TensorProductPatch => "TENSOR_PRODUCT_PATCH",
        };
        format!("ShadingType.{name}")
    }
}

// ── PaintType ─────────────────────────────────────────────────────────────

#[pyclass(name = "PaintType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyPaintType {
    pub inner: PaintType,
}

#[pymethods]
impl PyPaintType {
    #[classattr]
    const COLORED: Self = Self { inner: PaintType::Colored };
    #[classattr]
    const UNCOLORED: Self = Self { inner: PaintType::Uncolored };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            PaintType::Colored => "COLORED",
            PaintType::Uncolored => "UNCOLORED",
        };
        format!("PaintType.{name}")
    }
}

// ── TilingType ────────────────────────────────────────────────────────────

#[pyclass(name = "TilingType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTilingType {
    pub inner: TilingType,
}

#[pymethods]
impl PyTilingType {
    #[classattr]
    const CONSTANT_SPACING: Self = Self { inner: TilingType::ConstantSpacing };
    #[classattr]
    const NO_DISTORTION: Self = Self { inner: TilingType::NoDistortion };
    #[classattr]
    const CONSTANT_SPACING_FASTER: Self = Self { inner: TilingType::ConstantSpacingFaster };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            TilingType::ConstantSpacing => "CONSTANT_SPACING",
            TilingType::NoDistortion => "NO_DISTORTION",
            TilingType::ConstantSpacingFaster => "CONSTANT_SPACING_FASTER",
        };
        format!("TilingType.{name}")
    }
}

// ── RenderingIntent ───────────────────────────────────────────────────────

#[pyclass(name = "RenderingIntent", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyRenderingIntent {
    pub inner: RenderingIntent,
}

#[pymethods]
impl PyRenderingIntent {
    #[classattr]
    const ABSOLUTE_COLORIMETRIC: Self = Self { inner: RenderingIntent::AbsoluteColorimetric };
    #[classattr]
    const RELATIVE_COLORIMETRIC: Self = Self { inner: RenderingIntent::RelativeColorimetric };
    #[classattr]
    const SATURATION: Self = Self { inner: RenderingIntent::Saturation };
    #[classattr]
    const PERCEPTUAL: Self = Self { inner: RenderingIntent::Perceptual };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            RenderingIntent::AbsoluteColorimetric => "ABSOLUTE_COLORIMETRIC",
            RenderingIntent::RelativeColorimetric => "RELATIVE_COLORIMETRIC",
            RenderingIntent::Saturation => "SATURATION",
            RenderingIntent::Perceptual => "PERCEPTUAL",
        };
        format!("RenderingIntent.{name}")
    }
}

// ── SoftMaskType ──────────────────────────────────────────────────────────

#[pyclass(name = "SoftMaskType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PySoftMaskType {
    pub inner: SoftMaskType,
}

#[pymethods]
impl PySoftMaskType {
    #[classattr]
    const ALPHA: Self = Self { inner: SoftMaskType::Alpha };
    #[classattr]
    const LUMINOSITY: Self = Self { inner: SoftMaskType::Luminosity };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            SoftMaskType::Alpha => "ALPHA",
            SoftMaskType::Luminosity => "LUMINOSITY",
        };
        format!("SoftMaskType.{name}")
    }
}

// ── IccColorSpace ─────────────────────────────────────────────────────────

#[pyclass(name = "IccColorSpace", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyIccColorSpace {
    pub inner: IccColorSpace,
}

#[pymethods]
impl PyIccColorSpace {
    #[classattr]
    const RGB: Self = Self { inner: IccColorSpace::Rgb };
    #[classattr]
    const CMYK: Self = Self { inner: IccColorSpace::Cmyk };
    #[classattr]
    const LAB: Self = Self { inner: IccColorSpace::Lab };
    #[classattr]
    const GRAY: Self = Self { inner: IccColorSpace::Gray };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            IccColorSpace::Rgb => "RGB",
            IccColorSpace::Cmyk => "CMYK",
            IccColorSpace::Lab => "LAB",
            IccColorSpace::Gray => "GRAY",
            IccColorSpace::Generic(n) => return format!("IccColorSpace.GENERIC({n})"),
        };
        format!("IccColorSpace.{name}")
    }
}

// ── StandardIccProfile ────────────────────────────────────────────────────

#[pyclass(name = "StandardIccProfile", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyStandardIccProfile {
    pub inner: StandardIccProfile,
}

#[pymethods]
impl PyStandardIccProfile {
    #[classattr]
    const S_RGB: Self = Self { inner: StandardIccProfile::SRgb };
    #[classattr]
    const ADOBE_RGB: Self = Self { inner: StandardIccProfile::AdobeRgb };
    #[classattr]
    const PRO_PHOTO_RGB: Self = Self { inner: StandardIccProfile::ProPhotoRgb };
    #[classattr]
    const USWC_SWOP_V2: Self = Self { inner: StandardIccProfile::UswcSwopV2 };
    #[classattr]
    const COATED_FOGRA39: Self = Self { inner: StandardIccProfile::CoatedFogra39 };
    #[classattr]
    const UNCOATED_FOGRA29: Self = Self { inner: StandardIccProfile::UncoatedFogra29 };
    #[classattr]
    const GRAY_GAMMA22: Self = Self { inner: StandardIccProfile::GrayGamma22 };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            StandardIccProfile::SRgb => "S_RGB",
            StandardIccProfile::AdobeRgb => "ADOBE_RGB",
            StandardIccProfile::ProPhotoRgb => "PRO_PHOTO_RGB",
            StandardIccProfile::UswcSwopV2 => "USWC_SWOP_V2",
            StandardIccProfile::CoatedFogra39 => "COATED_FOGRA39",
            StandardIccProfile::UncoatedFogra29 => "UNCOATED_FOGRA29",
            StandardIccProfile::GrayGamma22 => "GRAY_GAMMA22",
        };
        format!("StandardIccProfile.{name}")
    }
}

// ── ShadingPoint ──────────────────────────────────────────────────────────
// Note: shadings::Point is different from geometry::Point (PyPoint). Named ShadingPoint.

#[pyclass(name = "ShadingPoint", from_py_object)]
#[derive(Clone)]
pub struct PyShadingPoint {
    pub inner: ShadingPointInner,
}

#[pymethods]
impl PyShadingPoint {
    #[new]
    fn new(x: f64, y: f64) -> Self {
        Self { inner: ShadingPointInner::new(x, y) }
    }

    #[getter]
    fn x(&self) -> f64 {
        self.inner.x
    }

    #[getter]
    fn y(&self) -> f64 {
        self.inner.y
    }

    fn __repr__(&self) -> String {
        format!("ShadingPoint({}, {})", self.inner.x, self.inner.y)
    }
}

// ── ColorStop ─────────────────────────────────────────────────────────────

#[pyclass(name = "ColorStop", from_py_object)]
#[derive(Clone)]
pub struct PyColorStop {
    pub inner: ColorStop,
}

#[pymethods]
impl PyColorStop {
    #[new]
    fn new(position: f64, color: &PyColor) -> Self {
        Self { inner: ColorStop::new(position, color.inner) }
    }

    #[getter]
    fn position(&self) -> f64 {
        self.inner.position
    }

    fn __repr__(&self) -> String {
        format!("ColorStop(position={})", self.inner.position)
    }
}

// ── AxialShading ──────────────────────────────────────────────────────────

#[pyclass(name = "AxialShading", from_py_object)]
#[derive(Clone)]
pub struct PyAxialShading {
    pub inner: AxialShading,
}

#[pymethods]
impl PyAxialShading {
    #[new]
    fn new(
        name: &str,
        start_point: &PyShadingPoint,
        end_point: &PyShadingPoint,
        color_stops: Vec<PyRef<PyColorStop>>,
    ) -> Self {
        let stops = color_stops.iter().map(|s| s.inner.clone()).collect();
        Self {
            inner: AxialShading::new(
                name.to_string(),
                start_point.inner,
                end_point.inner,
                stops,
            ),
        }
    }

    #[staticmethod]
    fn linear_gradient(
        name: &str,
        start_point: &PyShadingPoint,
        end_point: &PyShadingPoint,
        start_color: &PyColor,
        end_color: &PyColor,
    ) -> Self {
        Self {
            inner: AxialShading::linear_gradient(
                name.to_string(),
                start_point.inner,
                end_point.inner,
                start_color.inner,
                end_color.inner,
            ),
        }
    }

    fn with_extend(&self, extend_start: bool, extend_end: bool) -> Self {
        Self { inner: self.inner.clone().with_extend(extend_start, extend_end) }
    }

    #[getter]
    fn name(&self) -> &str {
        &self.inner.name
    }

    #[getter]
    fn extend_start(&self) -> bool {
        self.inner.extend_start
    }

    #[getter]
    fn extend_end(&self) -> bool {
        self.inner.extend_end
    }

    fn validate(&self) -> PyResult<()> {
        self.inner.validate().map_err(to_py_err)
    }

    fn __repr__(&self) -> String {
        format!(
            "AxialShading(name={:?}, stops={})",
            self.inner.name,
            self.inner.color_stops.len()
        )
    }
}

// ── RadialShading ─────────────────────────────────────────────────────────

#[pyclass(name = "RadialShading", from_py_object)]
#[derive(Clone)]
pub struct PyRadialShading {
    pub inner: RadialShading,
}

#[pymethods]
impl PyRadialShading {
    #[new]
    fn new(
        name: &str,
        start_center: &PyShadingPoint,
        start_radius: f64,
        end_center: &PyShadingPoint,
        end_radius: f64,
        color_stops: Vec<PyRef<PyColorStop>>,
    ) -> Self {
        let stops = color_stops.iter().map(|s| s.inner.clone()).collect();
        Self {
            inner: RadialShading::new(
                name.to_string(),
                start_center.inner,
                start_radius,
                end_center.inner,
                end_radius,
                stops,
            ),
        }
    }

    #[staticmethod]
    fn radial_gradient(
        name: &str,
        center: &PyShadingPoint,
        start_radius: f64,
        end_radius: f64,
        start_color: &PyColor,
        end_color: &PyColor,
    ) -> Self {
        Self {
            inner: RadialShading::radial_gradient(
                name.to_string(),
                center.inner,
                start_radius,
                end_radius,
                start_color.inner,
                end_color.inner,
            ),
        }
    }

    fn with_extend(&self, extend_start: bool, extend_end: bool) -> Self {
        Self { inner: self.inner.clone().with_extend(extend_start, extend_end) }
    }

    #[getter]
    fn name(&self) -> &str {
        &self.inner.name
    }

    #[getter]
    fn start_radius(&self) -> f64 {
        self.inner.start_radius
    }

    #[getter]
    fn end_radius(&self) -> f64 {
        self.inner.end_radius
    }

    fn validate(&self) -> PyResult<()> {
        self.inner.validate().map_err(to_py_err)
    }

    fn __repr__(&self) -> String {
        format!(
            "RadialShading(name={:?}, stops={})",
            self.inner.name,
            self.inner.color_stops.len()
        )
    }
}

// ── ShadingManager ────────────────────────────────────────────────────────

#[pyclass(name = "ShadingManager")]
pub struct PyShadingManager {
    inner: ShadingManager,
}

#[pymethods]
impl PyShadingManager {
    #[new]
    fn new() -> Self {
        Self { inner: ShadingManager::new() }
    }

    fn add_axial_shading(&mut self, shading: &PyAxialShading) -> PyResult<String> {
        self.inner
            .add_shading(ShadingDefinition::Axial(shading.inner.clone()))
            .map_err(to_py_err)
    }

    fn add_radial_shading(&mut self, shading: &PyRadialShading) -> PyResult<String> {
        self.inner
            .add_shading(ShadingDefinition::Radial(shading.inner.clone()))
            .map_err(to_py_err)
    }

    fn create_linear_gradient(
        &mut self,
        start: &PyShadingPoint,
        end: &PyShadingPoint,
        start_color: &PyColor,
        end_color: &PyColor,
    ) -> PyResult<String> {
        self.inner
            .create_linear_gradient(start.inner, end.inner, start_color.inner, end_color.inner)
            .map_err(to_py_err)
    }

    fn create_radial_gradient(
        &mut self,
        center: &PyShadingPoint,
        start_radius: f64,
        end_radius: f64,
        start_color: &PyColor,
        end_color: &PyColor,
    ) -> PyResult<String> {
        self.inner
            .create_radial_gradient(
                center.inner,
                start_radius,
                end_radius,
                start_color.inner,
                end_color.inner,
            )
            .map_err(to_py_err)
    }

    fn shading_count(&self) -> usize {
        self.inner.shading_count()
    }

    fn clear(&mut self) {
        self.inner.clear();
    }

    fn __repr__(&self) -> String {
        format!("ShadingManager(shadings={})", self.inner.shading_count())
    }
}

// ── PatternMatrix ─────────────────────────────────────────────────────────

#[pyclass(name = "PatternMatrix", from_py_object)]
#[derive(Clone)]
pub struct PyPatternMatrix {
    pub inner: PatternMatrix,
}

#[pymethods]
impl PyPatternMatrix {
    #[staticmethod]
    fn identity() -> Self {
        Self { inner: PatternMatrix::identity() }
    }

    #[staticmethod]
    fn translation(tx: f64, ty: f64) -> Self {
        Self { inner: PatternMatrix::translation(tx, ty) }
    }

    #[staticmethod]
    fn scale(sx: f64, sy: f64) -> Self {
        Self { inner: PatternMatrix::scale(sx, sy) }
    }

    #[staticmethod]
    fn rotation(angle: f64) -> Self {
        Self { inner: PatternMatrix::rotation(angle) }
    }

    fn multiply(&self, other: &PyPatternMatrix) -> Self {
        Self { inner: self.inner.multiply(&other.inner) }
    }

    #[getter]
    fn matrix(&self) -> [f64; 6] {
        self.inner.matrix
    }

    fn __repr__(&self) -> String {
        format!("PatternMatrix({:?})", self.inner.matrix)
    }
}

// ── TilingPattern ─────────────────────────────────────────────────────────

#[pyclass(name = "TilingPattern", from_py_object)]
#[derive(Clone)]
pub struct PyTilingPattern {
    pub inner: TilingPattern,
}

#[pymethods]
impl PyTilingPattern {
    #[new]
    fn new(
        name: &str,
        paint_type: &PyPaintType,
        tiling_type: &PyTilingType,
        bbox: [f64; 4],
        x_step: f64,
        y_step: f64,
    ) -> Self {
        Self {
            inner: TilingPattern::new(
                name.to_string(),
                paint_type.inner,
                tiling_type.inner,
                bbox,
                x_step,
                y_step,
            ),
        }
    }

    fn with_matrix(&self, matrix: &PyPatternMatrix) -> Self {
        Self { inner: self.inner.clone().with_matrix(matrix.inner.clone()) }
    }

    fn add_rectangle(&mut self, x: f64, y: f64, width: f64, height: f64) {
        self.inner.add_rectangle(x, y, width, height);
    }

    fn add_line(&mut self, x1: f64, y1: f64, x2: f64, y2: f64) {
        self.inner.add_line(x1, y1, x2, y2);
    }

    fn add_circle(&mut self, cx: f64, cy: f64, radius: f64) {
        self.inner.add_circle(cx, cy, radius);
    }

    fn stroke(&mut self) {
        self.inner.stroke();
    }

    fn fill(&mut self) {
        self.inner.fill();
    }

    fn fill_and_stroke(&mut self) {
        self.inner.fill_and_stroke();
    }

    #[getter]
    fn name(&self) -> &str {
        &self.inner.name
    }

    #[getter]
    fn x_step(&self) -> f64 {
        self.inner.x_step
    }

    #[getter]
    fn y_step(&self) -> f64 {
        self.inner.y_step
    }

    fn __repr__(&self) -> String {
        format!("TilingPattern(name={:?})", self.inner.name)
    }
}

// ── PatternManager ────────────────────────────────────────────────────────

#[pyclass(name = "PatternManager")]
pub struct PyPatternManager {
    inner: PatternManager,
}

#[pymethods]
impl PyPatternManager {
    #[new]
    fn new() -> Self {
        Self { inner: PatternManager::new() }
    }

    fn add_pattern(&mut self, pattern: &PyTilingPattern) -> PyResult<String> {
        self.inner.add_pattern(pattern.inner.clone()).map_err(to_py_err)
    }

    fn create_checkerboard_pattern(
        &mut self,
        cell_size: f64,
        color1: [f64; 3],
        color2: [f64; 3],
    ) -> PyResult<String> {
        self.inner
            .create_checkerboard_pattern(cell_size, color1, color2)
            .map_err(to_py_err)
    }

    fn create_stripe_pattern(
        &mut self,
        stripe_width: f64,
        angle: f64,
        color1: [f64; 3],
        color2: [f64; 3],
    ) -> PyResult<String> {
        self.inner
            .create_stripe_pattern(stripe_width, angle, color1, color2)
            .map_err(to_py_err)
    }

    fn create_dots_pattern(
        &mut self,
        dot_radius: f64,
        spacing: f64,
        dot_color: [f64; 3],
        background_color: [f64; 3],
    ) -> PyResult<String> {
        self.inner
            .create_dots_pattern(dot_radius, spacing, dot_color, background_color)
            .map_err(to_py_err)
    }

    fn count(&self) -> usize {
        self.inner.count()
    }

    fn clear(&mut self) {
        self.inner.clear();
    }

    fn __repr__(&self) -> String {
        format!("PatternManager(count={})", self.inner.count())
    }
}

// ── FormXObject ───────────────────────────────────────────────────────────

#[pyclass(name = "FormXObject", from_py_object)]
#[derive(Clone)]
pub struct PyFormXObject {
    pub inner: FormXObject,
}

#[pymethods]
impl PyFormXObject {
    #[new]
    fn new(bbox: &PyRectangle) -> Self {
        Self { inner: FormXObject::new(bbox.inner) }
    }

    fn with_matrix(&self, matrix: [f64; 6]) -> Self {
        Self { inner: self.inner.clone().with_matrix(matrix) }
    }

    fn with_content(&self, content: Vec<u8>) -> Self {
        Self { inner: self.inner.clone().with_content(content) }
    }

    #[staticmethod]
    fn from_graphics_ops(bbox: &PyRectangle, ops: &str) -> Self {
        Self { inner: FormXObject::from_graphics_ops(bbox.inner, ops) }
    }

    fn has_transparency(&self) -> bool {
        self.inner.has_transparency()
    }

    fn __repr__(&self) -> String {
        format!(
            "FormXObject(bbox=({}, {}, {}, {}))",
            self.inner.bbox.lower_left.x,
            self.inner.bbox.lower_left.y,
            self.inner.bbox.upper_right.x,
            self.inner.bbox.upper_right.y,
        )
    }
}

// ── FormXObjectBuilder ────────────────────────────────────────────────────

#[pyclass(name = "FormXObjectBuilder")]
pub struct PyFormXObjectBuilder {
    inner: Option<FormXObjectBuilder>,
}

#[pymethods]
impl PyFormXObjectBuilder {
    #[new]
    fn new(bbox: &PyRectangle) -> Self {
        Self { inner: Some(FormXObjectBuilder::new(bbox.inner)) }
    }

    fn matrix(&mut self, matrix: [f64; 6]) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.matrix(matrix));
        }
    }

    fn rectangle(&mut self, x: f64, y: f64, width: f64, height: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.rectangle(x, y, width, height));
        }
    }

    fn move_to(&mut self, x: f64, y: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.move_to(x, y));
        }
    }

    fn line_to(&mut self, x: f64, y: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.line_to(x, y));
        }
    }

    fn fill_color(&mut self, r: f64, g: f64, b: f64) {
        if let Some(builder) = self.inner.take() {
            self.inner = Some(builder.fill_color(r, g, b));
        }
    }

    fn stroke_color(&mut self, r: f64, g: f64, b: f64) {
        if let Some(builder) = self.inner.take() {
            self.inner = Some(builder.stroke_color(r, g, b));
        }
    }

    fn fill(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.fill());
        }
    }

    fn stroke(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.stroke());
        }
    }

    fn fill_stroke(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.fill_stroke());
        }
    }

    fn save_state(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.save_state());
        }
    }

    fn restore_state(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.restore_state());
        }
    }

    fn transparency_group(&mut self, isolated: bool, knockout: bool) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.transparency_group(isolated, knockout));
        }
    }

    fn build(&mut self) -> PyResult<PyFormXObject> {
        let b = self.inner.take().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("FormXObjectBuilder already consumed")
        })?;
        Ok(PyFormXObject { inner: b.build() })
    }

    fn __repr__(&self) -> String {
        if self.inner.is_some() {
            "FormXObjectBuilder(active)".to_string()
        } else {
            "FormXObjectBuilder(consumed)".to_string()
        }
    }
}

// ── FormTemplates ─────────────────────────────────────────────────────────

#[pyclass(name = "FormTemplates")]
pub struct PyFormTemplates;

#[pymethods]
impl PyFormTemplates {
    #[staticmethod]
    fn checkmark(size: f64) -> PyFormXObject {
        PyFormXObject { inner: FormTemplates::checkmark(size) }
    }

    #[staticmethod]
    fn cross(size: f64) -> PyFormXObject {
        PyFormXObject { inner: FormTemplates::cross(size) }
    }

    #[staticmethod]
    fn circle(radius: f64, filled: bool) -> PyFormXObject {
        PyFormXObject { inner: FormTemplates::circle(radius, filled) }
    }

    #[staticmethod]
    fn star(size: f64, points: usize) -> PyFormXObject {
        PyFormXObject { inner: FormTemplates::star(size, points) }
    }

    #[staticmethod]
    fn logo_placeholder(width: f64, height: f64) -> PyFormXObject {
        PyFormXObject { inner: FormTemplates::logo_placeholder(width, height) }
    }
}

// ── FormXObjectManager ────────────────────────────────────────────────────

#[pyclass(name = "FormXObjectManager")]
pub struct PyFormXObjectManager {
    inner: FormXObjectManager,
}

#[pymethods]
impl PyFormXObjectManager {
    #[new]
    fn new() -> Self {
        Self { inner: FormXObjectManager::new() }
    }

    fn add_form(&mut self, name: Option<String>, form: &PyFormXObject) -> String {
        self.inner.add_form(name, form.inner.clone())
    }

    fn get_form(&self, name: &str) -> Option<PyFormXObject> {
        self.inner.get_form(name).map(|f| PyFormXObject { inner: f.clone() })
    }

    fn remove_form(&mut self, name: &str) -> bool {
        self.inner.remove_form(name).is_some()
    }

    fn clear(&mut self) {
        self.inner.clear();
    }

    fn count(&self) -> usize {
        self.inner.get_all_forms().len()
    }

    fn __repr__(&self) -> String {
        format!("FormXObjectManager(count={})", self.inner.get_all_forms().len())
    }
}

// ── ExtGState ─────────────────────────────────────────────────────────────

#[pyclass(name = "ExtGState", from_py_object)]
#[derive(Clone)]
pub struct PyExtGState {
    pub inner: ExtGState,
}

#[pymethods]
impl PyExtGState {
    #[new]
    fn new() -> Self {
        Self { inner: ExtGState::new() }
    }

    fn with_line_width(&self, width: f64) -> Self {
        Self { inner: self.inner.clone().with_line_width(width) }
    }

    fn with_line_cap(&self, cap: &crate::graphics::PyLineCap) -> Self {
        Self { inner: self.inner.clone().with_line_cap(cap.inner) }
    }

    fn with_line_join(&self, join: &crate::graphics::PyLineJoin) -> Self {
        Self { inner: self.inner.clone().with_line_join(join.inner) }
    }

    fn with_miter_limit(&self, limit: f64) -> Self {
        Self { inner: self.inner.clone().with_miter_limit(limit) }
    }

    fn with_blend_mode(&self, mode: &crate::graphics::PyBlendMode) -> Self {
        Self { inner: self.inner.clone().with_blend_mode(mode.inner.clone()) }
    }

    fn with_alpha_stroke(&self, alpha: f64) -> Self {
        Self { inner: self.inner.clone().with_alpha_stroke(alpha) }
    }

    fn with_alpha_fill(&self, alpha: f64) -> Self {
        Self { inner: self.inner.clone().with_alpha_fill(alpha) }
    }

    fn with_alpha(&self, alpha: f64) -> Self {
        Self { inner: self.inner.clone().with_alpha(alpha) }
    }

    fn with_rendering_intent(&self, intent: &PyRenderingIntent) -> Self {
        Self { inner: self.inner.clone().with_rendering_intent(intent.inner) }
    }

    fn with_overprint_stroke(&self, overprint: bool) -> Self {
        Self { inner: self.inner.clone().with_overprint_stroke(overprint) }
    }

    fn with_overprint_fill(&self, overprint: bool) -> Self {
        Self { inner: self.inner.clone().with_overprint_fill(overprint) }
    }

    fn with_flatness(&self, flatness: f64) -> Self {
        Self { inner: self.inner.clone().with_flatness(flatness) }
    }

    fn with_smoothness(&self, smoothness: f64) -> Self {
        Self { inner: self.inner.clone().with_smoothness(smoothness) }
    }

    fn with_text_knockout(&self, knockout: bool) -> Self {
        Self { inner: self.inner.clone().with_text_knockout(knockout) }
    }

    fn uses_transparency(&self) -> bool {
        self.inner.uses_transparency()
    }

    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    fn __repr__(&self) -> String {
        format!("ExtGState(empty={})", self.inner.is_empty())
    }
}

// ── ExtGStateManager ──────────────────────────────────────────────────────

#[pyclass(name = "ExtGStateManager")]
pub struct PyExtGStateManager {
    inner: ExtGStateManager,
}

#[pymethods]
impl PyExtGStateManager {
    #[new]
    fn new() -> Self {
        Self { inner: ExtGStateManager::new() }
    }

    fn add_state(&mut self, state: &PyExtGState) -> PyResult<String> {
        self.inner.add_state(state.inner.clone()).map_err(to_py_err)
    }

    fn count(&self) -> usize {
        self.inner.count()
    }

    fn clear(&mut self) {
        self.inner.clear();
    }

    fn __repr__(&self) -> String {
        format!("ExtGStateManager(count={})", self.inner.count())
    }
}

// ── SoftMask ──────────────────────────────────────────────────────────────

#[pyclass(name = "SoftMask", from_py_object)]
#[derive(Clone)]
pub struct PySoftMask {
    pub inner: SoftMask,
}

#[pymethods]
impl PySoftMask {
    #[staticmethod]
    fn none() -> Self {
        Self { inner: SoftMask::none() }
    }

    #[staticmethod]
    fn alpha(group_ref: &str) -> Self {
        Self { inner: SoftMask::alpha(group_ref.to_string()) }
    }

    #[staticmethod]
    fn luminosity(group_ref: &str) -> Self {
        Self { inner: SoftMask::luminosity(group_ref.to_string()) }
    }

    fn with_background_color(&self, color: Vec<f64>) -> Self {
        Self { inner: self.inner.clone().with_background_color(color) }
    }

    fn with_bbox(&self, bbox: [f64; 4]) -> Self {
        Self { inner: self.inner.clone().with_bbox(bbox) }
    }

    fn is_none(&self) -> bool {
        self.inner.is_none()
    }

    fn __repr__(&self) -> String {
        if self.inner.is_none() {
            "SoftMask.none()".to_string()
        } else {
            format!("SoftMask({:?})", self.inner.mask_type)
        }
    }
}

// ── SoftMaskState ─────────────────────────────────────────────────────────

#[pyclass(name = "SoftMaskState")]
pub struct PySoftMaskState {
    inner: SoftMaskState,
}

#[pymethods]
impl PySoftMaskState {
    #[new]
    fn new() -> Self {
        Self { inner: SoftMaskState::new() }
    }

    fn set_mask(&mut self, mask: &PySoftMask) {
        self.inner.set_mask(mask.inner.clone());
    }

    fn push_mask(&mut self, mask: &PySoftMask) {
        self.inner.push_mask(mask.inner.clone());
    }

    fn pop_mask(&mut self) -> Option<PySoftMask> {
        self.inner.pop_mask().map(|m| PySoftMask { inner: m })
    }

    fn clear(&mut self) {
        self.inner.clear();
    }

    fn is_active(&self) -> bool {
        self.inner.is_active()
    }

    fn __repr__(&self) -> String {
        format!("SoftMaskState(active={})", self.inner.is_active())
    }
}

// ── TransparencyGroup ─────────────────────────────────────────────────────

#[pyclass(name = "TransparencyGroup", from_py_object)]
#[derive(Clone)]
pub struct PyTransparencyGroup {
    pub inner: TransparencyGroup,
}

#[pymethods]
impl PyTransparencyGroup {
    #[new]
    fn new() -> Self {
        Self { inner: TransparencyGroup::new() }
    }

    #[staticmethod]
    fn isolated() -> Self {
        Self { inner: TransparencyGroup::isolated() }
    }

    #[staticmethod]
    fn knockout() -> Self {
        Self { inner: TransparencyGroup::knockout() }
    }

    fn with_isolated(&self, isolated: bool) -> Self {
        Self { inner: self.inner.clone().with_isolated(isolated) }
    }

    fn with_knockout(&self, knockout: bool) -> Self {
        Self { inner: self.inner.clone().with_knockout(knockout) }
    }

    fn with_blend_mode(&self, mode: &crate::graphics::PyBlendMode) -> Self {
        Self { inner: self.inner.clone().with_blend_mode(mode.inner.clone()) }
    }

    fn with_opacity(&self, opacity: f32) -> Self {
        Self { inner: self.inner.clone().with_opacity(opacity) }
    }

    fn with_color_space(&self, color_space: &str) -> Self {
        Self { inner: self.inner.clone().with_color_space(color_space) }
    }

    fn __repr__(&self) -> String {
        "TransparencyGroup(...)".to_string()
    }
}

// ── IccProfile ────────────────────────────────────────────────────────────

#[pyclass(name = "IccProfile", from_py_object)]
#[derive(Clone)]
pub struct PyIccProfile {
    pub inner: IccProfile,
}

#[pymethods]
impl PyIccProfile {
    #[new]
    fn new(name: &str, data: Vec<u8>, color_space: &PyIccColorSpace) -> Self {
        Self {
            inner: IccProfile::new(name.to_string(), data, color_space.inner),
        }
    }

    #[staticmethod]
    fn from_standard(profile: &PyStandardIccProfile) -> Self {
        Self { inner: IccProfile::from_standard(profile.inner) }
    }

    fn with_range(&self, range: Vec<f64>) -> Self {
        Self { inner: self.inner.clone().with_range(range) }
    }

    fn validate(&self) -> PyResult<()> {
        self.inner.validate().map_err(to_py_err)
    }

    fn size(&self) -> usize {
        self.inner.size()
    }

    fn is_rgb(&self) -> bool {
        self.inner.is_rgb()
    }

    fn is_cmyk(&self) -> bool {
        self.inner.is_cmyk()
    }

    fn is_gray(&self) -> bool {
        self.inner.is_gray()
    }

    #[getter]
    fn name(&self) -> &str {
        &self.inner.name
    }

    fn __repr__(&self) -> String {
        format!("IccProfile(name={:?})", self.inner.name)
    }
}

// ── IccProfileManager ─────────────────────────────────────────────────────

#[pyclass(name = "IccProfileManager")]
pub struct PyIccProfileManager {
    inner: IccProfileManager,
}

#[pymethods]
impl PyIccProfileManager {
    #[new]
    fn new() -> Self {
        Self { inner: IccProfileManager::new() }
    }

    fn add_profile(&mut self, profile: &PyIccProfile) -> PyResult<String> {
        self.inner.add_profile(profile.inner.clone()).map_err(to_py_err)
    }

    fn add_standard_profile(&mut self, profile: &PyStandardIccProfile) -> PyResult<String> {
        self.inner.add_standard_profile(profile.inner).map_err(to_py_err)
    }

    fn create_default_srgb(&mut self) -> PyResult<String> {
        self.inner.create_default_srgb().map_err(to_py_err)
    }

    fn create_default_cmyk(&mut self) -> PyResult<String> {
        self.inner.create_default_cmyk().map_err(to_py_err)
    }

    fn create_default_gray(&mut self) -> PyResult<String> {
        self.inner.create_default_gray().map_err(to_py_err)
    }

    fn count(&self) -> usize {
        self.inner.count()
    }

    fn clear(&mut self) {
        self.inner.clear();
    }

    fn __repr__(&self) -> String {
        format!("IccProfileManager(count={})", self.inner.count())
    }
}

// ── SeparationColorSpace ──────────────────────────────────────────────────

#[pyclass(name = "SeparationColorSpace", from_py_object)]
#[derive(Clone)]
pub struct PySeparationColorSpace {
    pub inner: SeparationColorSpace,
}

#[pymethods]
impl PySeparationColorSpace {
    #[staticmethod]
    fn rgb_separation(colorant_name: &str, r: f64, g: f64, b: f64) -> Self {
        Self {
            inner: SeparationColorSpace::rgb_separation(colorant_name, r, g, b),
        }
    }

    #[staticmethod]
    fn cmyk_separation(colorant_name: &str, c: f64, m: f64, y: f64, k: f64) -> Self {
        Self {
            inner: SeparationColorSpace::cmyk_separation(colorant_name, c, m, y, k),
        }
    }

    #[getter]
    fn colorant_name(&self) -> &str {
        &self.inner.colorant_name
    }

    fn apply_tint(&self, tint: f64) -> Vec<f64> {
        self.inner.apply_tint(tint)
    }

    fn __repr__(&self) -> String {
        format!("SeparationColorSpace(name={:?})", self.inner.colorant_name)
    }
}

// ── SeparationColor ───────────────────────────────────────────────────────

#[pyclass(name = "SeparationColor", from_py_object)]
#[derive(Clone)]
pub struct PySeparationColor {
    pub inner: SeparationColor,
}

#[pymethods]
impl PySeparationColor {
    #[new]
    fn new(color_space: &PySeparationColorSpace, tint: f64) -> Self {
        Self {
            inner: SeparationColor::new(color_space.inner.clone(), tint),
        }
    }

    fn to_rgb(&self) -> PyColor {
        PyColor { inner: self.inner.to_rgb() }
    }

    fn colorant_name(&self) -> &str {
        self.inner.colorant_name()
    }

    #[getter]
    fn tint(&self) -> f64 {
        self.inner.tint
    }

    fn __repr__(&self) -> String {
        format!(
            "SeparationColor(name={:?}, tint={})",
            self.inner.colorant_name(),
            self.inner.tint
        )
    }
}

// ── SpotColors ────────────────────────────────────────────────────────────

#[pyclass(name = "SpotColors")]
pub struct PySpotColors;

#[pymethods]
impl PySpotColors {
    #[staticmethod]
    fn pantone_185c() -> PySeparationColorSpace {
        PySeparationColorSpace { inner: SpotColors::pantone_185c() }
    }

    #[staticmethod]
    fn pantone_286c() -> PySeparationColorSpace {
        PySeparationColorSpace { inner: SpotColors::pantone_286c() }
    }

    #[staticmethod]
    fn pantone_376c() -> PySeparationColorSpace {
        PySeparationColorSpace { inner: SpotColors::pantone_376c() }
    }

    #[staticmethod]
    fn gold() -> PySeparationColorSpace {
        PySeparationColorSpace { inner: SpotColors::gold() }
    }

    #[staticmethod]
    fn silver() -> PySeparationColorSpace {
        PySeparationColorSpace { inner: SpotColors::silver() }
    }

    #[staticmethod]
    fn varnish() -> PySeparationColorSpace {
        PySeparationColorSpace { inner: SpotColors::varnish() }
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Enums
    m.add_class::<PyShadingType>()?;
    m.add_class::<PyPaintType>()?;
    m.add_class::<PyTilingType>()?;
    m.add_class::<PyRenderingIntent>()?;
    m.add_class::<PySoftMaskType>()?;
    m.add_class::<PyIccColorSpace>()?;
    m.add_class::<PyStandardIccProfile>()?;
    // Shadings (F65)
    m.add_class::<PyShadingPoint>()?;
    m.add_class::<PyColorStop>()?;
    m.add_class::<PyAxialShading>()?;
    m.add_class::<PyRadialShading>()?;
    m.add_class::<PyShadingManager>()?;
    // Patterns (F66)
    m.add_class::<PyPatternMatrix>()?;
    m.add_class::<PyTilingPattern>()?;
    m.add_class::<PyPatternManager>()?;
    // FormXObject (F67)
    m.add_class::<PyFormXObject>()?;
    m.add_class::<PyFormXObjectBuilder>()?;
    m.add_class::<PyFormTemplates>()?;
    m.add_class::<PyFormXObjectManager>()?;
    // ExtGState (F68)
    m.add_class::<PyExtGState>()?;
    m.add_class::<PyExtGStateManager>()?;
    // SoftMask + TransparencyGroup (F69)
    m.add_class::<PySoftMask>()?;
    m.add_class::<PySoftMaskState>()?;
    m.add_class::<PyTransparencyGroup>()?;
    // Color Spaces (F70)
    m.add_class::<PyIccProfile>()?;
    m.add_class::<PyIccProfileManager>()?;
    m.add_class::<PySeparationColorSpace>()?;
    m.add_class::<PySeparationColor>()?;
    m.add_class::<PySpotColors>()?;
    Ok(())
}
