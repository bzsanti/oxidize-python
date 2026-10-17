from oxidize_pdf import BlendMode, Page

modes: list[BlendMode] = [BlendMode.DIFFERENCE, BlendMode.EXCLUSION,
    BlendMode.HUE, BlendMode.SATURATION, BlendMode.COLOR, BlendMode.LUMINOSITY]
name: str = BlendMode.DIFFERENCE.pdf_name()
for mode in modes:
    Page.a4().set_blend_mode(mode)
