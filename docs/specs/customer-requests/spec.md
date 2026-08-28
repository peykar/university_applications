# Customer requests

Status: APPROVED
Version: 1.2

## Goal

Present the customer journey as a simple end-to-end **Request** without exposing
Agent/internal lifecycle terminology such as Lead, Student, or Application as
customer navigation concepts.

## Requirements

CRQ-001 — Customer-facing workspace navigation and request pages MUST use
**Request** terminology for the customer's case; Lead, Student, and Application
remain internal/Agent domain terminology.

CRQ-002 — The customer desktop sidebar MUST contain menu items only: **My
Requests**, **Messages**, **Get Help**, and, when configured, **Message us on
WhatsApp**. It MUST NOT render sidebar heading/subtitle copy such as “MY
TURKDEMY” or “Student workspace”.

CRQ-003 — **Get Help** MUST link to the existing Contact page. The WhatsApp item
MUST derive its number from the `WHATSAPP_NUMBER` environment-backed Django
setting, MUST NOT hard-code a number in templates, and MUST be hidden when no
number is configured.

CRQ-004 — **My Requests** MUST be the authenticated customer workspace landing
page and MUST expose a **Find Programs** page action linking to the public
Programs catalogue.

CRQ-005 — Each request card MUST show the request person's full name, email and
cell when available.

CRQ-006 — Each request card MUST show an **Applied for** section containing all
program interests associated with the request regardless of whether they were
added by the customer or suggested by an Agent. Agent-originated interests MUST
carry a small “Suggested by your agent” tip.

CRQ-007 — A request card MUST visibly indicate that action is required when the
request has unread incoming customer-visible messages or a document with
replacement requested.

CRQ-008 — The whole request card/row MUST be a single primary click target that
opens that request.

CRQ-009 — Desktop page actions MUST use the shared TurkDemy convention: top
right of the main section in LTR and top left in RTL. Mobile placement MAY adapt
to the most usable responsive layout.

CRQ-010 — The customer Request abstraction MUST NOT change the canonical
Lead→Student→Application backend lifecycle or Agent-facing terminology.

CRQ-011 — Each program entry in **Applied for** MUST render a non-empty program
name and university name from the canonical Program/University display fields;
missing/nonexistent template attributes MUST NOT produce placeholder separator-only
boxes.

CRQ-012 — Request cards MUST remain visually stable on pointer hover. Hover MUST
NOT add underline, movement, border changes, or shadow changes; clickability is
communicated by the card being a link/click target itself.

CRQ-013 — Customer Request detail pages MUST use a three-part desktop hierarchy:
the global Customer sidebar, a central Request workspace, and a right-side Request
context sidebar. The context sidebar MAY stack below the main content on narrower
layouts.

CRQ-014 — Request navigation MUST remain inside the central Request workspace,
after the Request header and before page-specific content, with **Overview**,
**Profile**, **Programs**, **Documents**, and **Messages** as customer tabs.

CRQ-015 — The Request context sidebar MUST persist across Request detail tabs and
MUST include a compact **Uploaded documents** summary with review state and access
to document management/upload.

CRQ-016 — The Request context sidebar MUST include **Program preferences**, using
the existing LeadPreference data (degree, field, language, tuition and other
configured preferences) and MUST link to the existing preference-edit workflow
when the Request remains editable.

CRQ-017 — Request Overview MUST prioritize customer-relevant information in the
main section: action-required items, applied-for programs, customer-safe progress,
and recent messages. Agent-originated program interests MUST remain visibly marked.

CRQ-018 — Opening Request Overview MUST NOT mark incoming messages as read. The
Request-specific Messages page is the read boundary for that conversation.

CRQ-019 — Customer Request status labels MUST be customer-friendly presentation
labels and MUST NOT change the underlying Lead status values or Agent-facing
status labels.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by named tests or repository checks in traceability.
