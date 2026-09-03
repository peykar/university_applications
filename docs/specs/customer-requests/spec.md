# Customer requests

Status: APPROVED
Version: 1.27

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
stack below the main content on narrower layouts, and later tab-specific requirements MAY
remove it when the active task benefits from a focused mobile/full-width workspace.

CRQ-014 — Request navigation MUST remain inside the central Request workspace,
after the Request header and before page-specific content, with **Overview**,
**Profile**, **Programs**, **Documents**, and **Messages** as customer tabs.

CRQ-015 — The Request context sidebar MUST persist across Request detail tabs except
where a later tab-specific requirement explicitly removes it, and MUST include a
compact **Uploaded documents** summary with review state and access to document
management/upload when the sidebar is present.

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

CRQ-032 — The customer Request **Profile** tab MUST use **Profile** as its single workspace title and MUST NOT repeat that identity with decorative **Profile** eyebrows or **Request profile** headings. The shared Request header continues to own the person name; Profile content beneath the page-title row MUST begin with meaningful person-information sections.

CRQ-033 — Customer Profile information MUST be grouped by meaning: **Personal information**, **Identity & nationality**, **Residence**, **Passport**, and **Education & language**. The Request person's name MUST remain in the shared Request header and MUST NOT be repeated inside Profile content.

CRQ-034 — Customer Profile MUST expose at most one **Edit profile** action. When the Request is editable, that action MUST live on the Profile page-title/action row rather than appearing in the shared Request header or inside a person-information subsection. Finalized Requests MUST NOT expose the customer edit action. Agent-facing **Edit applicant** behavior remains unchanged.

CRQ-035 — The customer Profile tab MUST remain person-focused and MUST NOT duplicate **Program preferences** or uploaded-document context already owned by the persistent Request context sidebar. The context sidebar MUST continue to render beside Profile using the same Request detail layout.

CRQ-036 — Profile groups MUST use a compact, scan-friendly presentation inside one primary Profile panel, with clear section boundaries and responsive fact grids rather than separate decorative cards or repeated page-level headings.

CRQ-037 — Customer Profile read-only content MUST represent every field that the customer can edit in the existing Request profile editor, except the person's first/middle/last name MAY be represented once by the shared Request title instead of repeated in the Profile body. The read-only groups MUST include country of birth, residence address, passport issuing authority and dates, English test details, high-school GPA details, and educational background in addition to the previously shown fields.

CRQ-038 — Customer Profile display and customer Profile editing MUST remain field-aligned: adding a new customer-editable profile field requires adding a corresponding customer-visible read-only representation, unless an explicit customer-requests SDD requirement documents why that field is intentionally hidden. Missing values MUST render a stable placeholder rather than disappearing from the Profile layout.

CRQ-039 — The existing customer **Edit profile** page MUST use customer-facing Request/Profile terminology and MUST NOT expose internal Applicant/finalization workflow wording. Editing an existing Request MUST use **Edit profile**, **Save changes**, and return/cancel to the Request Profile tab.

CRQ-040 — Internal workflow controls such as **needs program recommendation** MUST NOT render in the existing customer Profile editor. Customer program-preference/help flows remain separate; Agent-side recommendation controls and the initial Request-intake behavior MAY continue to use the underlying domain flag where required.

CRQ-041 — Customer Profile editing MUST preserve the same semantic grouping as the read-only Profile wherever practical: Personal information, identity/nationality and residence, Passport, and Education & language. The read-only Profile MAY split identity/nationality and residence into separate scan-friendly sections without changing field ownership.

CRQ-042 — The customer Request **Programs** tab MUST use **Programs** as its single section heading and MUST NOT repeat the tab identity with a decorative Programs eyebrow. The tab MAY expose one **Find programs** action because adding another program is the primary workflow on this page.

CRQ-043 — Every program shown on the customer Programs tab MUST provide a large, clear primary link to that program's public detail page. Program name MUST be the strongest card label, followed by university and compact comparison metadata; program-level management controls MUST remain separate interactive elements and the card MUST NOT require a separate View details label.

CRQ-044 — Customer program cards MUST preserve provenance without letting provenance dominate the card hierarchy: Agent-originated interests MUST show **Suggested by your advisor** and customer-originated interests MUST show **Added by you** as secondary source labels.

