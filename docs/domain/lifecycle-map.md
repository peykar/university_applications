# Domain lifecycle map

This file records lifecycle vocabulary that is already present in the baselined specifications and implementation. It does not invent transition permissions that the specs do not define.

## Applicant / Lead

Implementation states: `NEW`, `ASSIGNED`, `FINALIZED`, `CLOSED`.

The finalization capability governs conversion to Student. `FIN-001`–`FIN-006` define authorization, validation, atomicity, audit effects and duplicate safety. A detailed transition matrix should only be added when transition permissions are explicitly specified.

## TODO

Specification states: `CREATED`, `IN_PROGRESS`, `DONE`, `CANCELLED` (`TODO-004`). DONE records who/when completed it. DONE and CANCELLED are explicitly reopenable. Other transition restrictions must not be inferred without a requirement change.

## Formal Application

Implementation states: `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `ADDITIONAL_DOCUMENTS`, `ACCEPTED`, `REJECTED`, `WITHDRAWN`, `CANCELLED`.

The current `APP-*` baseline defines creation, uniqueness, scoping and navigation, but does not yet define an authoritative status-transition matrix. That matrix remains future specification work rather than an assumed rule.

## Applicant document review

Implementation states: `PENDING`, `APPROVED`, `REPLACEMENT_REQUESTED`. Review/conversion behavior is governed by `DOC-*` and `FIN-*` requirements.
