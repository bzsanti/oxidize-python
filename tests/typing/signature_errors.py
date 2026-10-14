from oxidize_pdf import (
    PdfError, PdfSignatureError, PdfSignatureRuntimeError, PdfSignatureValueError,
    SignatureErrorCode, SignatureErrorDetails, SignaturePreparationOptions,
    SignatureTarget, prepare_incremental_signature,
)


def handle(source: bytes) -> None:
    try:
        prepare_incremental_signature(source, SignaturePreparationOptions(SignatureTarget.new_field('approval')))
    except PdfSignatureError as error:
        code: SignatureErrorCode = error.code
        details: SignatureErrorDetails = error.details
        if code == 'byte_range_exceeds_document':
            size: int = details['document_size']
            print(size)
        elif code == 'unsupported_algorithm':
            algorithm: str = details['algorithm']
            print(algorithm)
    except PdfError:
        pass


value_error: ValueError = PdfSignatureValueError('message', 'missing_field', {'field': 'Contents'})
runtime_error: RuntimeError = PdfSignatureRuntimeError('message', 'parse_error', {'message': 'parse'})

from oxidize_pdf import verify_pdf_signatures, SignatureVerificationSummary


def inspect_signatures(source: bytes) -> None:
    summaries: list[SignatureVerificationSummary] = verify_pdf_signatures(source)
    for summary in summaries:
        code = summary['error_code']
        details = summary['error_details']
        if code == 'unsupported_algorithm' and details is not None:
            print(details['algorithm'])
