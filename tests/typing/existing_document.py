from oxidize_pdf import (
    ExistingDocumentPolicy, ExistingDocumentMergeInput, PageRange, PageMutation,
    SemanticPreservationReport, PageMutationReport, plan_merge_existing_pdfs,
    plan_pdf_page_mutations,
)

def check(input_path: str) -> int:
    report: SemanticPreservationReport = plan_merge_existing_pdfs(
        [ExistingDocumentMergeInput(input_path, PageRange.all())],
        ExistingDocumentPolicy.preserve_base(page_labels_first_input_wins=True),
    )
    mutation: PageMutationReport = plan_pdf_page_mutations(
        input_path, [PageMutation.rotate(0, 90)]
    )
    if report.plan.incremental is not None:
        for number, generation in report.plan.incremental.replaced_objects:
            assert number >= 0 and generation >= 0
    return report.plan.page_count + mutation.page_count
