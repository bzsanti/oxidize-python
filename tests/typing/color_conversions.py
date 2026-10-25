from oxidize_pdf import Color, Page

color = Color.rgb(.2, .4, .8)
cmyk: Color = color.to_cmyk()
rgb: Color = cmyk.to_rgb()
components: tuple[float, float, float, float] = color.cmyk_components()
space: str = color.color_space_name()
flags: tuple[bool, bool, bool] = (color.is_rgb(), color.is_cmyk(), color.is_gray())
Page.a4().set_fill_color(rgb)
Page.a4().set_stroke_color(cmyk)
