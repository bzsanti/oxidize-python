"""Tests for F78 — XMP Metadata."""

import pytest
from oxidize_pdf import (
    Document,
    XmpMetadata,
    XmpNamespace,
    XmpProperty,
    XmpValue,
)


# ═══════════════════════════════════════════════════════════════════════════════
# XmpNamespace
# ═══════════════════════════════════════════════════════════════════════════════


class TestXmpNamespace:
    def test_dublin_core(self):
        ns = XmpNamespace.DUBLIN_CORE
        assert ns.prefix == "dc"
        assert "purl.org" in ns.uri

    def test_xmp_basic(self):
        ns = XmpNamespace.XMP_BASIC
        assert ns.prefix == "xmp"

    def test_xmp_rights(self):
        ns = XmpNamespace.XMP_RIGHTS
        assert ns.prefix == "xmpRights"

    def test_xmp_media_management(self):
        ns = XmpNamespace.XMP_MEDIA_MANAGEMENT
        assert ns.prefix == "xmpMM"

    def test_pdf(self):
        ns = XmpNamespace.PDF
        assert ns.prefix == "pdf"

    def test_photoshop(self):
        ns = XmpNamespace.PHOTOSHOP
        assert ns.prefix == "photoshop"

    def test_custom(self):
        ns = XmpNamespace.custom("myns", "http://example.com/ns/")
        assert ns.prefix == "myns"
        assert ns.uri == "http://example.com/ns/"

    def test_repr(self):
        ns = XmpNamespace.DUBLIN_CORE
        assert "XmpNamespace" in repr(ns)


# ═══════════════════════════════════════════════════════════════════════════════
# XmpValue
# ═══════════════════════════════════════════════════════════════════════════════


class TestXmpValue:
    def test_text(self):
        v = XmpValue.text("Hello")
        assert v is not None
        assert v.value_type == "Text"

    def test_date(self):
        v = XmpValue.date("2026-03-21T12:00:00Z")
        assert v.value_type == "Date"

    def test_array(self):
        v = XmpValue.array(["a", "b", "c"])
        assert v.value_type == "Array"

    def test_bag(self):
        v = XmpValue.bag(["keyword1", "keyword2"])
        assert v.value_type == "Bag"

    def test_alt(self):
        v = XmpValue.alt([("en", "Hello"), ("es", "Hola")])
        assert v.value_type == "Alt"

    def test_struct_value(self):
        v = XmpValue.struct_value({
            "name": XmpValue.text("John"),
            "age": XmpValue.text("30"),
        })
        assert v.value_type == "Struct"

    def test_array_struct(self):
        v = XmpValue.array_struct([
            {"name": XmpValue.text("Alice"), "role": XmpValue.text("Author")},
            {"name": XmpValue.text("Bob"), "role": XmpValue.text("Editor")},
        ])
        assert v.value_type == "ArrayStruct"

    def test_repr(self):
        v = XmpValue.text("test")
        assert "XmpValue" in repr(v)


# ═══════════════════════════════════════════════════════════════════════════════
# XmpProperty
# ═══════════════════════════════════════════════════════════════════════════════


class TestXmpProperty:
    def test_create(self):
        prop = XmpProperty(
            XmpNamespace.DUBLIN_CORE,
            "title",
            XmpValue.text("My Document"),
        )
        assert prop is not None

    def test_getters(self):
        prop = XmpProperty(
            XmpNamespace.DUBLIN_CORE,
            "creator",
            XmpValue.text("Author Name"),
        )
        assert prop.name == "creator"
        assert prop.namespace is not None

    def test_repr(self):
        prop = XmpProperty(
            XmpNamespace.DUBLIN_CORE,
            "title",
            XmpValue.text("Test"),
        )
        assert "XmpProperty" in repr(prop)


# ═══════════════════════════════════════════════════════════════════════════════
# XmpMetadata
# ═══════════════════════════════════════════════════════════════════════════════


