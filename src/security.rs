use pyo3::prelude::*;

use oxidize_pdf::signatures::{
    ByteRange, SignatureField, ParsedSignature, TrustStore,
    HashVerificationResult, SignatureVerificationResult,
    CertificateValidationResult, FullSignatureValidationResult,
    DigestAlgorithm, SignatureAlgorithm,
    parse_pkcs7_signature, compute_pdf_hash, verify_signature,
    validate_certificate,
};

/// PDF document permissions.
///
/// Controls what operations are allowed on an encrypted PDF.
///
/// Example::
///
///     perms = Permissions(print=True, copy=False)
///     doc.encrypt("user", "owner", permissions=perms)
#[pyclass(name = "Permissions", from_py_object)]
#[derive(Clone)]
pub struct PyPermissions {
    pub inner: oxidize_pdf::encryption::Permissions,
}

#[pymethods]
impl PyPermissions {
    #[new]
    #[pyo3(signature = (
        print = false,
        copy = false,
        modify_contents = false,
        modify_annotations = false,
        fill_forms = false,
        accessibility = true,
        assemble = false,
        print_high_quality = false,
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        print: bool,
        copy: bool,
        modify_contents: bool,
        modify_annotations: bool,
        fill_forms: bool,
        accessibility: bool,
        assemble: bool,
        print_high_quality: bool,
    ) -> Self {
        let mut perms = oxidize_pdf::encryption::Permissions::new();
        perms.set_print(print);
        perms.set_copy(copy);
        perms.set_modify_contents(modify_contents);
        perms.set_modify_annotations(modify_annotations);
        perms.set_fill_forms(fill_forms);
        perms.set_accessibility(accessibility);
        perms.set_assemble(assemble);
        perms.set_print_high_quality(print_high_quality);
        Self { inner: perms }
    }

    /// Create permissions with everything allowed.
    #[staticmethod]
    fn all() -> Self {
        Self {
            inner: oxidize_pdf::encryption::Permissions::all(),
        }
    }

    /// Create permissions with everything denied (except accessibility).
    #[staticmethod]
    fn none() -> Self {
        Self {
            inner: oxidize_pdf::encryption::Permissions::new(),
        }
    }

    #[getter]
    fn can_print(&self) -> bool {
        self.inner.can_print()
    }

    #[getter]
    fn can_copy(&self) -> bool {
        self.inner.can_copy()
    }

    #[getter]
    fn can_modify_contents(&self) -> bool {
        self.inner.can_modify_contents()
    }

    #[getter]
    fn can_modify_annotations(&self) -> bool {
        self.inner.can_modify_annotations()
    }

    #[getter]
    fn can_fill_forms(&self) -> bool {
        self.inner.can_fill_forms()
    }

    #[getter]
    fn can_assemble(&self) -> bool {
        self.inner.can_assemble()
    }

    #[getter]
    fn can_print_high_quality(&self) -> bool {
        self.inner.can_print_high_quality()
    }

    fn __repr__(&self) -> String {
        let flags: Vec<&str> = [
            (self.inner.can_print(), "print"),
            (self.inner.can_copy(), "copy"),
            (self.inner.can_modify_contents(), "modify_contents"),
            (self.inner.can_modify_annotations(), "modify_annotations"),
            (self.inner.can_fill_forms(), "fill_forms"),
            (self.inner.can_assemble(), "assemble"),
            (self.inner.can_print_high_quality(), "print_high_quality"),
        ]
        .into_iter()
        .filter(|(allowed, _)| *allowed)
        .map(|(_, name)| name)
        .collect();

        if flags.is_empty() {
            "Permissions(none)".to_string()
        } else {
            format!("Permissions({})", flags.join(", "))
        }
    }
}

// ── EncryptionStrength ─────────────────────────────────────────────────────

#[pyclass(name = "EncryptionStrength", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyEncryptionStrength {
    pub inner: oxidize_pdf::document::EncryptionStrength,
}

#[pymethods]
impl PyEncryptionStrength {
    #[classattr]
    const RC4_40: PyEncryptionStrength = PyEncryptionStrength {
        inner: oxidize_pdf::document::EncryptionStrength::Rc4_40bit,
    };
    #[classattr]
    const RC4_128: PyEncryptionStrength = PyEncryptionStrength {
        inner: oxidize_pdf::document::EncryptionStrength::Rc4_128bit,
    };
    #[classattr]
    const AES_128: PyEncryptionStrength = PyEncryptionStrength {
        inner: oxidize_pdf::document::EncryptionStrength::Aes128,
    };
    #[classattr]
    const AES_256: PyEncryptionStrength = PyEncryptionStrength {
        inner: oxidize_pdf::document::EncryptionStrength::Aes256,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            oxidize_pdf::document::EncryptionStrength::Rc4_40bit => "RC4_40",
            oxidize_pdf::document::EncryptionStrength::Rc4_128bit => "RC4_128",
            oxidize_pdf::document::EncryptionStrength::Aes128 => "AES_128",
            oxidize_pdf::document::EncryptionStrength::Aes256 => "AES_256",
        };
        format!("EncryptionStrength.{name}")
    }
}

