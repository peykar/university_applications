# CHG-0004 — Create Student Record full-page conversion

Status: IMPLEMENTED
Date: 2026-08-28

## Decision

Replace the Agent finalization modal with a dedicated **Create Student Record** page.
The Agent reviews editable Student data prefilled from the Lead, explicitly chooses
which Lead documents transfer, and may select zero or more discussed programs for
DRAFT Application creation. Every checked program requires an active offering.

Verified Lead documents are checked by default. Unverified documents are unchecked
by default, but if the Agent checks one it is approved inside the successful
conversion transaction and then copied to the Student document library. Unchecking
a verified document only excludes it from transfer and does not revoke verification.

The existing LeadDocument → StudentDocument conversion relation remains. The
LeadProgramInterest → Application persistent relation is removed because it adds
unnecessary lifecycle coupling.

## Affected requirements

`FIN-002`, `FIN-004`, `FIN-007`–`FIN-017`, `APP-002`, `APP-003`, `APP-006`.

## Atomicity

Student creation, selected document approval/transfer, selected DRAFT Application
creation, Lead finalization, audit and communication share the finalization service
transaction. Validation errors return to the page with the submitted values/selections
and no partial database conversion state committed.
