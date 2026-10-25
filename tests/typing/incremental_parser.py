"""Strict discriminated-event consumer, including not-yet-emitted variants."""
from oxidize_pdf import IncrementalParser, PdfValue, ParseEvent

def inspect(parser: IncrementalParser) -> list[bytes]:
    events: list[ParseEvent] = parser.take_events()
    chunks: list[bytes] = []
    for event in events:
        if event['type'] == 'stream_data':
            data: bytes = event['data']
            assert len(data) == event['data_len']
            chunks.append(data)
        elif event['type'] == 'object_end':
            obj: PdfValue = event['object']
            if obj.kind == 'null':
                assert obj.value is None
        elif event['type'] == 'xref':
            for entry in event['entries']:
                offset: int = entry['offset']
                in_use: bool = entry['in_use']
                assert offset >= 0 or not in_use
        elif event['type'] == 'trailer':
            values: dict[str, PdfValue] = event['dict']
            assert isinstance(values, dict)
    return chunks
