"""Strict consumer of native note/highlight values, mutations and results."""
from oxidize_pdf import (
    IncrementalTextNoteEditor, IncrementalHighlightEditor, TextNoteId, HighlightId,
    TextNoteMutation, HighlightMutation, HighlightQuad, HighlightColor,
    HighlightOpacity, TextNote, Highlight, TextNoteUpdate, HighlightUpdate,
)

def edit(source: bytes) -> bytes:
    notes = IncrementalTextNoteEditor(source)
    update: TextNoteUpdate = notes.apply([TextNoteMutation.add(0, (20., 30.), 'café 世界')])
    note: TextNote = update.added_notes[0]
    ident: TextNoteId = note.id
    pos: tuple[float, float] = note.position
    mutation = TextNoteMutation.update(ident, pos, note.contents)
    assert mutation.position == pos and mutation.id == ident and mutation.kind == 'update'
    changed = IncrementalTextNoteEditor(update.pdf_bytes).apply([mutation])
    removed = IncrementalTextNoteEditor(changed.pdf_bytes).apply([TextNoteMutation.remove(ident)])
    quad = HighlightQuad([(10., 50.), (80., 50.), (10., 35.), (80., 35.)])
    color = HighlightColor([1., .5, 0.])
    opacity = HighlightOpacity(.25)
    add = HighlightMutation.add(0, [quad], color, opacity, '')
    assert add.quadrilaterals is not None and add.color is not None
    result: HighlightUpdate = IncrementalHighlightEditor(removed.pdf_bytes).apply([add])
    mark: Highlight = result.highlights[0]
    hid: HighlightId = mark.id
    rgb: list[float] = mark.color.components
    points: list[tuple[float, float]] = mark.quadrilaterals[0].points
    assert rgb and points and mark.opacity is not None and mark.opacity.value == .25
    return IncrementalHighlightEditor(result.pdf_bytes).apply([HighlightMutation.remove(hid)]).pdf_bytes
