# Customer requests — technical design

Status: APPROVED

## Domain boundary

`Lead` remains the current root used to locate a customer's request. Its related
`LeadProgramInterest`, `LeadDocument`, generic `Conversation`, converted
`Student`, and formal `Application` records remain unchanged. “Request” is a
customer-facing presentation abstraction, not a new database model.

## Navigation

`templates/customer/base.html` owns the customer sidebar. It contains only menu
links. `apps.core.context_processors.customer_support_links` converts the
optional environment-backed `WHATSAPP_NUMBER` setting into a safe `wa.me` URL.
The contact link reuses the existing `contact` route.

The customer login redirect and legacy dashboard route resolve to `lead-list`,
which is presented as **My Requests**.

## My Requests query/view

`apps.leads.views.lead_list` prefetches program interests (including university)
and documents. Existing subject conversations are loaded for the customer's
Leads, and the generic messaging unread service determines per-request incoming
unread counts. No conversation is created merely by listing Requests.

A request needs attention when either:

- the request conversation has at least one unread Agent/System message; or
- a Lead document has `replacement_requested` review status.

## Presentation

`templates/leads/lead_list.html` renders each request as one anchor/card. It
shows identity/contact information, all program interests, an Agent suggestion
tip when `LeadProgramInterest.source == agent`, and compact attention reasons.
The primary page action is **Find Programs**.

CSS in `static/css/turkdemy.css` provides desktop row/card presentation,
responsive mobile stacking, and logical/RTL-safe alignment.

## Compatibility

Django route names and backend model/service names remain internal and stable.
Agent pages continue to use Applicant/Student/Application terminology.

## Request-card display details

Applied-for entries render the canonical `Program.name_en` and
`University.name_en` fields used by the existing catalogue templates. This avoids
Django silently rendering nonexistent `.name` attributes as empty strings.

The entire request card remains an anchor, but its hover state intentionally has
no visual transformation. The card overrides the site's global `a:hover` underline
so nested card content does not become visually noisy when the pointer enters it.

## Request detail workspace

Customer Request detail pages use a nested workspace hierarchy. The global
`templates/customer/base.html` sidebar remains the account-level navigation.
Inside the main account column, `request-detail-layout` is the top-level Request
workspace grid. Its central `request-detail-main` contains the Request header,
Request-local tabs, and page-specific content. Its sibling
`customer_request_context_sidebar.html` is the persistent right-hand aside. This
keeps the right context rail parallel to the whole Request workspace instead of
starting only after the header and tabs.

The Request context sidebar deliberately contains operational context rather than
more navigation: a compact uploaded-document list/status summary and the existing
`LeadPreference` study preferences. On smaller screens the aside stacks below the
main content rather than competing for horizontal space.

Request Overview is a dashboard, not a duplication of every tab. Its central
content follows one vertical information flow: attention items (when present), all
applied-for/program-interest records, the customer-safe activity timeline, then
recent conversation messages. Progress and Recent messages are not split into a
secondary two-column grid. Detailed editing and management continue through the
Profile, Programs, Documents and Messages tabs.

Unread state is calculated before optional read marking. Overview does not mark
the conversation read; `lead_messages` remains the explicit Request-level read
boundary. Customer activity labels are presentation mappings so internal Lead
activity descriptions do not leak Applicant/finalization terminology.

Customer status presentation maps Lead states to Received / In progress /
Completed / Closed while Agent pages continue using the canonical Lead labels.
The customer Request header deliberately contains status only: advisory/internal
workflow hints such as program-recommendation next steps are not rendered there.
Customer-required work is surfaced by Action required, informational attention by
Needs your attention, and TurkDemy/Agent work by the customer-safe progress timeline.

## Overview density and action semantics

Overview cards are content-sized and intentionally compact. The main flow keeps
clear card boundaries, but padding, heading spacing, timeline spacing and message
rows are reduced so short datasets do not create a long mostly-empty page.

The attention panel does not use a vague summary such as “You have something to
review”. Each attention row is self-describing: unread-message attention includes
the actual unread count, while document attention names the document type that
needs replacement and links to the relevant Request tab.

The right-side document summary uses one customer-facing review vocabulary:
**Approved**, **Under review**, and **Needs replacement**. These are presentation
labels over the existing document review states and do not change model values.


## Label and action economy

