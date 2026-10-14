"""Strict consumer for the real page iterator."""
from oxidize_pdf import PageStreamer, StreamingPage

def read(path: str) -> list[str]:
    texts: list[str] = []
    with PageStreamer.open(path) as stream:
        count: int = stream.total_pages()
        for index in range(count):
            page: StreamingPage | None = stream.next()
            assert page is not None
            box: list[float] = page.media_box()
            assert page.number == index and len(box) == 4
            texts.append(page.extract_text_streaming())
        assert stream.next() is None
    return texts
