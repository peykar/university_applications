# Customer requests

Status: APPROVED
Version: 1.11

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
context sidebar. The right context sidebar MUST be a peer of the entire central
Request workspace and start at the same workspace level as the Request header; it
MUST NOT begin only below the Request header/navigation. The context sidebar MAY
stack below the main content on narrower layouts.

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
central main section in this order: action-required items when present, applied-for
programs, customer-safe progress, and recent messages. These major Overview sections
MUST remain one central vertical flow rather than splitting Progress and Recent
messages into a nested two-column dashboard. Agent-originated program interests MUST
remain visibly marked.

CRQ-018 — Opening Request Overview MUST NOT mark incoming messages as read. The
Request-specific Messages page is the read boundary for that conversation.

CRQ-019 — Customer Request status labels MUST be customer-friendly presentation
labels and MUST NOT change the underlying Lead status values or Agent-facing
status labels.

CRQ-020 — Request Overview MUST use compact, content-sized cards rather than
excessive empty vertical space. Action-required rows MUST state the concrete
customer action or condition (for example the unread-message count or the
document that needs replacement) instead of a generic “something to review”
heading. Customer document review labels in the context sidebar MUST use the
canonical presentation vocabulary **Approved**, **Under review**, and **Needs
replacement**.

CRQ-021 — Customer Request header MUST show only the canonical customer-facing
Request status and MUST NOT expose internal/advisory workflow guidance such as
**Next step — Program recommendations**. Customer-required work belongs in
**Action required**, informational items belong in **Needs your attention**, and
TurkDemy/Agent work belongs in customer-safe **Request progress**. Agent-facing
recommendation guidance remains unchanged.

CRQ-022 — Unread messages alone MUST be presented as **Needs your attention**,
not **Action required**. **Action required** is reserved for a concrete customer
action represented by the Request workspace, such as replacing a rejected
document.

CRQ-023 — Customer progress entries MUST add useful subject context when the
recorded customer-visible activity contains it, such as the uploaded document
name or program name, instead of showing only generic event types.

CRQ-024 — Recent-message previews MUST NOT expose an Agent's login/email as the
customer-facing sender identity. They MUST prefer the Agent user's full display
name and otherwise use **Your advisor**; system messages remain **TurkDemy**.

CRQ-025 — Customer Request pages MUST follow the presentation principle **one concept, one label, one primary action**. Repetition MUST add distinct information or functionality and MUST NOT exist only to create visual hierarchy.

CRQ-026 — The customer Request identity MUST show the Request person's name exactly once. Customer detail pages MUST use **← My Requests** as the back-navigation affordance, MUST NOT repeat the name in a breadcrumb, and MUST NOT show a decorative **Request** eyebrow above the title. Agent-facing breadcrumbs and Applicant labeling remain unchanged.

CRQ-027 — Request Overview MUST use **Programs** as the single program-summary heading because Request-stage program interests are not necessarily formal university applications. It MUST NOT additionally show **Applied for**, **Applied programs**, or a redundant **View programs** action. Each visible program row remains the direct link to that program's detail page, and the Request-level Programs tab remains available for the complete program workflow.

CRQ-028 — Request Overview MUST use **Progress** as the single timeline heading and MUST NOT pair a decorative **Progress** eyebrow with **Request progress**.

CRQ-029 — Request Overview MUST use **Recent messages** as the single message-summary heading. Its link to the complete Request Messages tab MUST be labeled **View all** rather than repeating the word Messages.

CRQ-030 — The Request context document card MUST use **Uploaded documents** as its single heading and MUST NOT show a decorative **Files** eyebrow. **View all** and **Upload document** MAY coexist because they perform distinct actions.

CRQ-031 — The Request context preference card MUST use **Program preferences** as its single heading, MUST NOT show a decorative **Study** eyebrow, and MUST expose at most one edit action. When editable, that action MUST be the header-level **Edit** action; the duplicate bottom **Edit preferences** action MUST NOT render.

CRQ-032 — The customer Request **Profile** tab MUST rely on the active Request navigation tab for page identity and MUST NOT repeat that identity with decorative **Profile** or **Request profile** headings inside the tab content. The content MUST begin with meaningful person-information sections.

CRQ-033 — Customer Profile information MUST be grouped by meaning: **Personal information**, **Identity & nationality**, **Residence**, **Passport**, and **Education & language**. The Request person's name MUST remain in the shared Request header and MUST NOT be repeated inside Profile content.

CRQ-034 — Customer Profile MUST expose at most one **Edit profile** action. When the Request is editable, that action MUST live with the Profile content rather than appearing in the shared Request header. Finalized Requests MUST NOT expose the customer edit action. Agent-facing **Edit applicant** behavior remains unchanged.

