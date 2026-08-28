# TODO Management — Specification

Status: BASELINED

## Requirements

TODO-001 — A TODO MUST belong to exactly one Agent organization and MAY exist
without a subject.

TODO-002 — Every user of the owning Agent organization MUST be able to see its
TODOs. Any Agent user in that organization MAY assign or reassign a TODO.

TODO-003 — A TODO MUST have a title, MAY have a description, MAY have one
assignee, and MAY have a date-only due date.

TODO-004 — TODO lifecycle states MUST be CREATED, IN_PROGRESS, DONE and
CANCELLED. DONE MUST record who completed it and when. DONE and CANCELLED TODOs
MUST be reopenable.

TODO-005 — V1 MUST expose due/overdue state in the UI and MUST NOT require
reminders.

TODO-006 — TODO comments MUST contain author, body, created_at and updated_at.
Comments MUST be immutable after posting. V1 MUST NOT support attachments.

TODO-007 — A TODO MAY have exactly one canonical generic subject using
ContentType + UUID object id. The design MUST remain extensible to future subject
types such as a dormitory service.

TODO-008 — Parent entity views MUST aggregate TODOs from supported child
subjects. Applicant views therefore include TODOs directly about the Applicant
and TODOs about that Applicant's Applications.

TODO-009 — TODO creation/status/assignment/comment actions MUST be Agent-private
operational activity and MUST feed the existing Applicant/Application activity
experience when the generic subject can be resolved to those entities.

TODO-010 — Agent workspace MUST provide a global TODO page. Applicant and
Application Agent contextual navigation MUST provide a TODOs tab.