CRQ-045 — Program intake presentation on the customer Programs tab MUST use the selected offering in the intake control when one exists and MUST use the customer-facing placeholder **Select intake** when no offering is selected. The internal phrase **Any intake / decide later** MUST NOT render on this customer page.

CRQ-046 — The customer Programs tab MUST expose only one browse/add-program action. When the persistent header-level **Find programs** action is present, the empty state MUST provide explanatory copy without adding a second **Browse programs** button.

CRQ-047 — The customer Programs tab MUST remain focused on programs associated with the Request and MUST NOT duplicate the **Program preferences** summary/edit UI owned by the persistent Request context sidebar.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by named tests or repository checks in traceability.


CRQ-048 — Request Overview program rows MUST remain compact but MUST add the program's degree level, language, and tuition when tuition data is available, while preserving program name, university, provenance, and direct program-detail navigation.

CRQ-049 — Tuition displayed for a Request program MUST come from ProgramOffering data. When a specific offering is selected, its discounted tuition when available (otherwise standard tuition), currency, and fee basis MUST be shown. When no offering is selected, the UI MAY show a clearly labelled **From** price from an active offering and MUST NOT imply that this is a selected intake price.

CRQ-050 — The Programs tab MUST function as the detailed program-comparison workspace and MUST show degree, language, tuition, duration when known, intake, and provenance without duplicating long-form catalogue content already available on Program Detail.

CRQ-051 — While a Request is editable, the customer MUST be able to select or change the ProgramOffering/intake for an existing Request program. The selected offering MUST belong to that same program and be active; no selected offering MUST be represented by the **Select intake** placeholder.

CRQ-052 — While a Request is editable, the customer MUST be able to remove a program interest from the Request. Intake changes and removal MUST be scoped to a Request owned by the authenticated customer, and finalized Requests MUST reject these mutations.

CRQ-053 — The Programs workspace MUST NOT introduce accept/reject or add-to-request approval states for advisor suggestions. Once a program interest exists on the Request, provenance is informational and both customer-added and advisor-suggested interests use the same intake/removal management model.

CRQ-054 — Because program cards now contain management controls, the Programs workspace MUST use a clear program-detail link as the primary informational click target rather than nesting forms inside a whole-card anchor. The program name/content area and directional affordance MUST remain visibly navigable to Program Detail.


CRQ-055 — Each editable Request program MUST expose exactly one intake dropdown. When an intake is already selected, that offering MUST be the selected option; otherwise **Select intake** MUST be selected. Changing the dropdown MUST immediately submit the intake form and return the customer to the Programs page without a separate Select, Save, or Change intake button.

CRQ-056 — Program removal MUST remain a program-level action separate from intake selection. The Programs card MUST represent removal with a conventional trash-bin icon, provide an accessible **Remove program** label, and request confirmation before submitting the removal form. The icon control MUST be visually neutral: gray, borderless, and without a persistent surrounding button box.

CRQ-057 — For Agent-originated program interests, the Programs workspace MUST show `suggestion_reason` as customer-visible advisor context when it is non-empty. It MUST NOT expose the generic/internal `notes` field. Customer-originated interests MUST NOT render an empty advisor-note area.

CRQ-058 — Finalized Requests MUST keep program management read-only: intake controls and removal controls MUST not render, while the selected intake (or **Not selected**) MAY be shown as read-only context.

CRQ-059 — Program cards in the dedicated Programs workspace MUST fill the available width of their holding Programs column rather than shrink to content width. Card widths MUST remain consistent regardless of program title, metadata, recommendation note, or intake state.

CRQ-060 — When an Agent recommendation has a customer-visible `suggestion_reason`, the Programs workspace MUST render the advisor provenance label and the recommendation explanation as separate visual lines. The explanation MUST use normal readable body styling and automatic bidirectional text direction so Persian, Arabic, English, and other note content renders naturally.

CRQ-061 — A customer Request MUST remain viewable when its Lead has no Agent organization assigned. Request Overview/Profile/Programs/Documents MUST render without creating an invalid Conversation; unread/recent-message summaries MUST behave as empty until an Agent is assigned. The Request Messages tab MUST explain that messaging becomes available after advisor assignment and MUST NOT render a compose form while no Agent is available.


