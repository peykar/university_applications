# Applicant finalization — technical design

Status: BASELINED

## Design mapping

- Canonical service is the Lead conversion/finalization service.
- Treat validation + Student creation + approved document copy + Lead transition
  as one workflow transaction boundary.
- UI starts from Applicant context with `Create Student Record` and uses a dedicated full-page form.
- See ADR-001.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.


## Audit semantics

Validation occurs inside the atomic finalization operation. Successful
finalization persists `validated_by` and `validated_at`, then records the
`FINALIZED` LeadActivity and established system message. A separate intermediate
`VALIDATED` activity/message is intentionally not emitted because there is no
standalone validated workflow phase.

## Create Student Record page

- `applicant_finalize` accepts GET and POST and renders `templates/agents/student_record_create.html`.
- `StudentRecordConversionForm` is prefilled from Lead fields but validates against the Student model.
- All Lead documents are listed. Verified documents are checked on GET; pending/replacement documents are unchecked. POST selections are preserved on validation failure.
- Checking an unverified document promotes it to APPROVED within the same successful transaction before creating/reusing its `StudentDocument`. Unchecking a verified document does not change Lead review state.
- All discussed `LeadProgramInterest` rows are listed. Program selection is optional (zero or more). Each checked row requires an active offering. Existing active discussed offerings are preselected but remain editable.
- `finalize_lead()` accepts reviewed Student data, selected document IDs and zero-or-more `(LeadProgramInterest, ProgramOffering)` selections.
- The service validates selections before durable conversion, creates the Student and any draft Applications, transfers selected documents, then finalizes the Lead. Database changes share one `transaction.atomic()` boundary.
- `LeadDocument.converted_student_document` remains the idempotent document-conversion bridge. `LeadProgramInterest` has no persistent Application pointer; application creation uses the discussed interest only as transient UI/service input.
- Django admin bulk finalization remains unavailable because the workflow requires per-applicant review and selections.
