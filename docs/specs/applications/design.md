# Formal applications — technical design

Status: BASELINED

## Design mapping

- Canonical service: `create_student_application()`.
- Model chain: Student → Application → ProgramOffering → Program → University.
- Agent application queryset is active-Agent scoped.
- Customer application detail checks ownership.
- Requirements are not yet a complete standalone domain model.
- See ADR-004 and ADR-005.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.

## Initial applications at Lead finalization

`create_student_application()` remains the canonical Application creation service.
Lead finalization supplies the newly created/reused Student plus each explicitly
selected concrete active offering. The service creates each record in DRAFT state,
snapshots canonical structured tuition and any structured deposit, prevents active
duplicates, and does not persist a LeadProgramInterest relation. Missing active
amount-bearing tuition raises validation and the outer finalization transaction
rolls back. Nested atomic blocks participate in that outer transaction.
