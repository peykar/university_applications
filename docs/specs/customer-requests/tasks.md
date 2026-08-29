# Customer requests — tasks

Status: IMPLEMENTED

- [x] `CRQ-001` Establish Request as the customer-facing case abstraction.
- [x] `CRQ-002` Replace customer sidebar with menu-only Request navigation.
- [x] `CRQ-003` Add environment-backed optional WhatsApp support and Contact link.
- [x] `CRQ-004` Make My Requests the customer landing page and add Find Programs.
- [x] `CRQ-005` Show request full name, email, and cell.
- [x] `CRQ-006` Show all associated programs with Agent-suggestion tips.
- [x] `CRQ-007` Surface unread-message/document-replacement attention state.
- [x] `CRQ-008` Make the full request card clickable.
- [x] `CRQ-009` Apply desktop action/RTL/mobile placement convention.
- [x] `CRQ-010` Preserve internal lifecycle and Agent terminology.

- [x] `CRQ-011` Render canonical program and university names in Applied for entries.
- [x] `CRQ-012` Keep clickable request cards visually unchanged on hover.

- [x] `CRQ-013` Make the right context sidebar a peer of the whole central Request workspace, aligned from the Request header level.
- [x] `CRQ-014` Keep Request navigation between Request header and tab content.
- [x] `CRQ-015` Add uploaded-document summary/statuses to the context sidebar.
- [x] `CRQ-016` Add existing program preferences and edit path to the context sidebar.
- [x] `CRQ-017` Keep Overview as one central vertical flow: attention, applied-for programs, progress, then recent messages.
- [x] `CRQ-018` Preserve unread state until the customer opens Request Messages.
- [x] `CRQ-019` Present customer-friendly Request statuses without changing Lead lifecycle values.

- [x] `CRQ-020` Tighten Request Overview information density, replace generic
  attention copy with explicit message/document actions, and normalize customer
  document statuses to Approved / Under review / Needs replacement.

- [x] `CRQ-021` Keep the customer Request header status-only; route actions, attention, and TurkDemy work to their dedicated Overview sections.
- [x] `CRQ-022` Distinguish unread-message attention from concrete required actions.
- [x] `CRQ-023` Enrich customer progress labels with recorded document/program context.
- [x] `CRQ-024` Use customer-safe advisor identity in recent-message previews.

- [x] `CRQ-025` Apply one-concept/one-label/one-primary-action presentation economy.
- [x] `CRQ-026` Show customer Request identity once with a simple My Requests back link.
- [x] `CRQ-027` Simplify the Overview program summary to Applied programs with direct program rows.
- [x] `CRQ-028` Simplify the timeline heading to Progress.
- [x] `CRQ-029` Simplify the message summary to Recent messages with View all.
- [x] `CRQ-030` Remove the redundant Files eyebrow from Uploaded documents.
- [x] `CRQ-031` Remove Study and the duplicate preference edit action.

- [x] `CRQ-032` Remove duplicate Profile / Request profile identity from customer Profile content.
- [x] `CRQ-033` Group customer Profile facts into personal, location/nationality, passport, and education sections.
- [x] `CRQ-034` Move the single customer Edit profile action into Profile content while preserving finalized and Agent behavior.
- [x] `CRQ-035` Keep Profile person-focused and leave preferences/documents in the persistent context sidebar.
- [x] `CRQ-036` Present Profile as one compact grouped panel with responsive fact grids.

- [x] `CRQ-037` Expand customer Profile read-only data to cover every customer-editable profile field, with the Request title owning the name.
- [x] `CRQ-038` Add a field-alignment/placeholder contract between Profile display and customer editing.
- [x] `CRQ-039` Clean existing customer Edit Profile wording/actions and return path.
- [x] `CRQ-040` Remove internal recommendation workflow control from customer Profile editing while preserving intake/Agent behavior.
- [x] `CRQ-041` Align customer Profile view/edit semantic sections.

- [x] `CRQ-042` Simplify the Programs tab to one Programs heading plus one Find programs action.
- [x] `CRQ-043` Make each customer program card the complete program-detail click target with program-first hierarchy.
- [x] `CRQ-044` Keep Added by you / Suggested by your advisor as secondary provenance labels.
- [x] `CRQ-045` Use the customer-facing Select intake placeholder while keeping concrete selected-offering metadata.
- [x] `CRQ-046` Remove the duplicate Browse programs empty-state action.
- [x] `CRQ-047` Keep Program preferences exclusively in the persistent Request context sidebar.


- [x] `CRQ-048` Enrich compact Overview program rows with degree, language, and offering-backed tuition.
- [x] `CRQ-049` Keep tuition grounded in selected/active ProgramOffering data and label fallback pricing as From.
- [x] `CRQ-050` Make Programs the detailed comparison workspace with level, language, tuition, duration, intake, and provenance.
- [x] `CRQ-051` Add customer select/change-intake workflow constrained to active offerings of the same program.
- [x] `CRQ-052` Add customer program removal with ownership/finalized guards.
- [x] `CRQ-053` Keep advisor provenance informational; do not add accept/reject/add-to-request states.
- [x] `CRQ-054` Replace whole-card anchors with a primary detail link so management forms remain valid interactive markup.

- [x] `CRQ-055` Collapse intake management to one auto-submit dropdown with current offering or Select intake placeholder.
- [x] `CRQ-056` Move removal to an accessible confirmed trash-icon action at program-card level.
- [x] `CRQ-057` Surface Agent `suggestion_reason` to customers without exposing internal `notes`.
- [x] `CRQ-058` Preserve finalized Request read-only behavior for intake and removal controls.
- [x] `CRQ-059` Make Programs-workspace cards fill the available column width and keep card widths consistent.

- [x] `CRQ-060` Render advisor recommendation reasons on a separate bidi-aware readable line beneath provenance.
- [x] `CRQ-061` Keep Agent-less customer Requests renderable and make Request messaging safely unavailable until assignment.

- [x] `CRQ-062` Keep Program Detail and Remove in visually distinct locations in LTR and RTL.
- [x] `CRQ-063` Use borderless vector affordances: lightweight Program Detail arrow and neutral-gray trash + Remove action.
- [x] `CRQ-064` Keep the Program Detail arrow at the card top/end and move Remove to a bottom/end footer row beneath intake management.
