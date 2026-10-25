//! Preserve native signature variants and fields without parsing Display text.
use oxidize_pdf::signatures::SignatureError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

pub(crate) fn to_py_error(error: SignatureError) -> PyErr {
    Python::attach(|py| convert(py, error)).unwrap_or_else(|error| error)
}

fn convert(py: Python<'_>, error: SignatureError) -> PyResult<PyErr> {
    let message = error.to_string();
    let details = PyDict::new(py);
    let (code, value_error) = match error {
        SignatureError::MissingField { field } => {
            details.set_item("field", field)?;
            ("missing_field", true)
        }
        SignatureError::InvalidByteRange { details: value } => {
            details.set_item("details", value)?;
            ("invalid_byte_range", true)
        }
        SignatureError::InvalidSignatureDict { details: value } => {
            details.set_item("details", value)?;
            ("invalid_signature_dict", true)
        }
        SignatureError::ContentsExtractionFailed { details: value } => {
            details.set_item("details", value)?;
            ("contents_extraction_failed", false)
        }
        SignatureError::AcroFormNotFound => ("acro_form_not_found", true),
        SignatureError::NoSignatureFields => ("no_signature_fields", true),
        SignatureError::ParseError { message } => {
            details.set_item("message", message)?;
            ("parse_error", false)
        }
        SignatureError::CmsParsingFailed { details: value } => {
            details.set_item("details", value)?;
            ("cms_parsing_failed", false)
        }
        SignatureError::UnsupportedAlgorithm { algorithm } => {
            details.set_item("algorithm", algorithm)?;
            ("unsupported_algorithm", true)
        }
        SignatureError::ByteRangeExceedsDocument { offset, length, document_size } => {
            details.set_item("offset", offset)?;
            details.set_item("length", length)?;
            details.set_item("document_size", document_size)?;
            ("byte_range_exceeds_document", true)
        }
        SignatureError::HashVerificationFailed { details: value } => {
            details.set_item("details", value)?;
            ("hash_verification_failed", false)
        }
        SignatureError::SignatureVerificationFailed { details: value } => {
            details.set_item("details", value)?;
            ("signature_verification_failed", false)
        }
        SignatureError::CertificateExtractionFailed { details: value } => {
            details.set_item("details", value)?;
            ("certificate_extraction_failed", false)
        }
        SignatureError::CertificateValidationFailed { details: value } => {
            details.set_item("details", value)?;
            ("certificate_validation_failed", false)
        }
    };
    let class = if value_error { "PdfSignatureValueError" } else { "PdfSignatureRuntimeError" };
    let exception = py.import("oxidize_pdf.signature_errors")?
        .getattr(class)?.call1((message, code, details))?;
    Ok(PyErr::from_value(exception))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_all_signature_variants_and_fields() {
        // Independent fixtures cover variants not reachable through ordinary
        // malformed-PDF inputs, including unknown algorithms and full u64 values.
        let cases = [
            (SignatureError::MissingField { field: "ByteRange".into() }, "missing_field", r#"{"field":"ByteRange"}"#, true),
            (SignatureError::InvalidByteRange { details: "range detail".into() }, "invalid_byte_range", r#"{"details":"range detail"}"#, true),
            (SignatureError::InvalidSignatureDict { details: "dict detail".into() }, "invalid_signature_dict", r#"{"details":"dict detail"}"#, true),
            (SignatureError::ContentsExtractionFailed { details: "contents detail".into() }, "contents_extraction_failed", r#"{"details":"contents detail"}"#, false),
            (SignatureError::AcroFormNotFound, "acro_form_not_found", "{}", true),
            (SignatureError::NoSignatureFields, "no_signature_fields", "{}", true),
            (SignatureError::ParseError { message: "é\0parse".into() }, "parse_error", r#"{"message":"é\u0000parse"}"#, false),
            (SignatureError::CmsParsingFailed { details: "CMS detail".into() }, "cms_parsing_failed", r#"{"details":"CMS detail"}"#, false),
            (SignatureError::UnsupportedAlgorithm { algorithm: "1.2.3.999".into() }, "unsupported_algorithm", r#"{"algorithm":"1.2.3.999"}"#, true),
            (SignatureError::ByteRangeExceedsDocument { offset: u64::MAX, length: 17, document_size: 9007199254740993 }, "byte_range_exceeds_document", r#"{"offset":18446744073709551615,"length":17,"document_size":9007199254740993}"#, true),
            (SignatureError::HashVerificationFailed { details: "hash detail".into() }, "hash_verification_failed", r#"{"details":"hash detail"}"#, false),
            (SignatureError::SignatureVerificationFailed { details: "signature detail".into() }, "signature_verification_failed", r#"{"details":"signature detail"}"#, false),
            (SignatureError::CertificateExtractionFailed { details: "extract detail".into() }, "certificate_extraction_failed", r#"{"details":"extract detail"}"#, false),
            (SignatureError::CertificateValidationFailed { details: "validation detail".into() }, "certificate_validation_failed", r#"{"details":"validation detail"}"#, false),
        ];
        Python::initialize();
        Python::attach(|py| {
            let package = py.import("oxidize_pdf").unwrap();
            let json = py.import("json").unwrap();
            let builtins = py.import("builtins").unwrap();
            let contract = json.call_method1("loads", (include_str!("../docs/parity-contract.json"),)).unwrap();
            let codes = contract.get_item("signature_errors").unwrap().get_item("codes").unwrap();
            for (native, code, fields, value_error) in cases {
                let message = native.to_string();
                let error = to_py_error(native);
                let exception = error.value(py);
                assert!(exception.is_instance(&package.getattr("PdfError").unwrap()).unwrap(), "{code}");
                assert!(exception.is_instance(&package.getattr("PdfSignatureError").unwrap()).unwrap(), "{code}");
                let legacy = if value_error { "ValueError" } else { "RuntimeError" };
                assert!(exception.is_instance(&builtins.getattr(legacy).unwrap()).unwrap(), "{code}");
                assert_eq!(exception.getattr("code").unwrap().extract::<String>().unwrap(), code);
                assert_eq!(exception.str().unwrap().to_str().unwrap(), message);
                let expected = json.call_method1("loads", (fields,)).unwrap();
                assert!(exception.getattr("details").unwrap().eq(&expected).unwrap(), "{code}");
                let mut keys = expected.call_method0("keys").unwrap().try_iter().unwrap()
                    .map(|key| key.unwrap().extract::<String>().unwrap()).collect::<Vec<_>>();
                let mut declared = codes.get_item(code).unwrap().extract::<Vec<String>>().unwrap();
                keys.sort();
                declared.sort();
                assert_eq!(keys, declared, "error fields disagree with parity contract: {code}");
            }
        });
    }
}
