# Navigation and workspace information architecture — technical design

Status: BASELINED

## Design mapping

- Shared workspace base templates provide L2 navigation.
- Applicant/Application header/nav partials provide L3.
- Agent desktop shell may use a wider content container than public catalogue.
- See `docs/architecture/navigation.md`.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.

## Shared footer workspace links

The footer mirrors the current customer workspace vocabulary instead of legacy student-dashboard terminology. Its workspace group is **My TurkDemy**. Authenticated users enter **My Requests** or **Messages** directly; signed-out visitors receive the Login entry. This keeps global footer navigation consistent with the customer sidebar and login redirect without exposing internal Lead/Student/Application lifecycle language.
