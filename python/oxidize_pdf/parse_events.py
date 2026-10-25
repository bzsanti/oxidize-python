"""Typed payloads returned by IncrementalParser, reflecting core events.

Core 5.5.0 emits parsed objects, xref/trailer events, and binary stream payloads.
"""
from typing import Literal, TypedDict, Union

from oxidize_pdf._oxidize_pdf import PdfValue


class HeaderEvent(TypedDict):
    type: Literal['header']
    version: str


class ObjectStartEvent(TypedDict):
    type: Literal['object_start']
    id: int
    generation: int


class ObjectEndEvent(TypedDict):
    type: Literal['object_end']
    id: int
    generation: int
    object: PdfValue


class StreamDataEvent(TypedDict):
    type: Literal['stream_data']
    object_id: int
    data_len: int
    data: bytes


class XRefEntry(TypedDict):
    object_number: int
    generation: int
    offset: int
    in_use: bool


class XRefEvent(TypedDict):
    type: Literal['xref']
    entry_count: int
    entries: list[XRefEntry]


class TrailerEvent(TypedDict):
    type: Literal['trailer']
    dict: dict[str, PdfValue]


class EndOfFileEvent(TypedDict):
    type: Literal['end_of_file']


ParseEvent = Union[HeaderEvent, ObjectStartEvent, ObjectEndEvent, StreamDataEvent,
                   XRefEvent, TrailerEvent, EndOfFileEvent]
