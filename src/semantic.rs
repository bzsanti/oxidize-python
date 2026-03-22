use pyo3::prelude::*;
use oxidize_pdf::semantic::{
    EntityType, RelationType, ExportFormat, BoundingBox,
    EntityMetadata, SemanticEntity, Entity, EntityMap,
};

// ── PyEntityType ──────────────────────────────────────────────────────────

/// Semantic entity type for classifying regions in a PDF.
///
/// Standard variants: ``TEXT``, ``IMAGE``, ``TABLE``, ``HEADING``,
/// ``PARAGRAPH``, ``LIST``, ``PAGE_NUMBER``, ``HEADER``, ``FOOTER``,
/// ``INVOICE``, ``INVOICE_NUMBER``, ``CUSTOMER_NAME``, ``LINE_ITEM``,
/// ``TOTAL_AMOUNT``, ``TAX_AMOUNT``, ``DUE_DATE``, ``PAYMENT_AMOUNT``,
/// ``PERSON_NAME``, ``ORGANIZATION_NAME``, ``ADDRESS``, ``PHONE_NUMBER``,
/// ``EMAIL``, ``WEBSITE``, ``CONTRACT``, ``CONTRACT_PARTY``,
/// ``CONTRACT_TERM``, ``EFFECTIVE_DATE``, ``CONTRACT_VALUE``,
/// ``SIGNATURE``, ``DATE``, ``AMOUNT``, ``QUANTITY``, ``PERCENTAGE``.
/// Custom: ``EntityType.custom("MyType")``.
#[pyclass(name = "EntityType", frozen, from_py_object, eq, hash)]
#[derive(Clone, PartialEq, Eq, Hash)]
pub struct PyEntityType {
    pub inner: EntityType,
}

#[pymethods]
impl PyEntityType {
    #[classattr]
    #[allow(non_snake_case)]
    fn TEXT() -> Self { Self { inner: EntityType::Text } }

    #[classattr]
    #[allow(non_snake_case)]
    fn IMAGE() -> Self { Self { inner: EntityType::Image } }

    #[classattr]
    #[allow(non_snake_case)]
    fn TABLE() -> Self { Self { inner: EntityType::Table } }

    #[classattr]
    #[allow(non_snake_case)]
    fn HEADING() -> Self { Self { inner: EntityType::Heading } }

    #[classattr]
    #[allow(non_snake_case)]
    fn PARAGRAPH() -> Self { Self { inner: EntityType::Paragraph } }

    #[classattr]
    #[allow(non_snake_case)]
    fn LIST() -> Self { Self { inner: EntityType::List } }

    #[classattr]
    #[allow(non_snake_case)]
    fn PAGE_NUMBER() -> Self { Self { inner: EntityType::PageNumber } }

    #[classattr]
    #[allow(non_snake_case)]
    fn HEADER() -> Self { Self { inner: EntityType::Header } }

    #[classattr]
    #[allow(non_snake_case)]
    fn FOOTER() -> Self { Self { inner: EntityType::Footer } }

    #[classattr]
    #[allow(non_snake_case)]
    fn INVOICE() -> Self { Self { inner: EntityType::Invoice } }

    #[classattr]
    #[allow(non_snake_case)]
    fn INVOICE_NUMBER() -> Self { Self { inner: EntityType::InvoiceNumber } }

    #[classattr]
    #[allow(non_snake_case)]
    fn CUSTOMER_NAME() -> Self { Self { inner: EntityType::CustomerName } }

    #[classattr]
    #[allow(non_snake_case)]
    fn LINE_ITEM() -> Self { Self { inner: EntityType::LineItem } }

    #[classattr]
    #[allow(non_snake_case)]
    fn TOTAL_AMOUNT() -> Self { Self { inner: EntityType::TotalAmount } }

    #[classattr]
    #[allow(non_snake_case)]
    fn TAX_AMOUNT() -> Self { Self { inner: EntityType::TaxAmount } }

