from oxidize_pdf import (StreamingDocument, StreamingOptions, MemoryOptions,
    LazyDocument, MemoryConfiguration, StreamingConfiguration, MemoryStats,
    UnsupportedMemoryOption, PdfValue, ParsedPage, StreamingPage)

def inspect(path: str) -> tuple[int, int]:
    with StreamingDocument.open(path, StreamingOptions(page_cache_size=0)) as stream:
        config: StreamingConfiguration = stream.configuration()
        page: StreamingPage | None = stream.next_page()
        if page is not None:
            text: str = page.extract_text_streaming()
        budget: int = config.effective.memory_limit
        stream.clear_cache()
    with LazyDocument.open(path, MemoryOptions.small_file().with_cache_size(2)) as lazy:
        memory: MemoryConfiguration = lazy.configuration()
        unsupported: list[UnsupportedMemoryOption] = memory.unsupported
        obj: PdfValue = lazy.get_object(1)
        parsed: ParsedPage = lazy.get_page(0)
        stats: MemoryStats = lazy.memory_stats()
        count: int = stats.cached_objects
        lazy.preload_page(0)
    return budget, count
