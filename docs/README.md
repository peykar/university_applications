# TurkDemy Documentation

## Spec-driven development

TurkDemy now uses repository-backed spec-driven development.

Start here:

- [`SDD.md`](SDD.md) — development workflow.
- [`changes/README.md`](changes/README.md) — bug/change/feature triage and records.
- [`specs/README.md`](specs/README.md) — capability specifications and requirement IDs.
- [`product/terminology.md`](product/terminology.md) — canonical domain vocabulary.
- [`product/business-rules.md`](product/business-rules.md) — cross-capability invariants.
- [`architecture/overview.md`](architecture/overview.md) — architecture baseline.
- [`architecture/domain-model.md`](architecture/domain-model.md) — domain relationships.
- [`architecture/permissions.md`](architecture/permissions.md) — authorization model.
- [`architecture/decisions/`](architecture/decisions/) — accepted ADRs.
- [`spec-code-gap-report.md`](spec-code-gap-report.md) — baseline gaps/debt.

The root [`AGENTS.md`](../AGENTS.md) is the mandatory implementation and delivery
contract for ChatGPT/coding agents. It defines source-of-truth precedence,
one-request implementation semantics, verification, documentation duties, and
full-archive delivery. Approved capability specs take precedence over older flat
documentation when they conflict.


- `architecture.md`
- `project-structure.md`
- `models.md`
- `development.md`
- `business-rules.md`
- `authentication.md`
- `country-data.md`
- `faq-and-contact.md`
- `model-field-guidelines.md`
- `changelog.md`
- `linting-and-quality.md`
- `rasa-data.md`
- `rasa-import.md`
- `rasa-mapping.md`
- `admin.md`
- `configuration.md`
- `auditing.md`
- `deployment.md`
- `i18n.md`
- `public-and-api.md`
- `site-url-and-email.md`
- `dependency-audit.md`
- `public-frontend.md`
- `branding.md`
- `homepage.md`
- `program-filters.md`
- `program-detail.md`
- `leads.md`
- `lead-user-journey.md`

- [Agent workspace](agent-workspace.md) — agent operations, permissions, messages, program requests, and formal applications.

- [Navigation and workspace architecture](navigation.md)

- [Entity-level navigation](entity-navigation.md)


See also: [Agent workspace context](agent-workspace-context.md).


See also: [Agent applicant workspace](agent-applicant-workspace.md).

- `specs/todo-management/` — Agent-wide generic TODO work management.
- `specs/communication-log/` — CRM-style external communication history.

- `operations-workspace.md` — TODO and Communication Log workspace behavior/setup.

## Catalogue import

- `university-program-json-import.md` — normalized per-University JSON format and import command.

- `university-data-dump.md` — export one University catalogue as JSON for offline comparison and Rasa text enrichment.

- `catalogue-v3-cutover.md` — safe pre-migration backfill when upgrading an existing database from the removed Catalogue v2 storage.
