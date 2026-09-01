# CHG-0010 — Locale-aware structured system messages

Status: IMPLEMENTED
Date: 2026-09-01
Requirements: `MSG-010`, `I18N-001`

## Problem

System-generated conversation messages were rendered into the request locale at creation time and
persisted only as `Message.body`. Their language was therefore frozen. A recommendation created
from an English Agent session continued to display in English when the same conversation was later
opened under Persian, Turkish, or Arabic.

## Decision

New system-generated workflow messages store a stable `event_type` plus JSON-safe structured
`event_data`. `Message.body` remains an English fallback snapshot for resilience and legacy
compatibility. Rendering resolves the structured event in the active request locale and resolves
localized referenced catalogue values at display time.

Human-authored customer/Agent messages remain unchanged. Existing historical system messages that
have no structured event metadata continue to display their stored body and are not machine
translated or rewritten.

## Implemented event families

- program recommendation;
- customer document replacement upload;
- Agent document replacement request;
- Applicant finalization.

## Database note

The repository intentionally does not commit generated Django migrations. Existing deployments must
run the project's normal local migration workflow after updating so the new `Message.event_type` and
`Message.event_data` columns are added.
