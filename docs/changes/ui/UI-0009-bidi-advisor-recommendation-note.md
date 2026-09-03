# UI-0009 — Bidi-aware advisor recommendation note

Status: IMPLEMENTED
Requested: 2026-09-03

## Request

Make Agent recommendation reasons read as a deliberate advisor note instead of loose text, especially when the note language direction differs from the surrounding page.

## Classification check

UI only. This change does not alter recommendation data, permissions, entity scope, lifecycle behavior, activity semantics, or information architecture.

## Affected surfaces

- Customer Request Overview program summary.
- Customer Request Programs workspace.
- Customer Request Progress recommendation event.
- Agent Applicant Programs workspace.
- Agent Applicant Activity recommendation event.

## Implementation

- Recommendation explanations use a shared subtle note treatment: neutral background, logical inline-start accent border, compact padding, and readable body text.
- Existing `dir="auto"` / `unicode-bidi: plaintext` behavior is preserved, and the Agent Programs surface now also declares `dir="auto"`.
- Logical border and `text-align: start` make Persian/Arabic notes anchor on the right while English and other LTR notes anchor on the left.
- No recommendation text is copied or transformed; the UI renders the same structured `suggestion_reason`.

## Acceptance

- [x] Visual change implemented consistently on recommendation-reason surfaces.
- [x] Mixed LTR/RTL note direction follows note content rather than page direction.
- [x] Existing recommendation behavior remains unchanged.
- [x] Structural regression coverage verifies the shared treatment and bidi attributes.