    #[classattr]
    #[allow(non_snake_case)]
    fn DUE_DATE() -> Self { Self { inner: EntityType::DueDate } }

    #[classattr]
    #[allow(non_snake_case)]
    fn PAYMENT_AMOUNT() -> Self { Self { inner: EntityType::PaymentAmount } }

    #[classattr]
    #[allow(non_snake_case)]
    fn PERSON_NAME() -> Self { Self { inner: EntityType::PersonName } }

    #[classattr]
    #[allow(non_snake_case)]
    fn ORGANIZATION_NAME() -> Self { Self { inner: EntityType::OrganizationName } }

    #[classattr]
    #[allow(non_snake_case)]
    fn ADDRESS() -> Self { Self { inner: EntityType::Address } }

    #[classattr]
    #[allow(non_snake_case)]
    fn PHONE_NUMBER() -> Self { Self { inner: EntityType::PhoneNumber } }

    #[classattr]
    #[allow(non_snake_case)]
    fn EMAIL() -> Self { Self { inner: EntityType::Email } }

    #[classattr]
    #[allow(non_snake_case)]
    fn WEBSITE() -> Self { Self { inner: EntityType::Website } }

    #[classattr]
    #[allow(non_snake_case)]
    fn CONTRACT() -> Self { Self { inner: EntityType::Contract } }

    #[classattr]
    #[allow(non_snake_case)]
    fn CONTRACT_PARTY() -> Self { Self { inner: EntityType::ContractParty } }

    #[classattr]
    #[allow(non_snake_case)]
    fn CONTRACT_TERM() -> Self { Self { inner: EntityType::ContractTerm } }

    #[classattr]
    #[allow(non_snake_case)]
    fn EFFECTIVE_DATE() -> Self { Self { inner: EntityType::EffectiveDate } }

    #[classattr]
    #[allow(non_snake_case)]
    fn CONTRACT_VALUE() -> Self { Self { inner: EntityType::ContractValue } }

    #[classattr]
    #[allow(non_snake_case)]
    fn SIGNATURE() -> Self { Self { inner: EntityType::Signature } }

    #[classattr]
    #[allow(non_snake_case)]
    fn DATE() -> Self { Self { inner: EntityType::Date } }

    #[classattr]
    #[allow(non_snake_case)]
    fn AMOUNT() -> Self { Self { inner: EntityType::Amount } }

    #[classattr]
    #[allow(non_snake_case)]
    fn QUANTITY() -> Self { Self { inner: EntityType::Quantity } }

    #[classattr]
    #[allow(non_snake_case)]
    fn PERCENTAGE() -> Self { Self { inner: EntityType::Percentage } }

