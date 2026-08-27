# TurkDemy Agent Development Contract

TurkDemy uses spec-driven development (SDD). The repository, not a chat prompt,
is the source of truth for approved product behavior.

## Required reading order

Before changing behavior:

1. Read `docs/product/terminology.md`.
2. Read `docs/product/business-rules.md`.
3. Read `docs/architecture/overview.md`.
4. Read `docs/architecture/domain-model.md`.
5. Read `docs/architecture/permissions.md`.
6. Read the relevant `docs/specs/<capability>/spec.md`.
7. Read its `design.md`.
8. Implement only approved items in its `tasks.md`.

Also read any ADR referenced by the design.

## Change-request triage

Before editing code for a reported issue/request, classify it using
`docs/changes/README.md`:

- `BUG` — code violates an existing approved/baselined requirement;
- `CHANGE` — desired behavior changes an existing requirement;
- `FEATURE` — new behavior/capability;
- `UI` — non-behavioral visual/copy refinement;
- `REFACTOR` — implementation/design change, behavior unchanged;
- `DISCOVERY` — idea needs product decisions before specification;
- `CONFLICT` — code/spec disagree and intended behavior is unresolved.

For non-trivial work, create the corresponding record under `docs/changes/`.

A confirmed BUG does not require changing the product spec. Add a regression
test, fix code to the existing requirement, verify, and update traceability.

A CHANGE or FEATURE must not enter implementation until its behavioral spec is
approved. DISCOVERY and CONFLICT items must not enter dependent implementation
while relevant decisions remain OPEN.

Do not classify an information-architecture, permission, entity-scope, or
workflow change as a cosmetic UI change.

## SDD workflow

Every behavioral change follows:

`proposal -> spec -> design -> tasks -> implementation -> verification`

Do not silently combine these stages for a new or ambiguous feature.

### Proposal/spec stage

- Define actors, goal, scope, requirements, acceptance criteria, edge cases,
  permissions and non-goals.
- Give requirements stable IDs.
- Do not encode accidental implementation behavior as a requirement.
- Mark unresolved decisions `OPEN` and do not implement behavior that depends on
  them.

### Design stage

- Map approved requirements to models, services, routes, UI and side effects.
- State transaction boundaries and authorization checks.
- Reuse existing domain services and invariants.
- Architecture changes require an ADR.

### Task stage

- Every task references one or more requirement IDs.
- Keep tasks small enough to implement and verify independently.
- Include tests and documentation work.

### Implementation stage

- Do not invent domain behavior not supported by an approved requirement.
- Do not weaken a spec to make existing code pass.
- If code and spec conflict, stop and report the conflict.
- Preserve organization scoping and privacy-safe access behavior.
- Keep business rules in domain/services rather than duplicating them across views.

### Verification stage

Every behavioral requirement needs tests at the appropriate level. Run:

```bash
make format
make check
```

Update the capability's `traceability.md` before declaring work complete.

## Global invariants

- A `LeadProgramInterest` is exploratory; it is not an `Application`.
- Formal applications are created for a `Student` and a concrete
  `ProgramOffering`.
- Lead finalization must not leave a partially converted Student workflow.
- Agent assignment is responsibility, not organization-level authorization.
- Agent workspace data is scoped to the active Agent organization.
- A user may belong to multiple Agent organizations.
- Messaging uses generic subject-scoped conversations.
- Unread state is per conversation, user and participant role.
- Student documents are reusable; application documents are application-scoped.
- Audit history must not be discarded to simplify a workflow.

## Change classification

A change to behavior requires a spec update. A change to implementation without
behavioral impact may update only `design.md`/tasks. A cross-cutting architectural
decision requires an ADR. Pure formatting/refactoring requires tests to remain
green but does not require a new product requirement.

## Completion definition

A capability task is complete only when:

- implementation matches the approved spec;
- acceptance criteria are tested;
- authorization and negative paths are tested;
- docs/design match the implementation;
- traceability is updated;
- `make check` passes.
