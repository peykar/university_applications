# CHG-0012 — Reopen finalized Request for a new program

Status: VERIFYING
Classification: CHANGE

## Request

A customer may choose a previously completed Request in the public Apply flow. Adding a genuinely new Program should reopen that Request for additional admissions work instead of creating a duplicate person or pretending the original conversion never occurred.

## Decisions

- Add explicit `reopened` Lead status.
- Reopening preserves the existing Student, original conversion provenance, documents, and Applications.
- Reopening happens only when a genuinely new Program identity is added; an already-present Program is a no-op.
- Closed Requests are not customer-reopened by this flow.
- Reopened Requests expose program management/recommendation workflows, but historical Lead profile/document mutation stays locked after Student creation.
- Responsible Agent completion reuses the Student and creates only missing selected DRAFT Applications, then returns the Request to finalized.

## Requirements

- `APL-008`
- `CRQ-091`–`CRQ-093`
- `FIN-018`–`FIN-019`

## Implementation

- `LeadStatus.REOPENED` and preservation in `Lead.save()`.
- Transactional `add_customer_program_interest()` lifecycle service.
- Apply flow delegates program addition/reopening to the service.
- Converted/reopened branch in `finalize_lead()`.
- Program-only Agent completion presentation for reopened Requests.
- Converted-Student guards keep Lead person/documents read-only.

## Verification

Runtime lifecycle tests cover reopen, duplicate no-op, Student/Application preservation, and re-finalization. Structural tests cover Apply and Agent/customer presentation. Final repository verification is recorded at delivery time.