CRQ-062 — In editable Programs-workspace cards, the program-detail directional affordance and the program-removal action MUST occupy visually distinct locations so navigation and removal cannot be mistaken for one another in either LTR or RTL layouts.

CRQ-063 — Program-card navigation and removal affordances MUST be borderless. Program Detail MUST use a lightweight vector arrow rather than a boxed/circular control, and Remove MUST use a neutral-gray borderless trash affordance with accessible text and focus behavior.

CRQ-064 — The Program Detail arrow MUST occupy the card's top inline-end action position. The Remove action MUST be moved out of that top action position and rendered at the bottom inline-end of the card, below intake management, so destructive action is visually separated from primary navigation.

CRQ-065 — The customer Documents tab MUST use one page identity, **Documents**, without a decorative Documents eyebrow or duplicate **Request documents** heading.

CRQ-066 — Customer document cards MUST use the document type as the customer-visible document name and MUST NOT expose the stored/uploaded filename in the Documents workspace.

CRQ-067 — Each customer document card MUST show a clear review state using **Approved**, **Under review**, or **Needs replacement**, and MUST provide a lightweight document-open affordance without relying on the filename as the link label.

CRQ-068 — When replacement is requested, the customer document card MUST show the Agent review note when present and MUST expose the replacement action on that card; ordinary approved/under-review cards MUST remain compact.

CRQ-069 — The Documents workspace MUST expose only one primary Upload document action when documents exist. When no documents exist, that action MUST move into the empty state rather than being duplicated in the page heading and empty state.

CRQ-070 — While the Documents tab is active, the Request context sidebar MUST NOT render. The Documents workspace owns the complete document task on this page and MUST expand into the available Request-detail width rather than repeating Uploaded documents or Program preferences as side context.


CRQ-071 — The document type label on each customer Documents card MUST itself be a direct link to the uploaded file, in addition to the lightweight directional open affordance. Stored filenames MUST remain hidden.

CRQ-072 — On customer mobile Documents pages, the Documents heading and its upload action MUST remain on one header row when upload is available. Ordinary document cards MUST remain compact, and the open arrow MUST be vertically centered for ordinary cards while replacement-required cards MAY keep top-aligned navigation to preserve expanded content readability.

CRQ-073 — Customer Request tab navigation on mobile MUST present Overview, Profile, Preferences, Programs, Documents, and Messages without clipping or truncating a tab label. At narrow widths, the six-tab navigation MUST use a single-line horizontally scrollable strip with usable tap targets, an unambiguous active state, and no forced label wrapping.


CRQ-074 — The Documents workspace MUST place its page-level action on the opposite logical side of the **Documents** title on desktop and mobile. The action MUST use the primary dark-blue button treatment and MUST be labelled **+ Upload document**. Logical start/end alignment MUST preserve the same title/action relationship in RTL.

CRQ-075 — On narrow mobile widths, the **Documents** title and **+ Upload document** page action MUST remain on the same title row rather than stacking. The action MAY use reduced mobile padding/text size, but MUST retain the primary dark-blue treatment and opposite logical-side alignment.

CRQ-076 — The dedicated Programs workspace MUST follow the Request page-title/action convention: **Programs** occupies logical start and the page-level **Find programs →** action occupies logical end on the same heading row. The action MUST use the same primary dark-blue button treatment as other Request page-level actions, including Documents, and logical alignment MUST preserve the relationship in RTL.

CRQ-077 — On customer mobile Programs pages, each program card MUST collapse to a single vertical content flow rather than retaining a multi-column desktop layout. Program detail content MUST use the card width, intake management MUST render as its own full-width row with a usable full-width dropdown, and Remove MUST remain a horizontal bottom/end action rather than becoming a squeezed or vertically wrapped column. The Programs title and Find programs action MUST remain on one heading row at narrow widths.


CRQ-078 — All customer Request page-level primary actions MUST use one shared visual action class/component so Programs, Documents, Messages, and future Request tabs receive the same height, padding, typography, radius, dark-blue treatment, hover/focus behavior, mobile sizing, and RTL-safe alignment. Action width MUST remain content-driven rather than being forced equal.