    /// Create a custom entity type. Raises ``ValueError`` for empty or whitespace-only names.
    #[staticmethod]
    fn custom(name: &str) -> PyResult<Self> {
        if name.trim().is_empty() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Custom entity type name must not be empty or whitespace-only",
            ));
        }
        Ok(Self { inner: EntityType::Custom(name.to_string()) })
    }

    /// The canonical uppercase name of this entity type.
    #[getter]
    fn name(&self) -> String {
        match &self.inner {
            EntityType::Text => "TEXT".to_string(),
            EntityType::Image => "IMAGE".to_string(),
            EntityType::Table => "TABLE".to_string(),
            EntityType::Heading => "HEADING".to_string(),
            EntityType::Paragraph => "PARAGRAPH".to_string(),
            EntityType::List => "LIST".to_string(),
            EntityType::PageNumber => "PAGE_NUMBER".to_string(),
            EntityType::Header => "HEADER".to_string(),
            EntityType::Footer => "FOOTER".to_string(),
            EntityType::Invoice => "INVOICE".to_string(),
            EntityType::InvoiceNumber => "INVOICE_NUMBER".to_string(),
            EntityType::CustomerName => "CUSTOMER_NAME".to_string(),
            EntityType::LineItem => "LINE_ITEM".to_string(),
            EntityType::TotalAmount => "TOTAL_AMOUNT".to_string(),
            EntityType::TaxAmount => "TAX_AMOUNT".to_string(),
            EntityType::DueDate => "DUE_DATE".to_string(),
            EntityType::PaymentAmount => "PAYMENT_AMOUNT".to_string(),
            EntityType::PersonName => "PERSON_NAME".to_string(),
            EntityType::OrganizationName => "ORGANIZATION_NAME".to_string(),
            EntityType::Address => "ADDRESS".to_string(),
            EntityType::PhoneNumber => "PHONE_NUMBER".to_string(),
            EntityType::Email => "EMAIL".to_string(),
            EntityType::Website => "WEBSITE".to_string(),
            EntityType::Contract => "CONTRACT".to_string(),
            EntityType::ContractParty => "CONTRACT_PARTY".to_string(),
            EntityType::ContractTerm => "CONTRACT_TERM".to_string(),
            EntityType::EffectiveDate => "EFFECTIVE_DATE".to_string(),
            EntityType::ContractValue => "CONTRACT_VALUE".to_string(),
            EntityType::Signature => "SIGNATURE".to_string(),
            EntityType::Date => "DATE".to_string(),
            EntityType::Amount => "AMOUNT".to_string(),
            EntityType::Quantity => "QUANTITY".to_string(),
            EntityType::Percentage => "PERCENTAGE".to_string(),
            EntityType::Custom(s) => s.clone(),
        }
    }

    fn __repr__(&self) -> String {
        let name = match &self.inner {
            EntityType::Text => "TEXT",
            EntityType::Image => "IMAGE",
            EntityType::Table => "TABLE",
            EntityType::Heading => "HEADING",
            EntityType::Paragraph => "PARAGRAPH",
            EntityType::List => "LIST",
            EntityType::PageNumber => "PAGE_NUMBER",
            EntityType::Header => "HEADER",
            EntityType::Footer => "FOOTER",
            EntityType::Invoice => "INVOICE",
            EntityType::InvoiceNumber => "INVOICE_NUMBER",
            EntityType::CustomerName => "CUSTOMER_NAME",
            EntityType::LineItem => "LINE_ITEM",
            EntityType::TotalAmount => "TOTAL_AMOUNT",
            EntityType::TaxAmount => "TAX_AMOUNT",
            EntityType::DueDate => "DUE_DATE",
            EntityType::PaymentAmount => "PAYMENT_AMOUNT",
            EntityType::PersonName => "PERSON_NAME",
            EntityType::OrganizationName => "ORGANIZATION_NAME",
            EntityType::Address => "ADDRESS",
            EntityType::PhoneNumber => "PHONE_NUMBER",
            EntityType::Email => "EMAIL",
            EntityType::Website => "WEBSITE",
            EntityType::Contract => "CONTRACT",
            EntityType::ContractParty => "CONTRACT_PARTY",
            EntityType::ContractTerm => "CONTRACT_TERM",
            EntityType::EffectiveDate => "EFFECTIVE_DATE",
            EntityType::ContractValue => "CONTRACT_VALUE",
            EntityType::Signature => "SIGNATURE",
            EntityType::Date => "DATE",
            EntityType::Amount => "AMOUNT",
            EntityType::Quantity => "QUANTITY",
            EntityType::Percentage => "PERCENTAGE",
            EntityType::Custom(s) => return format!("EntityType.custom({:?})", s),
        };
        format!("EntityType.{}", name)
    }
}

// ── PyRelationType ────────────────────────────────────────────────────────

/// Relationship type between semantic entities.
///
/// Standard variants: ``CONTAINS``, ``IS_PART_OF``, ``REFERENCES``,
/// ``FOLLOWS``, ``PRECEDES``.
/// Custom: ``RelationType.custom("MyRelation")``.
#[pyclass(name = "RelationType", frozen, from_py_object, eq)]
#[derive(Clone, PartialEq, Eq)]
pub struct PyRelationType {
    pub inner: RelationType,
}

