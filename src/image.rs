use oxidize_pdf::graphics::{ColorSpace, ImageFormat};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

use crate::errors::to_py_err;

#[pyclass(name = "ImageColorSpace", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyImageColorSpace {
    DeviceGray,
    DeviceRGB,
    DeviceCMYK,
}
impl PyImageColorSpace {
    fn channels(self) -> usize {
        match self {
            Self::DeviceGray => 1,
            Self::DeviceRGB => 3,
            Self::DeviceCMYK => 4,
        }
    }
    fn core(self) -> ColorSpace {
        match self {
            Self::DeviceGray => ColorSpace::DeviceGray,
            Self::DeviceRGB => ColorSpace::DeviceRGB,
            Self::DeviceCMYK => ColorSpace::DeviceCMYK,
        }
    }
}
#[pyclass(name = "ImageFormat", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyImageFormat {
    Jpeg,
    Png,
    Tiff,
    Raw,
}
impl From<ImageFormat> for PyImageFormat {
    fn from(value: ImageFormat) -> Self {
        match value {
            ImageFormat::Jpeg => Self::Jpeg,
            ImageFormat::Png => Self::Png,
            ImageFormat::Tiff => Self::Tiff,
            ImageFormat::Raw => Self::Raw,
        }
    }
}
/// Validate byte-aligned PDF scanlines before copying input or calling core.
fn validate_pixels(
    length: usize,
    width: u32,
    height: u32,
    channels: usize,
    bits: u8,
) -> PyResult<()> {
    if width == 0 || height == 0 {
        return Err(PyValueError::new_err("image dimensions must be positive"));
    }
    if !matches!(bits, 1 | 2 | 4 | 8 | 16) {
        return Err(PyValueError::new_err(
            "bits_per_component must be 1, 2, 4, 8, or 16",
        ));
    }
    let expected = (width as usize)
        .checked_mul(channels)
        .and_then(|v| v.checked_mul(usize::from(bits)))
        .and_then(|v| v.checked_add(7))
        .map(|v| v / 8)
        .and_then(|v| v.checked_mul(height as usize))
        .ok_or_else(|| PyValueError::new_err("image dimensions exceed addressable buffer size"))?;
    if length != expected {
        return Err(PyValueError::new_err(format!(
            "pixel data size does not match dimensions: expected {expected} bytes, got {length}"
        )));
    }
    Ok(())
}
/// These core constructors multiply dimensions using u32 internally.
fn validate_core_dimensions(width: u32, height: u32, channels: u32) -> PyResult<()> {
    width
        .checked_mul(height)
        .and_then(|v| v.checked_mul(channels))
        .ok_or_else(|| {
            PyValueError::new_err("image dimensions exceed the core constructor limit")
        })?;
    Ok(())
}

#[pyclass(name = "Image", from_py_object)]
#[derive(Clone)]
pub struct PyImage {
    pub inner: oxidize_pdf::Image,
}

