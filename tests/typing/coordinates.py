from oxidize_pdf import CoordinateSystem, Page, Point, TransformMatrix

matrix: TransformMatrix = TransformMatrix(1, 2, 3, 4, 5, 6)
composed: TransformMatrix = TransformMatrix.translate(4, 5).multiply(TransformMatrix.scale(2, 3))
rotated: TransformMatrix = TransformMatrix.rotate(1.5)
flipped: TransformMatrix = TransformMatrix.flip_y(800)
identity: TransformMatrix = TransformMatrix.IDENTITY
component: float = matrix.a + matrix.b + matrix.c + matrix.d + matrix.e + matrix.f
ctm: str = composed.to_pdf_ctm()
point: Point = composed.transform_point(Point(1, 2))
custom: CoordinateSystem = CoordinateSystem.custom(matrix)
converted: Point = custom.to_pdf_standard(point, 800)
y: float = custom.y_to_pdf_standard(10, 800)
upward: bool = custom.grows_upward()
result: TransformMatrix = custom.to_pdf_standard_matrix(800)
page = Page(200, 100)
page.set_coordinate_system(custom)
snapshot: CoordinateSystem = page.coordinate_system