Customer Request presentation follows **one concept, one label, one primary action**. The customer header uses a single back link (`← My Requests`) plus the Request person's name once and the customer-facing status; the customer does not receive a duplicated name breadcrumb or decorative Request eyebrow. Agent breadcrumbs remain operationally unchanged.

Overview summary cards use single semantic headings: **Applied programs**, **Progress**, and **Recent messages**. Applied program rows themselves open program details, so the Overview does not duplicate that affordance with a View programs link. Recent messages uses the concise **View all** action to open the Request Messages tab.

The context rail likewise uses only **Uploaded documents** and **Program preferences** as card headings. Document View all and Upload document are both retained because they are distinct operations. Program preferences has one header-level Edit action and no repeated footer edit action.

## Profile information architecture

The customer Profile tab treats the active **Profile** navigation state as sufficient page identity. It therefore does not add a second Profile eyebrow or a generic Request profile title. The Request person's name remains owned by the shared Request header and is not repeated in the tab body.

Profile content is one compact primary panel divided into semantic groups: **Personal information**, **Identity & nationality**, **Residence**, **Passport**, and **Education & language**. Section boundaries provide scanability without turning each group into another dashboard card.

The single customer **Edit profile** action is placed beside the first Profile content heading and keeps the existing editability rule: finalized Requests do not expose customer editing. The shared Request header no longer changes its customer actions merely because Profile is selected. Agent-facing Edit applicant remains in the shared Agent header.

Program preferences and uploaded-document summaries remain exclusively in the persistent Request context sidebar. They are intentionally not copied into Profile because Profile describes the person while the context rail describes Request-level study and document context.

## Profile view/edit alignment

The customer Profile is the read-only representation of the customer-editable Request-person data. The shared Request title owns the person's name, so first/middle/last name are not repeated in the Profile body; every other field in the customer edit form has a visible read-only counterpart. Empty data remains visible as an em dash so customers can distinguish "not provided" from "field does not exist."

The read-only layout is grouped as **Personal information**, **Identity & nationality**, **Residence**, **Passport**, and **Education & language**. This exposes country of birth, full residence/address data, passport authority/issue/expiry dates, English test details, GPA/scale, and educational background rather than presenting only a partial profile.

Editing an existing Request uses a dedicated customer edit form derived from the intake form but excludes internal workflow controls such as `needs_program_recommendation`. The customer edit screen uses **Edit profile** / **Save changes**, omits Request-profile/finalization explanatory copy, and cancels back to the Request Profile tab. Initial intake is kept separate so its existing "need help choosing" behavior can continue without leaking the internal control into later profile maintenance.
## Programs tab information architecture

The active **Programs** Request navigation tab provides page identity, so the tab body uses one **Programs** heading without a decorative eyebrow. A single header-level **Find programs** action links to the catalogue and is the page's add/browse action. The empty state therefore contains guidance only and does not repeat that action.

Each associated `LeadProgramInterest` provides a large primary content link to the canonical public program detail route while keeping management controls as separate interactive elements. The visual hierarchy is program name first, university second, compact comparison metadata third, then provenance as secondary context. No separate View details label is needed.

Provenance remains customer-visible: Agent-originated rows use **Suggested by your advisor** and customer-originated rows use **Added by you**. When an Agent supplied `suggestion_reason`, that explanation is shown beneath the provenance label; the generic `notes` field remains internal. Intake is always represented by one dropdown on editable Requests, with the current offering selected or **Select intake** as the no-selection placeholder.

Program preferences remain Request context rather than Programs-tab body content. The existing persistent right sidebar continues to own preference summary/edit behavior, preventing the Programs tab from becoming a duplicate preference editor.



## Program summary versus workspace

Request Overview treats Programs as a compact summary, not as formal applications. Each row carries enough comparison context to be useful at a glance: degree, language, and offering-backed tuition. The dedicated Programs tab is the management workspace and adds duration, intake selection, removal, and fuller pricing context. Long-form programme content remains owned by the public Program Detail page.

Tuition is never synthesized from the Program itself because pricing belongs to ProgramOffering. A selected offering is authoritative; without one, the first active offering may provide a clearly labelled From price. Customer intake updates validate that the offering is active and belongs to the interest's program. Program removal and intake mutation are ownership-scoped and disabled/rejected after Request finalization. Advisor/customer provenance remains informational; there is deliberately no accept/reject state.

Because the richer card contains POST controls, valid HTML requires the program-detail anchor to wrap only the informational content rather than the entire card.


