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
