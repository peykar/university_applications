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

## Optional secondary/context columns

`NAV-012` makes secondary workspace columns content-driven rather than structural placeholders. A Request context sidebar is rendered only when it has meaningful document or preference context. If no such context exists, the same full-width layout used by intentionally sidebar-free tabs is applied, so the central workspace expands into the released column. The rule is shared with Agent workspace layouts: any future or existing optional Agent context sidebar must follow the same collapse behavior instead of leaving an empty right rail.


## Agent desktop canvas and released context space

`NAV-013` clarifies the desktop geometry implied by `NAV-012`. The shared visual system does not require Agent operational pages to stop at the public site's 1160px content boundary. Above the desktop breakpoint, the Agent page shell keeps its inline-start edge aligned with the standard site container, but may extend toward the inline-end viewport edge up to a 1496px workspace cap. This approximates the standard workspace width plus a 310px context rail and its 26px gap.

As a result, top-level Agent pages with no context rail (Overview, Applicants, Applications, TODOs, Communications, and Messages) use the released width for their main content. Applicant/Application entity pages that have a real secondary rail can use the same canvas without changing the visual language. At 1160px and below, the existing shared responsive workspace rules remain authoritative.
