from oxidize_pdf import Margins, Page

page = Page(200, 300)
page.set_margins(Margins(top=11, right=23, bottom=37, left=41))
page.set_rotation(90)
width: float = page.content_width
height: float = page.content_height
bounds: tuple[float, float, float, float] = page.content_area
effective_width: float = page.effective_width
effective_height: float = page.effective_height