class TestXmpMetadata:
    def test_create(self):
        xmp = XmpMetadata()
        assert xmp is not None

    def test_set_text(self):
        xmp = XmpMetadata()
        xmp.set_text(XmpNamespace.DUBLIN_CORE, "title", "My Document")
        assert xmp.property_count == 1

    def test_set_date(self):
        xmp = XmpMetadata()
        xmp.set_date(XmpNamespace.XMP_BASIC, "CreateDate", "2026-03-21T12:00:00Z")
        assert xmp.property_count == 1

    def test_set_array(self):
        xmp = XmpMetadata()
        xmp.set_array(XmpNamespace.DUBLIN_CORE, "subject", ["PDF", "Rust", "Python"])
        assert xmp.property_count == 1

    def test_set_bag(self):
        xmp = XmpMetadata()
        xmp.set_bag(XmpNamespace.DUBLIN_CORE, "subject", ["keyword1", "keyword2"])
        assert xmp.property_count == 1

    def test_set_alt(self):
        xmp = XmpMetadata()
        xmp.set_alt(XmpNamespace.DUBLIN_CORE, "title", [("en", "Title"), ("es", "Título")])
        assert xmp.property_count == 1

    def test_add_property(self):
        xmp = XmpMetadata()
        prop = XmpProperty(
            XmpNamespace.DUBLIN_CORE,
            "creator",
            XmpValue.text("Author"),
        )
        xmp.add_property(prop)
        assert xmp.property_count == 1

    def test_multiple_properties(self):
        xmp = XmpMetadata()
        xmp.set_text(XmpNamespace.DUBLIN_CORE, "title", "Doc")
        xmp.set_text(XmpNamespace.DUBLIN_CORE, "creator", "Author")
        xmp.set_date(XmpNamespace.XMP_BASIC, "CreateDate", "2026-01-01")
        assert xmp.property_count == 3

    def test_register_namespace(self):
        xmp = XmpMetadata()
        xmp.register_namespace("custom", "http://example.com/ns/")

    def test_to_xmp_packet(self):
        xmp = XmpMetadata()
        xmp.set_text(XmpNamespace.DUBLIN_CORE, "title", "Test")
        packet = xmp.to_xmp_packet()
        assert isinstance(packet, str)
        assert "xpacket" in packet or "rdf" in packet.lower()

    def test_set_text_duplicates_accumulate(self):
        """set_* methods append, not upsert — calling twice creates two properties."""
        xmp = XmpMetadata()
        xmp.set_text(XmpNamespace.DUBLIN_CORE, "title", "First")
        xmp.set_text(XmpNamespace.DUBLIN_CORE, "title", "Second")
        assert xmp.property_count == 2

    def test_repr(self):
        xmp = XmpMetadata()
        assert "XmpMetadata" in repr(xmp)

    def test_clear_resets_properties(self):
        """clear() removes all properties from the container."""
        xmp = XmpMetadata()
        xmp.set_text(XmpNamespace.DUBLIN_CORE, "title", "My Document")
        xmp.set_text(XmpNamespace.DUBLIN_CORE, "creator", "Author")
        assert xmp.property_count == 2
        xmp.clear()
        assert xmp.property_count == 0

    def test_clear_allows_reuse(self):
        """After clear(), the container can accept new properties."""
        xmp = XmpMetadata()
        xmp.set_text(XmpNamespace.DUBLIN_CORE, "title", "First")
        xmp.clear()
        xmp.set_text(XmpNamespace.DUBLIN_CORE, "title", "Second")
        assert xmp.property_count == 1

    def test_document_create_xmp(self):
        """Document.create_xmp_metadata() creates XMP from document metadata."""
        doc = Document()
        doc.set_title("Test Title")
        doc.set_author("Test Author")
        xmp = doc.create_xmp_metadata()
        assert isinstance(xmp, XmpMetadata)
        assert xmp.property_count > 0

    def test_document_get_xmp_packet(self):
        """Document.get_xmp_packet() returns XMP as XML string."""
        doc = Document()
        doc.set_title("Test")
        packet = doc.get_xmp_packet()
        assert isinstance(packet, str)
