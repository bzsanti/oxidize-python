"""Strict consumer for the complete editor input/plan/result boundary."""
from oxidize_pdf import (
    IncrementalTaggedPdfEditor, TaggedPdfMutation, TaggedPdfObjectRef, PdfValue,
    TaggedPdfValidationOptions, TaggedPdfLimits, TaggedPdfEditPlan,
    TaggedPdfMutationReport, TaggedPdfValidationReport, TaggedPdfChangedObjectKind,
)

def edit(source: bytes) -> bytes:
    target = TaggedPdfObjectRef(6, 7)
    editor = IncrementalTaggedPdfEditor(source).with_validation_options(
        TaggedPdfValidationOptions(TaggedPdfLimits(max_objects=1000)))
    prepared = editor.with_document_language('es').with_recovered_indexes()
    objects: list[TaggedPdfObjectRef] = prepared.preparation_objects()
    validation: TaggedPdfValidationReport = prepared.preflight()
    mutations = [
        TaggedPdfMutation.create_element(target, 'Div', {'Vendor': PdfValue.integer(3)}, 0),
        TaggedPdfMutation.set_element_attribute(target, 'T', PdfValue.string(b'title')),
        TaggedPdfMutation.reparent_element(target, TaggedPdfObjectRef(5, 0)),
        TaggedPdfMutation.associate_mcid(target, TaggedPdfObjectRef(3, 0), 0),
        TaggedPdfMutation.set_parent_tree_entry(0, PdfValue.array([PdfValue.reference(6, 7)])),
    ]
    plan: TaggedPdfEditPlan = editor.plan(mutations)
    result: TaggedPdfMutationReport = editor.apply(mutations)
    kind: TaggedPdfChangedObjectKind = plan.changed_objects[0].kind
    assert kind == TaggedPdfChangedObjectKind.StructureElement
    assert objects and validation.tagged and result.validation_after.tagged
    return result.pdf_bytes
