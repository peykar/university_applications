# TurkDemy Agent Development Contract

TurkDemy uses spec-driven development (SDD). The repository, not a chat prompt,
is the source of truth for approved product behavior.

This file is the standing development contract for ChatGPT and any other coding
agent working on this repository. A user request tells the agent *what change is
wanted*; this contract defines *how that change must be made*.

## Source-of-truth precedence

When sources disagree, use this order and do not silently choose the most
convenient behavior:

1. explicit product/domain rules and accepted business decisions;
2. accepted ADRs and cross-cutting architecture constraints;
3. the owning capability's approved/baselined `spec.md`;
4. that capability's `design.md`;
5. approved implementation tasks;
6. tests;
7. implementation code;
8. UI behavior/copy and older flat documentation.

Code and tests are evidence of current behavior, not authority to override an
approved requirement. When an explicit user instruction intentionally changes
approved behavior, process it as a CHANGE/FEATURE and update the higher-level
artifacts before or together with implementation.

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

## ChatGPT request semantics

ChatGPT is expected to execute complete repository changes, not merely propose
patches, when the user asks to "do", "fix", "implement", "add", "change" or
otherwise clearly requests implementation.

- If the requested behavior is already defined by an approved/baselined spec,
  implement it as a BUG or the appropriate implementation task.
- If the user clearly requests new or changed behavior and there are no material
  unresolved product decisions, the implementation request counts as approval
  to update the required spec/design/tasks and implement them in the same work
  session. Record the change and preserve traceability.
- If materially different domain choices remain possible, create/record a
  DISCOVERY or CONFLICT and do not invent the choice. Prefer implementing all
  unblocked parts rather than changing unrelated behavior.
- Never use existing code behavior alone as proof that a domain decision was
  intended.

The agent should therefore be able to accept business-level requests such as
"allow completed todos to be reopened" without requiring the user to describe
models, views, URLs, or tests.

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
- Use stable requirement IDs and never renumber accepted IDs.

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

For each changed behavioral requirement, trace at least:

`requirement ID -> design/task -> implementation -> automated test`

When a UI action is part of the requirement, verification must cover the actual
route/form/action wiring as well as the lower-level service behavior where
practical. A service test alone is insufficient evidence that a visible button
or modal works.



## Public-page SEO gate

Every change that adds or modifies a public page MUST include an SEO impact review
as part of the same change. SEO is not a later cleanup task.

For each affected public page, explicitly evaluate and update as applicable:

- localized document title and meta description;
- canonical URL identity;
- reciprocal `hreflang` alternates and `x-default`;
- robots/indexability policy;
- sitemap inclusion/exclusion;
- Open Graph/social metadata and representative image;
- structured data when the page represents a supported entity/content type;
- semantic headings, crawlable content and meaningful image alternative text;
- internal links and URL stability;
- filter, query-string and pagination duplicate-content behavior.

If an item is not applicable, the implementation/change record should make that
clear rather than silently omitting the review. Public-page tasks and tests MUST
include SEO acceptance coverage appropriate to the affected surface.

## Global invariants

- A `LeadProgramInterest` is exploratory; it is not an `Application` until an Agent explicitly selects it for conversion.
- Lead finalization requires at least one selected discussed interest and creates linked DRAFT Applications atomically with the Student transition.
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

## Repository documentation duties

Documentation is part of the implementation, not optional follow-up work.

- Keep `docs/` synchronized with every behavior, model, workflow, permission,
  configuration, operational, or UI change that makes existing documentation
  inaccurate.
- Update the owning capability's spec/design/tasks/traceability as required by
  the SDD classification.
- Update relevant flat operational/user-flow documentation when it remains an
  active entry point for developers or operators.
- Add a concise entry to `docs/changelog.md` for completed user-visible or
  architectural changes.
- Do not create competing documentation for a concept that already has a
  canonical home; link to the canonical document instead.

## Delivery contract

When working from an uploaded project archive, ChatGPT must return the complete
updated project archive after every repository change.

- Do not return only snippets or a patch as the final deliverable unless the
  user explicitly asks for that instead.
- Preserve the project directory structure and existing files.
- Exclude local virtual environments, caches, build output and secrets from the
  delivered archive.
- Report which checks were actually run and whether they passed; never claim a
  check passed when it was not executed.
- If an environment/dependency problem prevents a check from running, report the
  blocker and still run every independent check that can run safely.

## Completion definition

A capability task is complete only when:

- implementation matches the approved spec;
- acceptance criteria are tested;
- authorization and negative paths are tested;
- docs/design match the implementation;
- traceability is updated;
- relevant changelog/change records are updated;
- `make check` passes, or any environment-only blocker is explicitly reported;
- when the task started from an archive, the complete updated archive is
  produced for delivery.
