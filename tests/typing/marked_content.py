from oxidize_pdf import Page

page = Page.a4()
mcid: int = page.begin_marked_content('P')
replacement: int = page.begin_marked_content_with_actual_text('Span', 'café 😀')
next_id: int = page.next_mcid()
depth: int = page.marked_content_depth()
page.end_marked_content()
page.end_marked_content()
