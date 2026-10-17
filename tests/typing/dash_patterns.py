from oxidize_pdf import LineDashPattern, Page

pattern: LineDashPattern = LineDashPattern.dashed(6, 3)
points: LineDashPattern = LineDashPattern.dotted(1, 4)
solid: LineDashPattern = LineDashPattern.solid()
custom: LineDashPattern = LineDashPattern([2, 7], 3)
array: list[float] = pattern.array
phase: float = pattern.phase
pdf: str = pattern.to_pdf_string()
Page.a4().set_dash_pattern(points)
