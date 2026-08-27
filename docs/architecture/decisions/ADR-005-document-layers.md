# ADR-005: Separate Lead, Student master, and Application document concerns

Status: Accepted

## Context

Documents evolve from provisional Applicant uploads to reusable Student records
and application-specific attachments.

## Decision

Keep LeadDocument review/version history, reusable StudentDocument, and
ApplicationDocument as distinct concerns. Attaching a document to an Application
does not define a university requirement.

## Consequences

- Approved Lead documents can be copied during finalization.
- Student documents can be reused across applications.
- Requirements need their own explicit workflow/model if introduced.
