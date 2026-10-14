from oxidize_pdf import PdfReader, OutlineReadOptions, ReadOutline, ReadOutlineItem, ReadOutlineDestination


def read(reader: PdfReader) -> None:
    default: ReadOutline | None = reader.outline()
    tree = reader.outline_with_options(OutlineReadOptions(max_items=100, max_depth=10,
        max_named_destinations=20, max_name_tree_nodes=30))
    if tree is None:
        return
    items: list[ReadOutlineItem] = tree.items
    for item in items:
        destination: ReadOutlineDestination | None = item.destination
        color: tuple[float, float, float] | None = item.color
        print(item.title, item.is_bold, item.is_italic, item.is_open, color, default)
        if destination is not None:
            page: int = destination.page_index
            parameters: list[float | None] = destination.parameters
            print(page, destination.kind, parameters)
