# Domain lifecycle map

This file records lifecycle vocabulary that is already present in the baselined specifications and implementation. It does not invent transition permissions that the specs do not define.

## Applicant / Lead

Implementation states: `NEW`, `ASSIGNED`, `FINALIZED`, `CLOSED`.

The finalization capability governs conversion to Student and creation of the initial draft Applications. `FIN-001`–`FIN-017` define authorization, the full-page Create Student Record review, editable Student data, document selection, program selection, atomicity, audit effects and duplicate safety. Conversion may proceed with zero discussed programs. Any selected discussed program must have an active concrete offering and becomes a DRAFT Application. Selected Lead documents transfer to StudentDocument records; selected unverified documents are approved as part of successful conversion.

## TODO

Specification states: `CREATED`, `IN_PROGRESS`, `DONE`, `CANCELLED` (`TODO-004`). DONE records who/when completed it. DONE and CANCELLED are explicitly reopenable. Other transition restrictions must not be inferred without a requirement change.

## Formal Application

Implementation states: `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `ADDITIONAL_DOCUMENTS`, `ACCEPTED`, `REJECTED`, `WITHDRAWN`, `CANCELLED`.

The current `APP-*` baseline defines creation, uniqueness, scoping and navigation, but does not yet define an authoritative status-transition matrix. That matrix remains future specification work rather than an assumed rule.

## Applicant document review

Implementation states: `PENDING`, `APPROVED`, `REPLACEMENT_REQUESTED`. Review/conversion behavior is governed by `DOC-*` and `FIN-*` requirements.