CRQ-035 — The customer Profile tab MUST remain person-focused and MUST NOT duplicate **Program preferences** or uploaded-document context already owned by the persistent Request context sidebar. The context sidebar MUST continue to render beside Profile using the same Request detail layout.

CRQ-036 — Profile groups MUST use a compact, scan-friendly presentation inside one primary Profile panel, with clear section boundaries and responsive fact grids rather than separate decorative cards or repeated page-level headings.

CRQ-037 — Customer Profile read-only content MUST represent every field that the customer can edit in the existing Request profile editor, except the person's first/middle/last name MAY be represented once by the shared Request title instead of repeated in the Profile body. The read-only groups MUST include country of birth, residence address, passport issuing authority and dates, English test details, high-school GPA details, and educational background in addition to the previously shown fields.

CRQ-038 — Customer Profile display and customer Profile editing MUST remain field-aligned: adding a new customer-editable profile field requires adding a corresponding customer-visible read-only representation, unless an explicit customer-requests SDD requirement documents why that field is intentionally hidden. Missing values MUST render a stable placeholder rather than disappearing from the Profile layout.

CRQ-039 — The existing customer **Edit profile** page MUST use customer-facing Request/Profile terminology and MUST NOT expose internal Applicant/finalization workflow wording. Editing an existing Request MUST use **Edit profile**, **Save changes**, and return/cancel to the Request Profile tab.

CRQ-040 — Internal workflow controls such as **needs program recommendation** MUST NOT render in the existing customer Profile editor. Customer program-preference/help flows remain separate; Agent-side recommendation controls and the initial Request-intake behavior MAY continue to use the underlying domain flag where required.

CRQ-041 — Customer Profile editing MUST preserve the same semantic grouping as the read-only Profile wherever practical: Personal information, identity/nationality and residence, Passport, and Education & language. The read-only Profile MAY split identity/nationality and residence into separate scan-friendly sections without changing field ownership.

CRQ-042 — The customer Request **Programs** tab MUST use **Programs** as its single section heading and MUST NOT repeat the tab identity with a decorative Programs eyebrow. The tab MAY expose one **Find programs** action because adding another program is the primary workflow on this page.

CRQ-043 — Every program shown on the customer Programs tab MUST be a single whole-card link to that program's public detail page. Program name MUST be the strongest card label, followed by university, then compact degree/intake metadata; the card MUST NOT require a separate View details link.

CRQ-044 — Customer program cards MUST preserve provenance without letting provenance dominate the card hierarchy: Agent-originated interests MUST show **Suggested by your advisor** and customer-originated interests MUST show **Added by you** as secondary source labels.

CRQ-045 — Program intake presentation on the customer Programs tab MUST use concrete semester/year text when an offering is selected and MUST use the customer-facing phrase **Intake to be decided** when no offering is selected. The internal phrase **Any intake / decide later** MUST NOT render on this customer page.

CRQ-046 — The customer Programs tab MUST expose only one browse/add-program action. When the persistent header-level **Find programs** action is present, the empty state MUST provide explanatory copy without adding a second **Browse programs** button.

CRQ-047 — The customer Programs tab MUST remain focused on programs associated with the Request and MUST NOT duplicate the **Program preferences** summary/edit UI owned by the persistent Request context sidebar.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by named tests or repository checks in traceability.


CRQ-048 — Request Overview program rows MUST remain compact but MUST add the program's degree level, language, and tuition when tuition data is available, while preserving program name, university, provenance, and direct program-detail navigation.

CRQ-049 — Tuition displayed for a Request program MUST come from ProgramOffering data. When a specific offering is selected, its discounted tuition when available (otherwise standard tuition), currency, and fee basis MUST be shown. When no offering is selected, the UI MAY show a clearly labelled **From** price from an active offering and MUST NOT imply that this is a selected intake price.

CRQ-050 — The Programs tab MUST function as the detailed program-comparison workspace and MUST show degree, language, tuition, duration when known, intake, and provenance without duplicating long-form catalogue content already available on Program Detail.

CRQ-051 — While a Request is editable, the customer MUST be able to select or change the ProgramOffering/intake for an existing Request program. The selected offering MUST belong to that same program and be active; an empty selection MUST represent **Intake to be decided**.

CRQ-052 — While a Request is editable, the customer MUST be able to remove a program interest from the Request. Intake changes and removal MUST be scoped to a Request owned by the authenticated customer, and finalized Requests MUST reject these mutations.

CRQ-053 — The Programs workspace MUST NOT introduce accept/reject or add-to-request approval states for advisor suggestions. Once a program interest exists on the Request, provenance is informational and both customer-added and advisor-suggested interests use the same intake/removal management model.

CRQ-054 — Because program cards now contain management controls, the Programs workspace MUST use a clear program-detail link as the primary informational click target rather than nesting forms inside a whole-card anchor. The program name/content area and directional affordance MUST remain visibly navigable to Program Detail.
