# ADR-004: Program interest is exploratory; Application is formal

Status: Accepted

## Context

Applicants and agents discuss programs before a formal university application
exists.

## Decision

`LeadProgramInterest` represents discussion, user interest, or Agent
recommendation. It may optionally identify a ProgramOffering but never itself
means an Application exists.

A formal `Application` requires a Student and concrete ProgramOffering. During
Lead finalization, the responsible Agent explicitly selects one or more discussed
interests; those selections are converted into DRAFT Applications as part of the
same atomic finalization operation. Program-level interests require an explicit
active ProgramOffering selection.

## Consequences

- Merely adding or recommending a Program does not create an Application.
- Finalization is the explicit Agent decision point for selecting which discussed
  programs become draft Applications.
- A converted interest links to its created Application.
- Unselected discussed interests remain historical/exploratory and may be converted
  later through the Student workflow.
