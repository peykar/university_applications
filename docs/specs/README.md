# TurkDemy Specifications

This directory is the canonical home for behavioral capability specifications.

Each capability contains:

- `spec.md` — WHAT and WHY: actors, requirements, acceptance criteria, edge cases.
- `design.md` — HOW: domain mapping, services, permissions, routes, UI, side effects.
- `tasks.md` — implementation checklist referencing requirement IDs.
- `traceability.md` — requirement → implementation → test mapping.

## Lifecycle

1. Draft/change `spec.md`.
2. Resolve `OPEN` decisions.
3. Mark the spec approved.
4. Create/update `design.md`.
5. Create tasks.
6. Implement tasks.
7. Run verification.
8. Update traceability.

Specs describe capabilities and workflows, not individual Django models.

## Requirement IDs

Prefixes are stable:

| Prefix | Capability |
|---|---|
| AUTH | Identity & authentication |
| AGT | Agent organizations/workspace |
| APL | Applicant management |
| ASN | Agent assignment |
| PREF | Study preferences |
| PRG | Program interests/recommendations |
| DOC | Document management |
| FIN | Applicant finalization |
| STU | Student management |
| APP | Applications |
| COM | Communication log |
| TODO | TODO management |
| MSG | Messaging |
| AUD | Activity/audit |
| CAT | University/program catalogue |
| MAIL | Email/notifications |
| PERM | Permissions |
| NAV | Navigation/workspaces |
| CRQ | Customer requests |

Do not renumber an accepted requirement merely because another requirement is
inserted. Retired IDs remain reserved.

## Status vocabulary

- `BASELINED` — extracted from established intended project behavior.
- `DRAFT` — under discussion.
- `APPROVED` — accepted for implementation.
- `OPEN` — unresolved decision blocks dependent implementation.
- `DEPRECATED` — retained for historical traceability.
