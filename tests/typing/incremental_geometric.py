from oxidize_pdf import (
    GeometricColor, GeometricStyle, GeometricGeometry, GeometricLineEnding,
    GeometricMutation, GeometricAnnotation, IncrementalGeometricEditor,
)

def edit(source: bytes) -> bytes:
    style = GeometricStyle(GeometricColor.gray(0.0), 2.0, dash_pattern=[2.0, 1.0])
    geometry = GeometricGeometry.line((0.0, 0.0), (20.0, 30.0), end_ending=GeometricLineEnding.OpenArrow)
    result = IncrementalGeometricEditor(source).apply([GeometricMutation.add(0, geometry, style)])
    annotation: GeometricAnnotation = result.annotations[0]
    points: tuple[float, float] | None = annotation.geometry.start
    assert points is not None
    return IncrementalGeometricEditor(result.pdf_bytes).apply([GeometricMutation.remove(annotation.id)]).pdf_bytes
