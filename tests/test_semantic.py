"""Tests for F81 — Semantic Marking: EntityType, SemanticEntity, EntityMap."""

import pytest
from oxidize_pdf import (
    EntityType,
    RelationType,
    ExportFormat,
    BoundingBox,
    EntityMetadata,
    SemanticEntity,
    Entity,
    EntityMap,
)


# ═══════════════════════════════════════════════════════════════════════════════
# EntityType (33 variants + Custom)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEntityType:
    def test_document_structure_variants(self):
        assert EntityType.TEXT is not None
        assert EntityType.IMAGE is not None
        assert EntityType.TABLE is not None
        assert EntityType.HEADING is not None
        assert EntityType.PARAGRAPH is not None
        assert EntityType.LIST is not None
        assert EntityType.PAGE_NUMBER is not None
        assert EntityType.HEADER is not None
        assert EntityType.FOOTER is not None

    def test_financial_variants(self):
        assert EntityType.INVOICE is not None
        assert EntityType.INVOICE_NUMBER is not None
        assert EntityType.CUSTOMER_NAME is not None
        assert EntityType.LINE_ITEM is not None
        assert EntityType.TOTAL_AMOUNT is not None
        assert EntityType.TAX_AMOUNT is not None
        assert EntityType.DUE_DATE is not None
        assert EntityType.PAYMENT_AMOUNT is not None

    def test_identity_variants(self):
        assert EntityType.PERSON_NAME is not None
        assert EntityType.ORGANIZATION_NAME is not None
        assert EntityType.ADDRESS is not None
        assert EntityType.PHONE_NUMBER is not None
        assert EntityType.EMAIL is not None
        assert EntityType.WEBSITE is not None

    def test_legal_variants(self):
        assert EntityType.CONTRACT is not None
        assert EntityType.CONTRACT_PARTY is not None
        assert EntityType.CONTRACT_TERM is not None
        assert EntityType.EFFECTIVE_DATE is not None
        assert EntityType.CONTRACT_VALUE is not None
        assert EntityType.SIGNATURE is not None

    def test_dates_numbers_variants(self):
        assert EntityType.DATE is not None
        assert EntityType.AMOUNT is not None
        assert EntityType.QUANTITY is not None
        assert EntityType.PERCENTAGE is not None

    def test_custom(self):
        custom = EntityType.custom("MyCustomType")
        assert custom is not None

    def test_repr(self):
        assert "EntityType" in repr(EntityType.TEXT)

    def test_equality(self):
        assert EntityType.TEXT == EntityType.TEXT
        assert EntityType.TEXT != EntityType.IMAGE


# ═══════════════════════════════════════════════════════════════════════════════
# RelationType
# ═══════════════════════════════════════════════════════════════════════════════


class TestRelationType:
    def test_variants(self):
        assert RelationType.CONTAINS is not None
        assert RelationType.IS_PART_OF is not None
        assert RelationType.REFERENCES is not None
        assert RelationType.FOLLOWS is not None
        assert RelationType.PRECEDES is not None

    def test_custom(self):
        custom = RelationType.custom("MyRelation")
        assert custom is not None

    def test_repr(self):
        assert "RelationType" in repr(RelationType.CONTAINS)


# ═══════════════════════════════════════════════════════════════════════════════
# ExportFormat
# ═══════════════════════════════════════════════════════════════════════════════


class TestExportFormat:
    def test_variants(self):
        assert ExportFormat.JSON is not None
        assert ExportFormat.JSON_LD is not None
        assert ExportFormat.XML is not None

    def test_repr(self):
        assert "ExportFormat" in repr(ExportFormat.JSON)


# ═══════════════════════════════════════════════════════════════════════════════
# BoundingBox
# ═══════════════════════════════════════════════════════════════════════════════


class TestBoundingBox:
    def test_create(self):
        bb = BoundingBox(10.0, 20.0, 100.0, 50.0, 1)
        assert bb is not None

    def test_getters(self):
        bb = BoundingBox(10.0, 20.0, 100.0, 50.0, 1)
        assert bb.x == 10.0
        assert bb.y == 20.0
        assert bb.width == 100.0
        assert bb.height == 50.0
        assert bb.page == 1

    def test_right(self):
        bb = BoundingBox(10.0, 20.0, 100.0, 50.0, 1)
        assert bb.right == 110.0

    def test_top(self):
        bb = BoundingBox(10.0, 20.0, 100.0, 50.0, 1)
        assert bb.top == 70.0

    def test_area(self):
        bb = BoundingBox(0.0, 0.0, 10.0, 5.0, 1)
        assert bb.area == 50.0

    def test_intersects_same_page(self):
        bb1 = BoundingBox(0.0, 0.0, 100.0, 100.0, 1)
        bb2 = BoundingBox(50.0, 50.0, 100.0, 100.0, 1)
        assert bb1.intersects(bb2) is True

    def test_no_intersect_different_page(self):
        bb1 = BoundingBox(0.0, 0.0, 100.0, 100.0, 1)
        bb2 = BoundingBox(0.0, 0.0, 100.0, 100.0, 2)
        assert bb1.intersects(bb2) is False

    def test_no_intersect_no_overlap(self):
        bb1 = BoundingBox(0.0, 0.0, 10.0, 10.0, 1)
        bb2 = BoundingBox(50.0, 50.0, 10.0, 10.0, 1)
        assert bb1.intersects(bb2) is False

    def test_repr(self):
        bb = BoundingBox(10.0, 20.0, 100.0, 50.0, 1)
        assert "BoundingBox" in repr(bb)


