from oxidize_pdf import Ink, InkColor, InkColorSpace, InkId, InkMutation, InkStroke, InkUpdate, IncrementalInkEditor


def draw(data: bytes) -> bytes:
    editor = IncrementalInkEditor(data)
    color: InkColor = InkColor.cmyk([0., 0., 0., 1.])
    space: InkColorSpace = color.space
    components: list[float] = color.components
    assert space == InkColorSpace.Cmyk and len(components) == 4
    stroke: InkStroke = InkStroke([(10.,20.),(30.,40.)])
    points: list[tuple[float,float]] = stroke.points
    assert len(points) == 2
    result: InkUpdate = editor.apply([InkMutation.add(0, [stroke], color, 2., 0.5)])
    annotations: list[Ink] = result.annotations
    for item in annotations:
        identity: InkId = item.id
        page: int = item.page_index
        rect: list[float] = item.rect
        strokes: list[InkStroke] = item.strokes
        width: float = item.width
        opacity: float | None = item.opacity
        assert identity.object_number >= 0 and identity.generation_number >= 0
        assert page >= 0 and rect and strokes and width > 0 and opacity is not None
    return result.pdf_bytes
