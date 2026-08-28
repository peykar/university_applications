# Communication Log — Specification

Status: BASELINED

## Requirements

COM-001 — A Communication Log entry MUST belong to exactly one Agent
organization and MAY exist without a subject.

COM-002 — All users of the owning Agent organization MUST be able to see its
Communication Log entries.

COM-003 — V1 channels MUST be PHONE, EMAIL, WHATSAPP, TELEGRAM, IN_PERSON,
VIDEO_CALL and OTHER.

COM-004 — Counterparty type MUST be CUSTOMER, UNIVERSITY or OTHER.
`counterparty_name` MUST be optional free text in V1.

COM-005 — An entry MUST record the Agent user who performed the communication,
`occurred_at` for when it happened, `created_at` for when it was recorded, and a
short explanation.

COM-006 — Communication Log MUST remain explicitly separate from in-system
Messages.

COM-007 — The creator MAY edit a Communication Log entry. Every edit MUST retain
revision history. Other Agent users MUST NOT edit that entry.

COM-008 — A Communication Log entry MAY have exactly one canonical generic
subject using ContentType + UUID object id and MUST remain extensible to future
subject types.

COM-009 — Parent entity views MUST aggregate Communication Log entries from
supported child subjects. Applicant views therefore include direct Applicant
communications and communications about that Applicant's Applications.

COM-010 — An Agent user MUST be able to create a TODO directly from a
Communication Log entry.

COM-011 — Communication Log creation/editing MUST feed the existing
Applicant/Application activity experience when its subject resolves to those
entities.

COM-012 — Agent workspace MUST provide a global Communications page. Applicant
and Application Agent contextual navigation MUST provide a Communication Log
tab.

COM-013 — Applicant/Application communication experience SHOULD be capable of a
future unified timeline combining Messages and Communication Log without
merging their persistence models.
