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


## Agent Workspace UI

Document review and chat-attachment promotion use modal dialogs rather than
inline forms. This keeps the conversation and narrow Documents sidebar compact.

- Documents expose compact **Open** and **Review** actions.
- Review opens a dialog with document context, an Open-document action,
  Approve / Request replacement / Keep pending decisions, and an optional note.
- Chat attachments expose compact **Open** and **Add to documents** actions.
- Add to documents opens a dialog for document type, name and description.
- Promoted attachments show **Added to documents** and can open the related
  document review dialog.


## Replacement requests

A document that needs another copy uses **Replacement requested**, not
"Rejected".

When an agent requests replacement:

- the review decision and note are written to `LeadDocumentReviewHistory`;
- the applicant sees the replacement reason;
- a system message is added to the applicant conversation;
- the applicant gets **Replace document** on that exact document.

When the applicant uploads a replacement, TurkDemy archives the previous file
as a `LeadDocumentVersion`, replaces the current file on the same
`LeadDocument`, resets review state to **Needs review**, clears the current
review metadata, and sends a system message that the replacement is pending
review. This preserves both the logical document identity and internal history.