#[pymethods]
impl PyRelationType {
    #[classattr]
    #[allow(non_snake_case)]
    fn CONTAINS() -> Self { Self { inner: RelationType::Contains } }

    #[classattr]
    #[allow(non_snake_case)]
    fn IS_PART_OF() -> Self { Self { inner: RelationType::IsPartOf } }

    #[classattr]
    #[allow(non_snake_case)]
    fn REFERENCES() -> Self { Self { inner: RelationType::References } }

    #[classattr]
    #[allow(non_snake_case)]
    fn FOLLOWS() -> Self { Self { inner: RelationType::Follows } }

    #[classattr]
    #[allow(non_snake_case)]
    fn PRECEDES() -> Self { Self { inner: RelationType::Precedes } }

    /// Create a custom relation type. Raises ``ValueError`` for empty or whitespace-only names.
    #[staticmethod]
    fn custom(name: &str) -> PyResult<Self> {
        if name.trim().is_empty() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Custom relation type name must not be empty or whitespace-only",
            ));
        }
        Ok(Self { inner: RelationType::Custom(name.to_string()) })
    }

    /// The canonical uppercase name of this relation type.
    #[getter]
    fn name(&self) -> String {
        match &self.inner {
            RelationType::Contains => "CONTAINS".to_string(),
            RelationType::IsPartOf => "IS_PART_OF".to_string(),
            RelationType::References => "REFERENCES".to_string(),
            RelationType::Follows => "FOLLOWS".to_string(),
            RelationType::Precedes => "PRECEDES".to_string(),
            RelationType::Custom(s) => s.clone(),
        }
    }

    fn __repr__(&self) -> String {
        let name = match &self.inner {
            RelationType::Contains => "CONTAINS",
            RelationType::IsPartOf => "IS_PART_OF",
            RelationType::References => "REFERENCES",
            RelationType::Follows => "FOLLOWS",
            RelationType::Precedes => "PRECEDES",
            RelationType::Custom(s) => return format!("RelationType.custom({:?})", s),
        };
        format!("RelationType.{}", name)
    }
}

// ── PyExportFormat ────────────────────────────────────────────────────────

/// Export format for serialising an EntityMap.
///
/// Variants: ``JSON``, ``JSON_LD``, ``XML``.
#[pyclass(name = "ExportFormat", frozen, from_py_object, eq)]
#[derive(Clone, Copy, PartialEq)]
pub struct PyExportFormat {
    pub inner: ExportFormat,
}

#[pymethods]
impl PyExportFormat {
    #[classattr]
    const JSON: Self = Self { inner: ExportFormat::Json };

    #[classattr]
    const JSON_LD: Self = Self { inner: ExportFormat::JsonLd };

    #[classattr]
    const XML: Self = Self { inner: ExportFormat::Xml };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            ExportFormat::Json => "JSON",
            ExportFormat::JsonLd => "JSON_LD",
            ExportFormat::Xml => "XML",
        };
        format!("ExportFormat.{}", name)
    }
}

// ── PyBoundingBox ─────────────────────────────────────────────────────────

/// Axis-aligned bounding box for a region on a PDF page.
///
/// Constructor: ``BoundingBox(x, y, width, height, page)``.
/// Computed properties: ``right``, ``top``, ``area``.
/// Method: ``intersects(other)``.
/// Raises ``ValueError`` for negative width or height.
#[pyclass(name = "BoundingBox", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyBoundingBox {
    pub inner: BoundingBox,
}

