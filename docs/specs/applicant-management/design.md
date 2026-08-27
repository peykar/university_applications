# Applicant management — technical design

Status: BASELINED

## Design mapping

- `Lead` is the provisional Applicant aggregate.
- Customer ownership starts from `Lead.user`.
- Agent access starts from active-Agent-scoped Lead queryset.
- Agent edits use the shared applicant activity recorder.
- Entity-level navigation is implemented by applicant header/nav partials.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.


## Dedicated Agent edit page

Agent Applicant editing uses the dedicated
`/agent/applicants/<lead_id>/edit/` GET/POST page. The page reuses
`AgentLeadEditForm`, resolves the Lead through the active-Agent scope, keeps
invalid form errors in-page, and records successful changes through the shared
Applicant activity service. It is intentionally not a modal because the form is
a long structured workflow.

## Internal notes boundary

`Lead.notes` is the current private Agent case summary. It is operational
case-management data, not Applicant/person profile data.

- `AgentLeadEditForm` excludes `notes`.
- Applicant Overview is the canonical visible home for the current internal
  note and labels it Private.
- Active, non-closed Lead notes are edited through the dedicated
  `applicant_internal_notes` POST workflow/modal.
- Note changes create `INTERNAL_NOTES_UPDATED` activity with
  `is_customer_visible=False`.
- Customer Applicant pages never render the internal note.
- Finalized Lead notes remain visible as historical Agent context but are
  read-only; ongoing person/case maintenance belongs to the Student workflow.
