# Applicant intake and program application

When an authenticated customer clicks **Apply** for a program and has no
applicant records, TurkDemy sends them directly to the applicant intake form.
There is no intermediate "create an applicant" empty state.

The intake asks whether the application is for **Myself** or **Someone else**.
For "Myself", known account identity/contact values are prefilled and remain
editable. Choosing "Someone else" clears those prefills.

Lead intake is intentionally permissive: applicant fields are optional so a
customer can express interest with incomplete information. Staff/agents can
collect and validate missing data later. The selected program is preserved in
`next_program` and is automatically attached to the newly created lead.

Customers who already manage one or more applicants still see the applicant
picker so they can choose which existing person the program belongs to.


## Applying when applicants already exist

The program application page asks the customer-facing question **Who are you
applying for?** rather than exposing the internal `Lead` model.

Existing people are shown as selectable cards. The applicant matching the
account email is labelled **Myself**. If there is no matching self applicant,
**Myself** can create one directly. **Someone new** expands an inline,
lightweight applicant form; all identity/contact fields in that panel are
optional.

The second step is labelled **When would you like to start?** rather than
`Offering`. The customer can choose a concrete intake or leave **Any intake /
decide later**.

Submitting a new person creates the Lead and program interest atomically.

## Application vs interest

A customer clicking **Apply** creates/promotes the program relation to the
explicit `applied` state. Generic saved interests remain `interested`, user
shortlists remain `shortlisted`, and agent/system suggestions are presented as
recommendations.

On the applicant page the section is labelled **Applications & program
interests**. Applied programs show the selected intake, or **Any intake /
decide later** when no specific offering was chosen.


## Simplified applicant program list

Applicant programs are now deliberately modeled as a simple association list.
There are only two origins:

- **User-added** — selected by the customer/applicant.
- **Agent-suggested** — recommended by an advisor.

There is no interested/shortlisted/applied/qualified/suggested status workflow
on the applicant-program association, and there are no system-generated
suggestions.

The program list is collaborative context for the applicant and advisor. It is
not itself the formal university application workflow. Converting a Lead into a
Student therefore does not automatically create `Application` records from
these associations. Formal applications are created separately after the agent
and applicant decide which programs to proceed with.


Agent Workspace program names link to the public program detail page in a new
tab so advisors can inspect the catalogue entry without losing their place in
the applicant workspace.


## Customer Request program workspace

For customers, Request-stage program interests are presented as **Programs**, not as formal applications. Overview gives a compact comparison with university, degree, language, tuition, and provenance. The dedicated Programs tab adds duration, selected intake, and management. Customers can select/change an active intake belonging to that program or remove the program while the Request is editable. Advisor suggestions use the same management behavior as customer-added programs; no accept/reject step is introduced. Formal Application terminology remains reserved for post-finalization university applications.

### Customer program intake interaction

In an editable Request, each program uses one intake dropdown. The selected offering is preselected; otherwise the control shows **Select intake**. Choosing an option immediately submits and returns to the Programs tab, so there is no separate Select/Save/Change button. Program removal is a separate card-level trash action. Agent-suggested programs show the Agent's `suggestion_reason` when provided; generic internal notes are not exposed to the customer.

### Customer program recommendation notes

On the customer Request Programs workspace, an Agent recommendation may include `suggestion_reason`. When present it is shown directly below **Suggested by your advisor** as readable customer context with automatic text direction (`dir="auto"`). The generic LeadProgramInterest `notes` field remains internal and is not exposed.


### Customer Documents workspace

The customer Documents tab is a focused full-width workspace with no Request context sidebar. Document type is the customer-facing identity and direct file link; stored filenames are hidden. On mobile, the heading and single Upload document action share one row, ordinary document cards stay compact, and all five Request-local tabs remain visible without clipping.