// ── Recipient (Feature 29) ────────────────────────────────────────────────

#[pyclass(name = "Recipient", from_py_object)]
#[derive(Clone)]
pub struct PyRecipient {
    pub inner: oxidize_pdf::encryption::Recipient,
}

#[pymethods]
impl PyRecipient {
    #[staticmethod]
    fn from_certificate(cert_data: &[u8]) -> PyResult<Self> {
        const MIN_CERT_LEN: usize = 64;
        if cert_data.len() < MIN_CERT_LEN {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Invalid certificate data: too short ({} bytes, minimum {MIN_CERT_LEN})",
                cert_data.len()
            )));
        }
        if cert_data[0] != 0x30 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid certificate data: not a valid DER-encoded X.509 certificate",
            ));
        }
        Ok(Self {
            inner: oxidize_pdf::encryption::Recipient {
                certificate: cert_data.to_vec(),
                permissions: oxidize_pdf::encryption::Permissions::all(),
                encrypted_seed: Vec::new(),
            },
        })
    }

    fn __repr__(&self) -> String {
        format!("Recipient(cert_len={})", self.inner.certificate.len())
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// F75 — Signatures Deep
// ═══════════════════════════════════════════════════════════════════════════════

// ── DigestAlgorithm ──────────────────────────────────────────────────────

#[pyclass(name = "DigestAlgorithm", frozen, eq)]
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct PyDigestAlgorithm {
    pub inner: DigestAlgorithm,
}

#[pymethods]
impl PyDigestAlgorithm {
    #[classattr]
    const SHA256: Self = Self { inner: DigestAlgorithm::Sha256 };
    #[classattr]
    const SHA384: Self = Self { inner: DigestAlgorithm::Sha384 };
    #[classattr]
    const SHA512: Self = Self { inner: DigestAlgorithm::Sha512 };

    #[getter]
    fn name(&self) -> &str { self.inner.name() }

    #[getter]
    fn oid(&self) -> &str { self.inner.oid() }

    fn __repr__(&self) -> String {
        format!("DigestAlgorithm.{}", self.inner.name())
    }
}

// ── SignatureAlgorithm ───────────────────────────────────────────────────

#[pyclass(name = "SignatureAlgorithm", frozen, eq)]
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct PySignatureAlgorithm {
    pub inner: SignatureAlgorithm,
}

#[pymethods]
impl PySignatureAlgorithm {
    #[classattr]
    const RSA_SHA256: Self = Self { inner: SignatureAlgorithm::RsaSha256 };
    #[classattr]
    const RSA_SHA384: Self = Self { inner: SignatureAlgorithm::RsaSha384 };
    #[classattr]
    const RSA_SHA512: Self = Self { inner: SignatureAlgorithm::RsaSha512 };
    #[classattr]
    const ECDSA_SHA256: Self = Self { inner: SignatureAlgorithm::EcdsaSha256 };
    #[classattr]
    const ECDSA_SHA384: Self = Self { inner: SignatureAlgorithm::EcdsaSha384 };

    #[getter]
    fn name(&self) -> &str { self.inner.name() }

    #[getter]
    fn digest_algorithm(&self) -> PyDigestAlgorithm {
        PyDigestAlgorithm { inner: self.inner.digest_algorithm() }
    }

    fn __repr__(&self) -> String {
        format!("SignatureAlgorithm.{}", self.inner.name())
    }
}

// ── ByteRange ────────────────────────────────────────────────────────────

#[pyclass(name = "ByteRange")]
#[derive(Clone)]
pub struct PyByteRange {
    pub inner: ByteRange,
}

#[pymethods]
impl PyByteRange {
    #[new]
    fn new(ranges: Vec<(u64, u64)>) -> Self {
        Self { inner: ByteRange::new(ranges) }
    }

    #[staticmethod]
    fn from_array(values: Vec<i64>) -> PyResult<Self> {
        ByteRange::from_array(&values)
            .map(|br| Self { inner: br })
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))
    }

    #[getter]
    fn ranges(&self) -> Vec<(u64, u64)> {
        self.inner.ranges().to_vec()
    }

    #[getter]
    fn total_bytes(&self) -> u64 {
        self.inner.total_bytes()
    }

    #[getter]
    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    fn __len__(&self) -> usize {
        self.inner.len()
    }

    fn validate(&self) -> PyResult<bool> {
        match self.inner.validate() {
            Ok(()) => Ok(true),
            Err(e) => Err(pyo3::exceptions::PyValueError::new_err(e)),
        }
    }

    fn __repr__(&self) -> String {
        format!("ByteRange(ranges={}, total_bytes={})", self.inner.len(), self.inner.total_bytes())
    }
}