## Program intake and recommendation interaction

The customer Programs workspace keeps intake selection intentionally lightweight. Every editable program card owns one offering-backed `<select>` inside its intake form. The current `program_offering` is selected when present; otherwise the first state is **Select intake**. A change event submits that form immediately, and the existing POST endpoint validates ownership, Request mutability, active status, and same-program membership before redirecting back to the Programs tab. No adjacent Select/Save/Change button is rendered.

Removal is deliberately outside the intake form because it mutates the program interest rather than its offering. It is represented by a compact trash icon at card level, with accessible text and browser confirmation before POST.

For Agent-originated interests, `LeadProgramInterest.suggestion_reason` is the customer-facing recommendation explanation and is shown only when populated. The separate generic `notes` field remains internal and is not rendered to customers. Finalized Requests keep the same information presentation but suppress editable intake/removal controls.

## Programs card width and destructive-action styling

The dedicated Programs workspace is a single comparison column. Its program list is
therefore explicitly rendered as a one-column grid and each card fills the available
column width. Content length must not determine card width.

Program removal remains a separate card-level control, but the trash icon is visually
neutral rather than styled as a boxed/destructive button. It uses a gray borderless
icon at rest, a darker gray hover state, and a focus-visible outline for keyboard users.

## Advisor recommendation-note presentation

Agent recommendation provenance and explanation are deliberately distinct. The compact **Suggested by your advisor** label identifies origin; when `suggestion_reason` is present, it renders below that label as ordinary readable note text rather than inline badge copy. The note uses `dir="auto"` plus bidi-safe styling so its direction follows its actual content without changing the surrounding page direction. Generic `notes` remains internal.
## Unassigned Request messaging

A Lead may legitimately exist without an Agent when `DEFAULT_LEAD_AGENT_ID` is empty, invalid, inactive, or when an older record predates assignment. Customer Request rendering therefore does not call `ensure_conversation()` for an Agent-less Lead. The Request context uses an empty `Message` queryset, zero unread count, and no recent messages until an Agent organization exists. The Request Messages tab renders an assignment-pending explanation instead of a compose form. A direct message POST is also guarded and redirects safely with customer-facing feedback. Once an Agent is assigned, the existing generic conversation service creates/loads the canonical Agent + customer + subject conversation normally.


## Programs card action placement

Program navigation and removal are deliberately separated by role and location. Program Detail remains part of the main detail link and uses a lightweight borderless SVG arrow at the card's logical top/end edge. Remove remains a separate confirmed POST form, but it is placed in a bottom/end footer action row beneath intake management. The removal affordance is borderless and neutral gray, combining the trash icon with a visible **Remove** label while retaining accessible labeling and keyboard focus treatment. This avoids visually grouping navigation and destructive actions and uses logical alignment so LTR and RTL layouts remain correct.

## Customer Documents workspace

The Documents tab is the complete customer document-management workspace. It uses one **Documents** heading and presents each `LeadDocument` by semantic document type rather than storage filename. Review state is explicit customer copy: **Approved**, **Under review**, or **Needs replacement**. A lightweight borderless vector arrow opens the file without promoting the filename into the UI.

Cards stay compact unless action is required. A replacement-requested card expands to show `review_note` when available and the existing replacement upload disclosure/form. The normal upload flow remains the existing modal, but only one primary Upload document trigger is rendered: in the heading when documents exist, or inside the empty state when none exist.

The Request context sidebar is contextual. It is useful on Overview/Profile/Programs/Messages, but the Documents tab is a focused document-management workspace and renders no Request context sidebar at all. The Documents layout therefore expands into the available Request-detail width and does not repeat either Uploaded documents or Program preferences.


## Documents mobile refinement

On the Documents tab, document type is both the semantic identity and a direct file link; the stored filename remains implementation detail. The separate borderless arrow remains as a secondary open affordance. On small screens, the Documents heading and the single Upload document action share one row, with Upload using a lighter secondary treatment. Ordinary cards reduce vertical padding and center the open arrow against the card; replacement-required cards may keep the arrow near the top because their review note/replacement workflow makes the card intentionally taller.

The customer Request tab bar uses a five-column mobile layout for Overview, Profile, Programs, Documents, and Messages. This avoids the final tab being visually clipped while keeping all Request-local navigation available without a hidden horizontal-scroll dependency.
