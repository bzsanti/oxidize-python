from oxidize_pdf import CoordinateSystem, Point, RenderContext, TransformMatrix

context = RenderContext(CoordinateSystem.SCREEN_SPACE, 600, 800)
width: float = context.page_width
height: float = context.page_height
system: CoordinateSystem = context.coordinate_system
matrix: TransformMatrix = context.current_transform
context.page_width = 700
context.page_height = 900
context.coordinate_system = CoordinateSystem.custom(TransformMatrix.translate(7, 9))
context.current_transform = TransformMatrix.IDENTITY
point: Point = context.to_pdf_standard(Point(17, 19))
y: float = context.y_to_pdf(19)