#[pymethods]
impl PyBoundingBox {
    #[new]
    fn new(x: f32, y: f32, width: f32, height: f32, page: u32) -> PyResult<Self> {
        if width < 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "BoundingBox width must not be negative",
            ));
        }
        if height < 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "BoundingBox height must not be negative",
            ));
        }
        Ok(Self { inner: BoundingBox::new(x, y, width, height, page) })
    }

    #[getter]
    fn x(&self) -> f32 { self.inner.x }

    #[getter]
    fn y(&self) -> f32 { self.inner.y }

    #[getter]
    fn width(&self) -> f32 { self.inner.width }

    #[getter]
    fn height(&self) -> f32 { self.inner.height }

    #[getter]
    fn page(&self) -> u32 { self.inner.page }

    #[getter]
    fn right(&self) -> f32 { self.inner.right() }

    #[getter]
    fn top(&self) -> f32 { self.inner.top() }

    #[getter]
    fn area(&self) -> f32 { self.inner.area() }

    fn intersects(&self, other: &PyBoundingBox) -> bool {
        self.inner.intersects(&other.inner)
    }

    fn __repr__(&self) -> String {
        format!(
            "BoundingBox(x={}, y={}, width={}, height={}, page={})",
            self.inner.x, self.inner.y, self.inner.width, self.inner.height, self.inner.page
        )
    }
}

// ── PyEntityMetadata ──────────────────────────────────────────────────────

/// Metadata associated with a semantic entity.
///
/// Builder pattern: chain ``with_property()``, ``with_confidence()``,
/// ``with_schema()`` calls on a ``EntityMetadata()`` instance.
#[pyclass(name = "EntityMetadata", from_py_object)]
#[derive(Clone)]
pub struct PyEntityMetadata {
    pub inner: EntityMetadata,
}

#[pymethods]
impl PyEntityMetadata {
    #[new]
    fn new() -> Self {
        Self { inner: EntityMetadata::new() }
    }

    fn with_property(self_: PyRef<'_, Self>, key: &str, value: &str) -> Self {
        Self { inner: self_.inner.clone().with_property(key, value) }
    }

    fn with_confidence(self_: PyRef<'_, Self>, confidence: f32) -> Self {
        Self { inner: self_.inner.clone().with_confidence(confidence) }
    }

    fn with_schema(self_: PyRef<'_, Self>, schema: &str) -> Self {
        Self { inner: self_.inner.clone().with_schema(schema) }
    }

    fn __repr__(&self) -> String {
        let confidence = match self.inner.confidence {
            Some(c) => format!("{}", c),
            None => "None".to_string(),
        };
        format!(
            "EntityMetadata(properties={}, confidence={})",
            self.inner.properties.len(),
            confidence,
        )
    }
}

// ── PySemanticEntity ──────────────────────────────────────────────────────

/// Enhanced semantic entity with bounding box, content, metadata and relationships.
///
/// Constructor: ``SemanticEntity(id, entity_type, bounds)``.
/// Builder methods: ``with_content()``, ``with_metadata()``, ``with_relationship()``.
#[pyclass(name = "SemanticEntity", from_py_object)]
#[derive(Clone)]
pub struct PySemanticEntity {
    pub inner: SemanticEntity,
}

#[pymethods]
impl PySemanticEntity {
    #[new]
    fn new(id: &str, entity_type: &PyEntityType, bounds: &PyBoundingBox) -> Self {
        Self {
            inner: SemanticEntity::new(
                id.to_string(),
                entity_type.inner.clone(),
                bounds.inner.clone(),
            ),
        }
    }

    fn with_content(self_: PyRef<'_, Self>, content: &str) -> Self {
        Self { inner: self_.inner.clone().with_content(content) }
    }

    fn with_metadata(self_: PyRef<'_, Self>, meta: &PyEntityMetadata) -> Self {
        Self { inner: self_.inner.clone().with_metadata(meta.inner.clone()) }
    }

    fn with_relationship(
        self_: PyRef<'_, Self>,
        target_id: &str,
        relation_type: &PyRelationType,
    ) -> Self {
        Self {
            inner: self_.inner.clone().with_relationship(
                target_id.to_string(),
                relation_type.inner.clone(),
            ),
        }
    }

    #[getter]
    fn id(&self) -> &str { &self.inner.id }

    #[getter]
    fn content(&self) -> &str { &self.inner.content }

    /// The entity type of this semantic entity.
    #[getter]
    fn entity_type(&self) -> PyEntityType {
        PyEntityType { inner: self.inner.entity_type.clone() }
    }

