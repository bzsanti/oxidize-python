"""Pydantic models for MCP tool inputs and outputs."""

from __future__ import annotations

__all__ = [
    "ErrorOutput",
    "SessionOutput",
    "ReadPdfInput",
    "PageDetail",
    "ReadPdfOutput",
    "ExtractTextInput",
    "ExtractTextOutput",
    "ConvertPdfInput",
]

from typing import Literal

from pydantic import BaseModel


# --- Common ---


class ErrorOutput(BaseModel):
    error: str
    code: str


class SessionOutput(BaseModel):
    session_id: str
    status: str


# --- read_pdf ---


class ReadPdfInput(BaseModel):
    path: str
    password: str | None = None
    include_page_details: bool = False


class PageDetail(BaseModel):
    index: int
    width: float
    height: float
    rotation: int = 0


class ReadPdfOutput(BaseModel):
    path: str
    page_count: int
    is_encrypted: bool
    version: str
    title: str | None = None
    author: str | None = None
    subject: str | None = None
    keywords: str | None = None
    pages: list[PageDetail] | None = None


# --- extract_text ---


class ExtractTextInput(BaseModel):
    path: str
    page: int | None = None
    password: str | None = None


class ExtractTextOutput(BaseModel):
    text: str
    page: int | None = None
    page_count: int | None = None


# --- convert_pdf ---


class ConvertPdfInput(BaseModel):
    path: str
    format: Literal["markdown", "chunks", "rag"]
    password: str | None = None
    max_tokens: int = 256
    overlap: int = 50