CRQ-079 — The customer Profile workspace MUST apply the shared Request page-title/action convention: **Profile** at logical start and **Edit profile →** at logical end on the same row across desktop/mobile/RTL. **Edit profile →** MUST use the shared `request-page-primary-action` visual component used by Programs and Documents.

CRQ-080 — The customer **Messages** tab MUST use **Messages** as its single page
identity and MUST NOT repeat that identity with a decorative Messages eyebrow or
**Messages about this request** heading.

CRQ-081 — Customer Request messages MUST distinguish participant roles clearly:
customer-authored messages MUST be labeled **You** and align to logical end; Agent
messages MUST align to logical start and use the Agent user's full name when
available, otherwise **Your advisor**; system messages MUST be labeled **TurkDemy**
and use a visually distinct neutral centered treatment.

CRQ-082 — Every customer-visible Request message timestamp MUST expose both calendar
date and time on desktop and mobile. Responsive layouts MAY reposition or wrap the
timestamp but MUST NOT remove either date or time.

CRQ-083 — When a Request conversation is open, Messages MUST provide one integrated
composer containing the message textarea, an accessible **Attach file** affordance,
selected-file feedback, and **Send**. The empty-conversation state MUST use that
same composer rather than introducing a separate start-conversation action.

CRQ-084 — On desktop, the Messages tab MUST retain the Request context sidebar. At
customer mobile widths, Messages MUST hide the context sidebar so the conversation
and composer use the available width.

CRQ-085 — Message attachments MUST render as compact clickable file affordances that
open the uploaded attachment without replacing the surrounding conversation
workflow.

CRQ-086 — If an advisor has not yet been assigned, Messages MUST show a customer-safe
unavailable state explaining that messaging becomes available after advisor
assignment and MUST NOT render the composer. If an advisor/conversation exists but
contains no messages, Messages MUST show a concise **No messages yet** state while
keeping the composer available.



CRQ-087 — **Preferences** MUST be a first-class customer Request tab positioned between Profile and Programs. The tab MUST use the existing `/preferences/` Request-local URL and MUST render as active when the Preferences workspace is open.

CRQ-088 — The Preferences tab MUST be a read-only customer workspace with one **Preferences** page identity. It MUST present all customer-editable `LeadPreference` data in semantic groups: **Study preferences**, **University preferences**, **Budget**, and **Other preferences**, using stable empty/no-preference presentation where values are absent.

CRQ-089 — Editable Requests MUST expose one **Edit preferences →** page-level action on the Preferences tab. The action MUST reuse the shared `request-page-primary-action` component and open a dedicated preferences edit route. Saving or cancelling MUST return to the Preferences tab; finalized Requests MUST not render the action and direct edit access MUST be rejected safely.

CRQ-090 — The Program preferences card in Request context MUST remain a compact summary/shortcut on Overview, Profile, Programs, and desktop Messages, linking to the Preferences tab. The Preferences workspace itself MUST suppress the Request context sidebar and use the available Request-detail width so the same preferences are not duplicated beside their own page.

CRQ-091 — The public Apply flow MAY list a customer-owned finalized Request in **Who are you applying for?**. If the customer adds a genuinely new Program to that Request, the system MUST atomically add the Program interest and move the Request to `reopened`; selecting a Program already present on the Request MUST NOT reopen it or duplicate the interest.

CRQ-092 — A reopened Request MUST be customer-presented as **In progress** and its Programs workflow MUST be editable again. The linked Student and existing Applications remain authoritative downstream records.

CRQ-093 — Reopening a converted Request MUST NOT restore Lead profile or Lead-document mutation. Those surfaces remain read-only because person/document maintenance belongs to the existing Student workflow.

CRQ-094 — The public Program conversion path MUST present the primary action as **Start a
Request** and the selection/continuation page MUST use customer-facing Request terminology.
The route MAY retain its internal `apply-program` implementation name, but visible copy MUST
NOT describe the exploratory Program-interest action as a formal Application. Existing
Request reuse/reopen semantics remain unchanged.
