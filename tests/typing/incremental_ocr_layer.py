from oxidize_pdf import (IncrementalOcrLayerEditor, OcrLayerFragment, OcrLayerPage, OcrLayerPlan, OcrLayerUpdate)

def append_text(source: bytes) -> bytes:
    fragment = OcrLayerFragment('café', [30.0, 80.0, 40.0, 12.0], 0.9, 0)
    page = OcrLayerPage(0, 'es', [fragment])
    editor = IncrementalOcrLayerEditor(source)
    plan: OcrLayerPlan = editor.plan([page])
    result: OcrLayerUpdate = editor.apply([page])
    changed: list[int] = plan.pages
    assert result.plan.pages == changed
    skipped: list[int] = result.plan.pages_skipped_existing_ocr
    assert not skipped
    return result.pdf_bytes
