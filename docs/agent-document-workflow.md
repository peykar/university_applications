# Agent document review workflow

Agent Workspace treats applicant documents as reviewable records.

## Review states

Each `LeadDocument` has:

- `pending` — needs review
- `approved`
- `rejected`

The review also records `reviewed_by`, `reviewed_at`, and an optional
`review_note`. `is_verified` remains for compatibility and is synchronized to
`True` only for approved documents.

On the applicant detail page an agent can open the document and expand
**Review** to approve it, reject/request replacement, or leave it pending.

## Chat attachment → document

Customer chat attachments expose **Add to documents**. The agent chooses a
document type and can optionally edit the name/description.

The file is copied into normal `LeadDocument` storage and the document stores a
one-to-one `source_message_attachment` reference. This prevents duplicate
promotion and preserves provenance. The chat attachment then shows
**Added to documents**.

Promoted documents start in `pending` and follow the same review workflow as
files uploaded through the applicant Documents section.