// ── SignatureField ───────────────────────────────────────────────────────

#[pyclass(name = "SignatureField")]
#[derive(Clone)]
pub struct PySignatureField {
    pub inner: SignatureField,
}

#[pymethods]
impl PySignatureField {
    #[new]
    fn new(filter: &str, byte_range: &PyByteRange, contents: Vec<u8>) -> Self {
        Self {
            inner: SignatureField::new(
                filter.to_string(),
                byte_range.inner.clone(),
                contents,
            ),
        }
    }

    #[getter]
    fn filter(&self) -> &str { &self.inner.filter }

    #[getter]
    fn name(&self) -> Option<&str> { self.inner.name.as_deref() }

    #[getter]
    fn sub_filter(&self) -> Option<&str> { self.inner.sub_filter.as_deref() }

    #[getter]
    fn reason(&self) -> Option<&str> { self.inner.reason.as_deref() }

    #[getter]
    fn location(&self) -> Option<&str> { self.inner.location.as_deref() }

    #[getter]
    fn contact_info(&self) -> Option<&str> { self.inner.contact_info.as_deref() }

    #[getter]
    fn signing_time(&self) -> Option<&str> { self.inner.signing_time.as_deref() }

    #[getter]
    fn is_pkcs7_detached(&self) -> bool { self.inner.is_pkcs7_detached() }

    #[getter]
    fn is_pades(&self) -> bool { self.inner.is_pades() }

    #[getter]
    fn contents_size(&self) -> usize { self.inner.contents_size() }

    #[getter]
    fn byte_range(&self) -> PyByteRange {
        PyByteRange { inner: self.inner.byte_range.clone() }
    }

    fn __repr__(&self) -> String {
        format!("SignatureField(filter={:?}, contents_size={})",
            self.inner.filter, self.inner.contents_size())
    }
}

// ── TrustStore ───────────────────────────────────────────────────────────

#[pyclass(name = "TrustStore")]
#[derive(Clone)]
pub struct PyTrustStore {
    pub inner: TrustStore,
}

#[pymethods]
impl PyTrustStore {
    #[staticmethod]
    fn mozilla_roots() -> Self {
        Self { inner: TrustStore::mozilla_roots() }
    }

    #[staticmethod]
    fn empty() -> Self {
        Self { inner: TrustStore::empty() }
    }

    #[getter]
    fn root_count(&self) -> usize { self.inner.root_count() }

    #[getter]
    fn is_mozilla_bundle(&self) -> bool { self.inner.is_mozilla_bundle() }

    fn __repr__(&self) -> String {
        format!("TrustStore(roots={}, mozilla={})", self.inner.root_count(), self.inner.is_mozilla_bundle())
    }
}

// ── ParsedSignature ──────────────────────────────────────────────────────

#[pyclass(name = "ParsedSignature")]
#[derive(Clone)]
pub struct PyParsedSignature {
    pub inner: ParsedSignature,
}

#[pymethods]
impl PyParsedSignature {
    #[getter]
    fn digest_algorithm(&self) -> PyDigestAlgorithm {
        PyDigestAlgorithm { inner: self.inner.digest_algorithm }
    }

    #[getter]
    fn signature_algorithm(&self) -> PySignatureAlgorithm {
        PySignatureAlgorithm { inner: self.inner.signature_algorithm }
    }

    #[getter]
    fn signature_value(&self) -> &[u8] { &self.inner.signature_value }

    #[getter]
    fn signer_certificate_der(&self) -> &[u8] { &self.inner.signer_certificate_der }

    #[getter]
    fn signing_time(&self) -> Option<&str> { self.inner.signing_time.as_deref() }

    fn __repr__(&self) -> String {
        format!("ParsedSignature(algo={:?})", self.inner.signature_algorithm.name())
    }
}

// ── HashVerificationResult ───────────────────────────────────────────────

