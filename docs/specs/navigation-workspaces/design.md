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

## Mobile customer workspace navigation

`NAV-010` replaces the narrow-screen max-content horizontal strip for the customer sidebar with an adaptive grid. `repeat(auto-fit, minmax(...))` keeps all configured actions visible, allows long support labels to wrap, preserves the unread badge, and automatically redistributes space when WhatsApp is not configured.

## Shared customer / Agent workspace visual system

`NAV-011` makes the outer workspace presentation deliberately shared rather than maintaining an Agent-only shell variant. `templates/customer/base.html` and `templates/agents/base.html` both use `workspace-shell`, `workspace-sidebar`, `workspace-sidebar-nav`, `workspace-main`, and the shared entity-header/navigation components where applicable. The Agent base uses the same normal page-heading hierarchy as customer workspace pages and inherits the standard site container and page-shell spacing instead of overriding them with a 1500px Agent-only canvas.

This is visual-system alignment, not an information-architecture merge. The Agent sidebar keeps active organization identity and switching, and operational Applicant/Application pages retain their Agent-only actions and denser panels/tables.
