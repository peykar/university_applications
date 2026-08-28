# UI-0002 — Improve Django admin list/search/filter and relation UX

Status: VERIFYING
Requested: 2026-08-28

## Request

Make Django admin model pages substantially easier to browse and operate:

- useful list columns;
- search for human/business identifiers;
- filters for state, ownership and dates;
- sensible ordering/date navigation;
- inline editing/viewing for related child models where the relation is suitable.

## Classification check

UI. No domain rules, permissions, lifecycle transitions, workspace scope or public information architecture are changed.

## Affected surfaces

- Django admin — TODOs and comments.
- Django admin — Communication Logs and immutable revisions.
- Django admin — Conversations, messages, attachments and participant read state.
- Django admin — Students and their Applications.

Existing admin areas that already provide good list/search/filter/inline behavior remain unchanged.

## Inline policy

Use inline admin when the child collection is naturally edited/read in the context of one parent and is expected to remain reasonably bounded.

V1 inline relationships include:

- TODO → comments (read-only because comments are immutable);
- Communication Log → revisions (read-only because revisions are immutable);
- Conversation → messages and participant states;
- Message → attachments;
- Student → documents and applications;
- existing Agent → documents;
- existing Lead → preference, program interests, documents and activity;
- existing Application → documents;
- existing Program → offerings;
- existing University → media;
- existing FAQ Category → FAQs.

High-cardinality catalogue/geography reverse relations are intentionally not rendered inline because loading thousands of child rows on one admin change form makes the admin slower and less usable. They remain searchable/filterable standalone models.

Generic TODO/Communication subjects are also not injected as generic inlines into every possible subject model in this UI-only change. Their generic ownership and creation rules belong to the operations service/workspace and should not be duplicated implicitly in admin formsets.

## Acceptance

- [x] TODO and Communication admin have useful list/search/filter/date navigation.
- [x] TODO comments and Communication revisions are visible inline and preserve immutability.
- [x] Messaging models have useful list/search/filter UI.
- [x] Messages expose attachments inline; Conversations expose messages/read state inline.
- [x] Student exposes Applications inline alongside documents.
- [x] Existing strong admin configurations are preserved.
- [x] No model/migration change required.
- [ ] `make format` passes.
- [ ] `make check` passes.
