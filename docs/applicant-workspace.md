# Applicant workspace

The customer applicant detail page uses the shared TurkDemy shell and a scoped
`customer-applicant-page` design layer.

## Layout

- Applicant identity, workflow status, and primary actions are presented in the
  hero.
- Program interests and recommendations remain the first workflow panel.
- Documents use a compact list plus an expandable, fully styled upload form.
- The conversation is presented as a dedicated chat surface with responsive
  message bubbles, attachments, and composer controls.
- Profile and study-preference summaries live in the contextual sidebar.

## Responsive behavior

At tablet widths the sidebar becomes a two-card row above the main workflow.
At mobile widths all content stacks to one column, action buttons expand to
usable touch targets, upload controls fit the viewport, and chat bubbles use
most of the available width.

The page-specific styles are scoped under `.customer-applicant-page` so the
Agent Workspace and other lead views keep their own presentation.


## Agent recommendation reasons

When an Agent recommendation contains a customer-understandable reason, the
customer sees it on the Request Overview program card, on the Programs tab, and
with the PROGRAM_SUGGESTED item in Progress. The reason is recommendation data,
not an internal Agent note.
