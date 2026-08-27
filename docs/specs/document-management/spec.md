# Document management

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for document management.

## Requirements

DOC-001 — Customers MAY upload Applicant documents before finalization.

DOC-002 — Lead documents MUST have review state pending, approved, or replacement
requested.

DOC-003 — Agent review decisions MUST preserve reviewer/time/note and review
history.

DOC-004 — A customer replacement MUST preserve the prior document version and
review history instead of destructively replacing audit evidence.

DOC-005 — Agent users MAY promote a customer conversation attachment into the
Applicant document workflow.

DOC-006 — Approved/verified Lead documents MUST be eligible for copy to reusable
Student documents during finalization.

DOC-007 — Student documents MUST be reusable across Applications.

DOC-008 — ApplicationDocument MUST only reference a StudentDocument belonging to
the same Student as the Application.

DOC-009 — Attaching an ApplicationDocument MUST NOT imply that the document type
is a university requirement.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
