"""Structured errors emitted by signature operations in core 5.4.2.

``code`` identifies the native variant; ``details`` retains its original fields.
Messages remain readable but are not a machine-readable contract. These classes
also retain the historical ValueError/RuntimeError categories of deep-signature
operations. No error code implies successful verification or certificate trust.
"""
from typing import Literal, TypedDict

from oxidize_pdf._oxidize_pdf import PdfError

SignatureErrorCode = Literal[
    'missing_field', 'invalid_byte_range', 'invalid_signature_dict',
    'contents_extraction_failed', 'acro_form_not_found', 'no_signature_fields',
    'parse_error', 'cms_parsing_failed', 'unsupported_algorithm',
    'byte_range_exceeds_document', 'hash_verification_failed',
    'signature_verification_failed', 'certificate_extraction_failed',
    'certificate_validation_failed',
]


class SignatureErrorDetails(TypedDict, total=False):
    """Only fields belonging to the native variant are present; sizes are bytes."""
    field: str
    details: str
    message: str
    algorithm: str
    offset: int
    length: int
    document_size: int


class PdfSignatureError(PdfError):
    """Base for structured signature failures; still catchable as PdfError."""
    code: SignatureErrorCode
    details: SignatureErrorDetails

    def __init__(self, message: str, code: SignatureErrorCode,
                 details: SignatureErrorDetails) -> None:
        super().__init__(message)
        self.code = code
        self.details = details.copy()

    def __reduce__(self) -> tuple[object, ...]:
        return type(self), (str(self), self.code, self.details), self.__dict__


class PdfSignatureValueError(PdfSignatureError, ValueError):
    """Invalid signature input; retains ValueError compatibility."""


class PdfSignatureRuntimeError(PdfSignatureError, RuntimeError):
    """Signature processing failure; retains RuntimeError compatibility."""


class SignatureVerificationSummary(TypedDict):
    """Cryptographic verification only; does not establish certificate trust."""
    name: str
    filter: str
    sub_filter: str
    valid: bool
    error: str | None
    error_code: SignatureErrorCode | None
    error_details: SignatureErrorDetails | None