    fn __repr__(&self) -> String {
        format!("SemanticEntity(id={:?})", self.inner.id)
    }
}

// ── PyEntity ──────────────────────────────────────────────────────────────

/// Legacy semantic entity with simple bounding-box tuple.
///
/// Constructor: ``Entity(id, entity_type, bounds, page)``
/// where ``bounds`` is a ``(x, y, width, height)`` tuple of floats.
#[pyclass(name = "Entity", from_py_object)]
#[derive(Clone)]
pub struct PyEntity {
    pub inner: Entity,
}

#[pymethods]
impl PyEntity {
    #[new]
    fn new(
        id: &str,
        entity_type: &PyEntityType,
        bounds: (f64, f64, f64, f64),
        page: usize,
    ) -> Self {
        Self {
            inner: Entity::new(
                id.to_string(),
                entity_type.inner.clone(),
                bounds,
                page,
            ),
        }
    }

    #[getter]
    fn id(&self) -> &str { &self.inner.id }

    #[getter]
    fn page(&self) -> usize { self.inner.page }

    /// The entity type of this entity.
    #[getter]
    fn entity_type(&self) -> PyEntityType {
        PyEntityType { inner: self.inner.entity_type.clone() }
    }

    fn __repr__(&self) -> String {
        format!("Entity(id={:?}, page={})", self.inner.id, self.inner.page)
    }
}

// ── PyEntityMap ───────────────────────────────────────────────────────────

/// Container of semantic entities organised by page.
///
/// Methods: ``add_entity()``, ``entities_by_type()``,
/// ``entities_on_page()``, ``to_json()``, ``to_json_ld()``, ``to_format()``.
#[pyclass(name = "EntityMap", from_py_object)]
#[derive(Clone)]
pub struct PyEntityMap {
    pub inner: EntityMap,
}

#[pymethods]
impl PyEntityMap {
    #[new]
    fn new() -> Self {
        Self { inner: EntityMap::new() }
    }

    fn add_entity(&mut self, entity: &PyEntity) {
        self.inner.add_entity(entity.inner.clone());
    }

    fn entities_by_type(&self, entity_type: &PyEntityType) -> Vec<PyEntity> {
        self.inner
            .entities_by_type(entity_type.inner.clone())
            .into_iter()
            .map(|e| PyEntity { inner: e.clone() })
            .collect()
    }

    fn entities_on_page(&self, page: usize) -> Vec<PyEntity> {
        self.inner
            .entities_on_page(page)
            .map(|v| v.iter().map(|e| PyEntity { inner: e.clone() }).collect())
            .unwrap_or_default()
    }

    fn to_json(&self) -> PyResult<String> {
        self.inner
            .to_json()
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    fn to_json_ld(&self) -> PyResult<String> {
        self.inner
            .to_json_ld()
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    /// Serialise to the given export format.
    ///
    /// Supports ``ExportFormat.JSON`` and ``ExportFormat.JSON_LD``.
    /// Raises ``NotImplementedError`` for ``ExportFormat.XML``.
    fn to_format(&self, format: &PyExportFormat) -> PyResult<String> {
        match format.inner {
            ExportFormat::Json => self.to_json(),
            ExportFormat::JsonLd => self.to_json_ld(),
            ExportFormat::Xml => Err(pyo3::exceptions::PyNotImplementedError::new_err(
                "XML export is not yet implemented",
            )),
        }
    }

    fn __repr__(&self) -> String {
        let total: usize = self.inner.pages.values().map(|v| v.len()).sum();
        let page_count = self.inner.pages.len();
        format!("EntityMap(entities={}, pages={})", total, page_count)
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyEntityType>()?;
    m.add_class::<PyRelationType>()?;
    m.add_class::<PyExportFormat>()?;
    m.add_class::<PyBoundingBox>()?;
    m.add_class::<PyEntityMetadata>()?;
    m.add_class::<PySemanticEntity>()?;
    m.add_class::<PyEntity>()?;
    m.add_class::<PyEntityMap>()?;
    Ok(())
}