# ═══════════════════════════════════════════════════════════════════════════════
# EntityMetadata
# ═══════════════════════════════════════════════════════════════════════════════


class TestEntityMetadata:
    def test_create_empty(self):
        em = EntityMetadata()
        assert em is not None

    def test_with_property(self):
        em = EntityMetadata().with_property("source", "OCR")
        assert em is not None

    def test_with_confidence(self):
        em = EntityMetadata().with_confidence(0.95)
        assert em is not None

    def test_with_schema(self):
        em = EntityMetadata().with_schema("https://schema.org/Invoice")
        assert em is not None

    def test_chaining(self):
        em = (EntityMetadata()
              .with_property("key", "value")
              .with_confidence(0.8)
              .with_schema("https://schema.org"))
        assert em is not None

    def test_repr(self):
        em = EntityMetadata()
        assert "EntityMetadata" in repr(em)


# ═══════════════════════════════════════════════════════════════════════════════
# SemanticEntity
# ═══════════════════════════════════════════════════════════════════════════════


class TestSemanticEntity:
    def test_create(self):
        bb = BoundingBox(0.0, 0.0, 100.0, 50.0, 1)
        entity = SemanticEntity("e1", EntityType.TEXT, bb)
        assert entity is not None

    def test_getters(self):
        bb = BoundingBox(10.0, 20.0, 100.0, 50.0, 1)
        entity = SemanticEntity("e1", EntityType.HEADING, bb)
        assert entity.id == "e1"

    def test_with_content(self):
        bb = BoundingBox(0.0, 0.0, 100.0, 50.0, 1)
        entity = SemanticEntity("e1", EntityType.TEXT, bb).with_content("Hello World")
        assert entity is not None

    def test_with_metadata(self):
        bb = BoundingBox(0.0, 0.0, 100.0, 50.0, 1)
        meta = EntityMetadata().with_confidence(0.9)
        entity = SemanticEntity("e1", EntityType.TEXT, bb).with_metadata(meta)
        assert entity is not None

    def test_with_relationship(self):
        bb = BoundingBox(0.0, 0.0, 100.0, 50.0, 1)
        entity = (SemanticEntity("e1", EntityType.TEXT, bb)
                  .with_relationship("e2", RelationType.FOLLOWS))
        assert entity is not None

    def test_repr(self):
        bb = BoundingBox(0.0, 0.0, 100.0, 50.0, 1)
        entity = SemanticEntity("e1", EntityType.TEXT, bb)
        assert "SemanticEntity" in repr(entity)


# ═══════════════════════════════════════════════════════════════════════════════
# Entity (legacy)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEntity:
    def test_create(self):
        entity = Entity("e1", EntityType.TEXT, (10.0, 20.0, 100.0, 50.0), 0)
        assert entity is not None

    def test_getters(self):
        entity = Entity("e1", EntityType.TABLE, (10.0, 20.0, 100.0, 50.0), 1)
        assert entity.id == "e1"
        assert entity.page == 1

    def test_repr(self):
        entity = Entity("e1", EntityType.TEXT, (0.0, 0.0, 10.0, 10.0), 0)
        assert "Entity" in repr(entity)


# ═══════════════════════════════════════════════════════════════════════════════
# EntityMap
# ═══════════════════════════════════════════════════════════════════════════════


class TestEntityMap:
    def test_create_empty(self):
        em = EntityMap()
        assert em is not None

    def test_add_entity(self):
        em = EntityMap()
        entity = Entity("e1", EntityType.TEXT, (0.0, 0.0, 100.0, 50.0), 0)
        em.add_entity(entity)

    def test_entities_by_type(self):
        em = EntityMap()
        em.add_entity(Entity("e1", EntityType.TEXT, (0.0, 0.0, 10.0, 10.0), 0))
        em.add_entity(Entity("e2", EntityType.IMAGE, (0.0, 0.0, 10.0, 10.0), 0))
        em.add_entity(Entity("e3", EntityType.TEXT, (10.0, 0.0, 10.0, 10.0), 0))
        text_entities = em.entities_by_type(EntityType.TEXT)
        assert len(text_entities) == 2

    def test_entities_on_page(self):
        em = EntityMap()
        em.add_entity(Entity("e1", EntityType.TEXT, (0.0, 0.0, 10.0, 10.0), 0))
        em.add_entity(Entity("e2", EntityType.TEXT, (0.0, 0.0, 10.0, 10.0), 1))
        page0 = em.entities_on_page(0)
        assert len(page0) == 1

    def test_entities_on_missing_page(self):
        em = EntityMap()
        assert em.entities_on_page(99) == []

    def test_to_json(self):
        em = EntityMap()
        em.add_entity(Entity("e1", EntityType.TEXT, (0.0, 0.0, 10.0, 10.0), 0))
        json_str = em.to_json()
        assert isinstance(json_str, str)
        assert "e1" in json_str

    def test_repr(self):
        em = EntityMap()
        assert "EntityMap" in repr(em)
