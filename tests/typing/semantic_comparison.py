from oxidize_pdf import (
    compare_pdfs_semantically, SemanticComparisonLimits, SemanticComparisonOptions,
    SemanticComparisonResult, SemanticDifferenceClass, RevisionObjectChangeKind,
)

def compare(left: bytes, right: bytes) -> bool:
    limits = SemanticComparisonLimits(max_objects=100, max_depth=32,
        max_decoded_stream_bytes=100000, max_canonical_bytes=1000000,
        max_extracted_text_bytes=10000, max_unreachable_objects=20, max_revisions=10)
    result: SemanticComparisonResult = compare_pdfs_semantically(left, right, SemanticComparisonOptions(limits))
    for difference in result.differences:
        kind: SemanticDifferenceClass = difference.class_
        path: str = difference.path
        assert path and difference.description and kind != SemanticDifferenceClass.Security
    for revision in result.right_revisions:
        digest: bytes = revision.semantic_fingerprint
        offset: int = revision.xref_offset
        assert digest and offset >= 0 and revision.index >= 0
        for item in revision.object_changes:
            change: RevisionObjectChangeKind = item.kind
            assert item.object_number >= 0 and item.generation >= 0
            assert change in (RevisionObjectChangeKind.Added, RevisionObjectChangeKind.Replaced, RevisionObjectChangeKind.Freed)
    pairs: list[tuple[tuple[int, int], tuple[int, int]]] = result.semantically_equivalent_objects
    unreachable: list[tuple[int, int]] = result.left_unreachable_objects + result.right_unreachable_objects
    assert pairs or unreachable or result.left_revisions
    return result.semantically_equal
