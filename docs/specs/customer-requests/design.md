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

Profile content is one compact primary panel divided into semantic groups: **Personal information** for email, phone, birthdate and gender; **Location & nationality** for nationality and residence; **Passport** for passport number; and **Education** for educational background. Section boundaries provide scanability without turning each group into another dashboard card.

The single customer **Edit profile** action is placed beside the first Profile content heading and keeps the existing editability rule: finalized Requests do not expose customer editing. The shared Request header no longer changes its customer actions merely because Profile is selected. Agent-facing Edit applicant remains in the shared Agent header.

Program preferences and uploaded-document summaries remain exclusively in the persistent Request context sidebar. They are intentionally not copied into Profile because Profile describes the person while the context rail describes Request-level study and document context.