#[pymethods]
impl PyImage {
    /// Construct packed PDF scanlines, each padded to a byte boundary.
    #[staticmethod]
    #[pyo3(signature=(data,width,height,color_space,bits_per_component=8))]
    fn from_raw_data(
        data: &[u8],
        width: u32,
        height: u32,
        color_space: PyImageColorSpace,
        bits_per_component: u8,
    ) -> PyResult<Self> {
        validate_pixels(
            data.len(),
            width,
            height,
            color_space.channels(),
            bits_per_component,
        )?;
        Ok(Self {
            inner: oxidize_pdf::Image::from_raw_data(
                data.to_vec(),
                width,
                height,
                color_space.core(),
                bits_per_component,
            ),
        })
    }
    #[staticmethod]
    fn from_rgba_data(py: Python<'_>, rgba_data: &[u8], width: u32, height: u32) -> PyResult<Self> {
        validate_core_dimensions(width, height, 4)?;
        validate_pixels(rgba_data.len(), width, height, 4, 8)?;
        let data = rgba_data.to_vec();
        let inner = py
            .detach(|| oxidize_pdf::Image::from_rgba_data(data, width, height))
            .map_err(to_py_err)?;
        Ok(Self { inner })
    }
    #[staticmethod]
    fn from_gray_data(gray_data: &[u8], width: u32, height: u32) -> PyResult<Self> {
        validate_core_dimensions(width, height, 1)?;
        validate_pixels(gray_data.len(), width, height, 1, 8)?;
        let inner = oxidize_pdf::Image::from_gray_data(gray_data.to_vec(), width, height)
            .map_err(to_py_err)?;
        Ok(Self { inner })
    }
    #[getter]
    fn data<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, self.inner.data())
    }
    #[getter]
    fn format(&self) -> PyImageFormat {
        self.inner.format().into()
    }
    #[getter]
    fn bits_per_component(&self) -> u8 {
        self.inner.bits_per_component()
    }
    #[getter]
    fn alpha_data<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyBytes>> {
        self.inner.alpha_data().map(|data| PyBytes::new(py, data))
    }
    #[getter]
    fn soft_mask(&self) -> Option<Self> {
        self.inner.soft_mask().cloned().map(|inner| Self { inner })
    }

    #[staticmethod]
    fn from_jpeg_data(data: &[u8]) -> PyResult<Self> {
        let img = oxidize_pdf::Image::from_jpeg_data(data.to_vec()).map_err(to_py_err)?;
        Ok(Self { inner: img })
    }

    #[staticmethod]
    fn from_png_data(data: &[u8]) -> PyResult<Self> {
        let img = oxidize_pdf::Image::from_png_data(data.to_vec()).map_err(to_py_err)?;
        Ok(Self { inner: img })
    }

    #[staticmethod]
    fn from_tiff_data(data: &[u8]) -> PyResult<Self> {
        let img = oxidize_pdf::Image::from_tiff_data(data.to_vec()).map_err(to_py_err)?;
        Ok(Self { inner: img })
    }

    #[staticmethod]
    fn from_jpeg_file(path: &str) -> PyResult<Self> {
        let img = oxidize_pdf::Image::from_jpeg_file(path).map_err(to_py_err)?;
        Ok(Self { inner: img })
    }

    #[staticmethod]
    fn from_png_file(path: &str) -> PyResult<Self> {
        let img = oxidize_pdf::Image::from_png_file(path).map_err(to_py_err)?;
        Ok(Self { inner: img })
    }

    #[staticmethod]
    fn from_tiff_file(path: &str) -> PyResult<Self> {
        let img = oxidize_pdf::Image::from_tiff_file(path).map_err(to_py_err)?;
        Ok(Self { inner: img })
    }

    /// Auto-detect format from file extension.
    #[staticmethod]
    fn from_file(path: &str) -> PyResult<Self> {
        let ext = std::path::Path::new(path)
            .extension()
            .and_then(|e| e.to_str())
            .unwrap_or("")
            .to_lowercase();
        let img = match ext.as_str() {
            "jpg" | "jpeg" => oxidize_pdf::Image::from_jpeg_file(path),
            "png" => oxidize_pdf::Image::from_png_file(path),
            "tif" | "tiff" => oxidize_pdf::Image::from_tiff_file(path),
            _ => {
                return Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Unsupported image format: .{ext}. Use from_jpeg_file, from_png_file, or from_tiff_file."
                )));
            }
        }
        .map_err(to_py_err)?;
        Ok(Self { inner: img })
    }

    #[getter]
    fn width(&self) -> u32 {
        self.inner.width()
    }

    #[getter]
    fn height(&self) -> u32 {
        self.inner.height()
    }

    #[getter]
    fn has_transparency(&self) -> bool {
        self.inner.has_transparency()
    }

    fn __repr__(&self) -> String {
        format!(
            "Image({}x{}, transparency={})",
            self.inner.width(),
            self.inner.height(),
            self.inner.has_transparency()
        )
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyImageColorSpace>()?;
    m.add_class::<PyImageFormat>()?;
    m.add_class::<PyImage>()?;
    Ok(())
}
