use pyo3::prelude::*;

use crate::errors::to_py_err;

#[pyclass(name = "Image", from_py_object)]
#[derive(Clone)]
pub struct PyImage {
    pub inner: oxidize_pdf::Image,
}

#[pymethods]
impl PyImage {
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
    m.add_class::<PyImage>()?;
    Ok(())
}