#[pyclass(name = "HashVerificationResult")]
#[derive(Clone)]
pub struct PyHashVerificationResult {
    pub inner: HashVerificationResult,
}

#[pymethods]
impl PyHashVerificationResult {
    #[getter]
    fn computed_hash(&self) -> &[u8] { &self.inner.computed_hash }

    #[getter]
    fn algorithm(&self) -> PyDigestAlgorithm {
        PyDigestAlgorithm { inner: self.inner.algorithm }
    }

    #[getter]
    fn bytes_hashed(&self) -> u64 { self.inner.bytes_hashed }

    fn hash_hex(&self) -> String { self.inner.hash_hex() }

    fn __repr__(&self) -> String {
        format!("HashVerificationResult(algo={:?}, bytes={})",
            self.inner.algorithm.name(), self.inner.bytes_hashed)
    }
}

// ── SignatureVerificationResult ──────────────────────────────────────────

#[pyclass(name = "SignatureVerificationResult")]
#[derive(Clone)]
pub struct PySignatureVerificationResult {
    pub inner: SignatureVerificationResult,
}

#[pymethods]
impl PySignatureVerificationResult {
    #[getter]
    fn hash_valid(&self) -> bool { self.inner.hash_valid }

    #[getter]
    fn signature_valid(&self) -> bool { self.inner.signature_valid }

    #[getter]
    fn digest_algorithm(&self) -> PyDigestAlgorithm {
        PyDigestAlgorithm { inner: self.inner.digest_algorithm }
    }

    #[getter]
    fn signature_algorithm(&self) -> PySignatureAlgorithm {
        PySignatureAlgorithm { inner: self.inner.signature_algorithm }
    }

    #[getter]
    fn details(&self) -> Option<&str> { self.inner.details.as_deref() }

    fn is_valid(&self) -> bool { self.inner.is_valid() }

    fn __repr__(&self) -> String {
        format!("SignatureVerificationResult(valid={})", self.inner.is_valid())
    }
}

// ── CertificateValidationResult ──────────────────────────────────────────

#[pyclass(name = "CertificateValidationResult")]
#[derive(Clone)]
pub struct PyCertificateValidationResult {
    pub inner: CertificateValidationResult,
}

#[pymethods]
impl PyCertificateValidationResult {
    #[getter]
    fn subject(&self) -> &str { &self.inner.subject }

    #[getter]
    fn issuer(&self) -> &str { &self.inner.issuer }

    #[getter]
    fn valid_from(&self) -> &str { &self.inner.valid_from }

    #[getter]
    fn valid_to(&self) -> &str { &self.inner.valid_to }

    #[getter]
    fn is_time_valid(&self) -> bool { self.inner.is_time_valid }

    #[getter]
    fn is_trusted(&self) -> bool { self.inner.is_trusted }

    #[getter]
    fn is_signature_capable(&self) -> bool { self.inner.is_signature_capable }

    #[getter]
    fn warnings(&self) -> Vec<String> { self.inner.warnings.clone() }

    fn is_valid(&self) -> bool { self.inner.is_valid() }

    fn has_warnings(&self) -> bool { self.inner.has_warnings() }

    fn __repr__(&self) -> String {
        format!("CertificateValidationResult(subject={:?}, valid={})",
            self.inner.subject, self.inner.is_valid())
    }
}

// ── FullSignatureValidationResult ────────────────────────────────────────

#[pyclass(name = "FullSignatureValidationResult")]
#[derive(Clone)]
pub struct PyFullSignatureValidationResult {
    pub inner: FullSignatureValidationResult,
}

#[pymethods]
impl PyFullSignatureValidationResult {
    #[getter]
    fn field(&self) -> PySignatureField {
        PySignatureField { inner: self.inner.field.clone() }
    }

    #[getter]
    fn signer_name(&self) -> &str { self.inner.signer_name() }

    #[getter]
    fn signing_time(&self) -> Option<&str> { self.inner.signing_time.as_deref() }

    #[getter]
    fn hash_valid(&self) -> bool { self.inner.hash_valid }

    #[getter]
    fn signature_valid(&self) -> bool { self.inner.signature_valid }

    #[getter]
    fn certificate_result(&self) -> Option<PyCertificateValidationResult> {
        self.inner.certificate_result.as_ref().map(|cr| PyCertificateValidationResult { inner: cr.clone() })
    }

    #[getter]
    fn has_modifications_after_signing(&self) -> bool { self.inner.has_modifications_after_signing }

    #[getter]
    fn errors(&self) -> Vec<String> { self.inner.errors.clone() }

    #[getter]
    fn warnings(&self) -> Vec<String> { self.inner.warnings.clone() }

