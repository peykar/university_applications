# ADR-004: Program interest is exploratory; Application is formal

Status: Accepted

## Context

Applicants and agents discuss programs before a formal university application
exists.

## Decision

`LeadProgramInterest` represents discussion, user interest, or Agent
recommendation. It may optionally identify a ProgramOffering but never itself
means an Application exists.

A formal `Application` requires a finalized Student and concrete
ProgramOffering.

## Consequences

- Recommendations do not automatically create Applications.
- An interest may later link to its converted Application.
- Application creation remains an explicit Agent workflow.
