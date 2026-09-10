# UI-0012 — Canonical applicant messaging UI

Status: DONE
Date: 2026-09-10

## Request

The Agent Applicant overview and dedicated Messages route presented the same Applicant conversation
with two independently maintained messaging UIs. The two surfaces differed in sender labels, system
message presentation, attachment controls, composer layout, and styling.

## Classification

UI / implementation consolidation. No messaging domain behavior, permissions, Conversation scope,
or send semantics change.

## Affected requirements

- `MSG-007` — Applicant Messages remain scoped to the Applicant.
- `MSG-008` — Existing active-Agent authorization remains unchanged.
- `MSG-010` — Both surfaces continue rendering locale-aware `localized_body` for system events.

## Decision

Use one canonical reusable Agent Applicant conversation partial wherever an Applicant conversation
is rendered. Both the Applicant overview and dedicated Messages route include this shared partial.
The shared component preserves attachment download and customer-attachment promotion to Documents.

## Implementation

- Added `templates/agents/includes/applicant_conversation.html` as the canonical Applicant messaging
  presentation.
- Replaced the duplicate message markup in `applicant_detail.html` and `applicant_section.html` with
  the shared include.
- Preserved the existing message-post endpoint and dedicated Messages redirect behavior.
- Promoted attachments link to the canonical Applicant Documents surface; unpromoted customer
  attachments retain the Add to Documents workflow.

## Verification

- Added `ApplicantMessagingCanonicalUITests` to verify both Agent Applicant surfaces include and
  render the same canonical component, sender identity, message content, and composer.
- Run `make format` and `make check` as final project verification.