    fn is_valid(&self) -> bool { self.inner.is_valid() }

    fn has_warnings(&self) -> bool { self.inner.has_warnings() }

    fn __repr__(&self) -> String {
        format!("FullSignatureValidationResult(signer={:?}, valid={})",
            self.inner.signer_name(), self.inner.is_valid())
    }
}

// ── Standalone Functions ─────────────────────────────────────────────────

fn sig_err_to_py(e: oxidize_pdf::signatures::SignatureError) -> PyErr {
    use oxidize_pdf::signatures::SignatureError;
    let msg = e.to_string();
    match e {
        // Input validation errors → ValueError
        SignatureError::MissingField { .. }
        | SignatureError::InvalidByteRange { .. }
        | SignatureError::InvalidSignatureDict { .. }
        | SignatureError::AcroFormNotFound
        | SignatureError::NoSignatureFields
        | SignatureError::ByteRangeExceedsDocument { .. }
        | SignatureError::UnsupportedAlgorithm { .. } => {
            pyo3::exceptions::PyValueError::new_err(msg)
        }
        // Processing/crypto failures → RuntimeError
        SignatureError::ContentsExtractionFailed { .. }
        | SignatureError::ParseError { .. }
        | SignatureError::CmsParsingFailed { .. }
        | SignatureError::HashVerificationFailed { .. }
        | SignatureError::SignatureVerificationFailed { .. }
        | SignatureError::CertificateExtractionFailed { .. }
        | SignatureError::CertificateValidationFailed { .. } => {
            pyo3::exceptions::PyRuntimeError::new_err(msg)
        }
    }
}

#[pyfunction]
fn compute_pdf_hash_py(
    pdf_bytes: &[u8],
    byte_range: &PyByteRange,
    algorithm: &PyDigestAlgorithm,
) -> PyResult<PyHashVerificationResult> {
    compute_pdf_hash(pdf_bytes, &byte_range.inner, algorithm.inner)
        .map(|r| PyHashVerificationResult { inner: r })
        .map_err(sig_err_to_py)
}

#[pyfunction]
fn parse_pkcs7_signature_py(contents: &[u8]) -> PyResult<PyParsedSignature> {
    parse_pkcs7_signature(contents)
        .map(|s| PyParsedSignature { inner: s })
        .map_err(sig_err_to_py)
}

#[pyfunction]
fn verify_pdf_signature_py(
    pdf_bytes: &[u8],
    signature: &PyParsedSignature,
    byte_range: &PyByteRange,
) -> PyResult<PySignatureVerificationResult> {
    verify_signature(pdf_bytes, &signature.inner, &byte_range.inner)
        .map(|r| PySignatureVerificationResult { inner: r })
        .map_err(sig_err_to_py)
}

#[pyfunction]
fn validate_pdf_certificate_py(
    cert_der: &[u8],
    trust_store: &PyTrustStore,
) -> PyResult<PyCertificateValidationResult> {
    validate_certificate(cert_der, &trust_store.inner)
        .map(|r| PyCertificateValidationResult { inner: r })
        .map_err(sig_err_to_py)
}

#[pyfunction]
fn has_incremental_update_py(
    pdf_bytes: &[u8],
    byte_range: &PyByteRange,
) -> bool {
    oxidize_pdf::signatures::has_incremental_update(pdf_bytes, &byte_range.inner)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPermissions>()?;
    m.add_class::<PyEncryptionStrength>()?;
    m.add_class::<PyRecipient>()?;
    // F75 — Signatures Deep
    m.add_class::<PyDigestAlgorithm>()?;
    m.add_class::<PySignatureAlgorithm>()?;
    m.add_class::<PyByteRange>()?;
    m.add_class::<PySignatureField>()?;
    m.add_class::<PyTrustStore>()?;
    m.add_class::<PyParsedSignature>()?;
    m.add_class::<PyHashVerificationResult>()?;
    m.add_class::<PySignatureVerificationResult>()?;
    m.add_class::<PyCertificateValidationResult>()?;
    m.add_class::<PyFullSignatureValidationResult>()?;
    // F75 — Functions
    m.add_function(wrap_pyfunction!(compute_pdf_hash_py, m)?)?;
    m.add_function(wrap_pyfunction!(parse_pkcs7_signature_py, m)?)?;
    m.add_function(wrap_pyfunction!(verify_pdf_signature_py, m)?)?;
    m.add_function(wrap_pyfunction!(validate_pdf_certificate_py, m)?)?;
    m.add_function(wrap_pyfunction!(has_incremental_update_py, m)?)?;
    Ok(())
}
