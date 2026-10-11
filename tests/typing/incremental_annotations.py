"""Typed consumer of existing-PDF free-text editing."""
from oxidize_pdf import (
    FreeText, FreeTextAlignment, FreeTextId, FreeTextMutation, FreeTextUpdate,
    IncrementalFreeTextEditor,
)


def edit(data: bytes) -> bytes:
    editor = IncrementalFreeTextEditor(data)
    initial: list[FreeText] = editor.annotations()
    mutation: FreeTextMutation = FreeTextMutation.add(
        0, [10., 20., 180., 80.], 'Review', '/Helv 12 Tf 0 g', FreeTextAlignment.Left,
    )
    result: FreeTextUpdate = editor.apply([mutation])
    for annotation in result.annotations:
        identity: FreeTextId = annotation.id
        page: int = annotation.page_index
        rect: list[float] = annotation.rect
        contents: str = annotation.contents
        appearance: str = annotation.default_appearance
        alignment: FreeTextAlignment = annotation.alignment
        assert identity.object_number >= 0 and identity.generation_number >= 0
        assert page >= 0 and rect and contents and appearance and alignment
    assert not initial or result.annotations
    return result.pdf_bytes
