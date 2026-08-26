# Lead lifecycle

Lead status is intentionally small and derived from real workflow state:

- `new`: created and not assigned to an agent user.
- `assigned`: `assigned_to` contains the agent user responsible for the lead.
- `finalized`: the lead has been converted to a `Student`.
- `closed`: the lead was explicitly closed without conversion.

All active users of the lead's `Agent` can see the lead. `assigned_to` represents
responsibility, not authorization. Any agent user with access to the lead can use
**Assign to me**, including taking responsibility from another user; the change is
recorded as a LeadActivity.

Closing is a manual terminal workflow action with optional `close_reason`,
`closed_by`, and `closed_at`. A closed lead can be reopened; it returns to
`assigned` when it still has an assignee, otherwise `new`.

Validation is not a lead status. `finalize_lead()` performs validation and records
validation metadata. Conversion to `Student` sets the lead status to `finalized`.


## Agent-user responsibility

Every active user belonging to the Lead's `Agent` can see the Lead. The
`assigned_to` field only identifies the person responsible for handling it.

Agent Workspace shows the responsible user's real display name, adding
**(You)** for the current user. Active leads support:

- **Assign to me** — immediately take responsibility.
- **Assign agent** — choose an active user of the Lead's Agent when unassigned.
- **Reassign** — move responsibility to another active user of the same Agent.

Assignment and reassignment are recorded in `LeadActivity`.

Responsibility actions are grouped directly under **Responsible agent**. Closing is separated as a lifecycle action at the bottom of the Applicant card.

**Close applicant** uses a compact outlined destructive-secondary button so it remains discoverable without competing with primary responsibility actions.


## Finalizing from Agent Workspace

The responsible agent user can finalize an active assigned lead. **Finalize
applicant** opens a confirmation/review modal showing the minimum Student fields
(first name, last name, nationality, and gender) plus useful context. Submission
runs the existing validation service and then converts the Lead to Student.

Finalization creates/reuses the Student, copies verified documents, sets
`converted_student`/`converted_at`, changes status to `finalized`, and records
the existing validation/finalization activities and system messages. Optional
Student fields are not required. If required information is missing, conversion
is not performed and the agent receives the validation errors.

Only the currently responsible agent user may finalize. Other users of the Agent
can still view the lead and can use **Assign to me** first.


## Agent-maintained applicant data

Agent users can update active Lead data directly from Agent Workspace when they
collect information by phone, email, chat, or another offline channel. Lead
fields remain permissive; the strict minimum is enforced only at finalization.
An edit creates an internal LeadActivity describing which fields changed.

Agents can also upload documents received outside the portal. The upload asks
for document type, file, and optional description; the original filename is
derived from the uploaded file rather than entered separately. The document
enters the normal Lead document review workflow and an internal
`DOCUMENT_UPLOADED` activity records that an agent user added it.

After finalization, Lead data is no longer edited and documents are no longer
uploaded to the Lead; subsequent maintenance belongs on the Student record.


Agent Workspace keeps **Edit applicant** and **Upload document** as compact
section-level secondary actions so Finalize remains the primary lifecycle
action. The Applicant section also exposes a subtle last-updated indicator;
hovering it shows who last updated the Lead and when, using the existing
`updated_by` and `updated_at` audit fields.


The Agent Workspace **Edit applicant** modal is grouped into Personal
information, Contact & residence, Passport, Education & language, Family, and
Internal notes. Optional fields are explicitly marked, and the Save/Cancel
footer remains sticky while scrolling.

Lead edit activities preserve old and new values for every changed field in an
internal `LeadActivity`, so shared agent teams can see exactly what changed
without exposing those details to the applicant.


## Internal notes and activity history

Agent Workspace shows the current `Lead.notes` in a dedicated **Internal notes**
panel marked as agent/staff-only. Agents can update notes from a small modal,
which creates an internal `LeadActivity` containing the previous and new note
content.

The **Activity** panel renders the latest LeadActivity records as a timeline.
Each entry shows the activity type, actor, timestamp, description, and whether
the event is internal or customer-visible. The timeline is newest-first and
loads actor information with `select_related("created_by")`.


### Structured activity metadata

`LeadActivity` now has a `metadata` JSON field for structured audit details.
Applicant edits and internal-note edits store field-level changes as
`label`/`old`/`new` values rather than embedding them in one long description.
The Agent Workspace renders those changes as scannable rows.

The timeline initially shows the 10 newest activities and offers **Show more**
when older entries exist. Because the whole Activity panel is agent-only,
ordinary internal entries no longer repeat an Internal badge; only
customer-visible events receive a visibility badge.


### LeadActivity metadata migration compatibility

The structured activity `metadata` field is part of the initial schema for
fresh and test databases. Migration `0016_leadactivity_metadata` is also kept
as an idempotent compatibility migration for existing databases: it inspects
the physical `LeadActivity` table and adds the column only if it is missing.


### Migration test policy

TurkDemy periodically recreates/squashes its development migrations, so tests
must not depend on a particular migration filename or on the presence of a
historical compatibility migration. Fresh schema correctness is exercised by
Django's test database creation and the application test suite. Existing
deployed databases should run the migration generated for their own migration
history before deploying a model schema change.


### Human-readable audit changes

Agent applicant edits now use the dedicated **Applicant data updated** activity
type rather than generic **Note**. Internal-note edits use **Internal notes
updated**. Audit values are normalized before comparison/storage: model-choice
PKs are resolved to labels, choice codes to display labels, booleans to Yes/No,
and dates to ISO text. Fields whose normalized old/new values are equal are not
recorded, preventing false changes such as a Country UUID → "Netherlands".


### Internal notes and activity page

Internal notes are treated as operationally important content on the main
Applicant page. The long privacy helper sentence was replaced by a compact
**Private** badge whose tooltip explains that notes are visible only to
agent/staff users.

The full Lead activity/audit log moved to a dedicated applicant Activity page
at `/agent/applicants/<lead-id>/activity/`. The main Applicant page links to
this page from the Internal notes header, keeping the daily workspace focused
while preserving access to the complete audit trail.


### Activity UI regression tests

Activity timeline assertions target the dedicated `applicant_activity.html`
template. The applicant detail regression tests assert that the timeline is
absent there and that navigation to the Activity page remains available.


### Activity page context, filters, and pagination

The dedicated Activity page keeps applicant context visible at the top: name,
status, responsible agent user, and Agent organization. Timeline spacing is
denser for audit-log use.

Activity can be filtered by All, Applicant data, Documents, Assignment &
status, and Programs. Results are paginated at 25 events per page instead of
being permanently truncated to the latest 100 records.


The Activity page also has a dedicated **Notes** filter. It includes both
legacy/general `NOTE` activities and the dedicated `INTERNAL_NOTES_UPDATED`
events. **Applicant data** is limited to applicant-field update activities.


### Agent-uploaded document review behavior

Documents uploaded directly by an agent user are trusted as an agent-side
action and do not enter the pending review queue. They are created as
**Approved**, marked verified, and receive `reviewed_by` / `reviewed_at`
metadata immediately. A `LeadDocumentReviewHistory` row is also created so the
approval remains auditable.

Documents uploaded by the applicant, or promoted from a customer chat
attachment, continue through the normal review workflow.


### Phone validation during finalization

Lead finalization validates a non-empty cell number before creating the Student.
The number must be valid in international format (for example,
`+31612345678`). Invalid or locally formatted numbers are returned to the
agent as a normal validation error instead of raising a `NumberParseException`
during `Student.save()`.

The shared `normalize_phone_number()` helper converts `phonenumbers` parsing
exceptions to `ValueError`, giving callers one stable validation contract.


### Atomic Lead finalization

Agent-facing finalization is one atomic business operation. There is no
agent-visible or persisted "validated, ready for conversion" phase.

`finalize_lead()` now performs the complete transition inside one database
transaction:

1. Reject closed Leads and reuse an already converted Student.
2. Validate all required Lead data, including international phone format.
3. Create the canonical Student from Lead fields.
4. Copy only verified Lead documents to Student documents.
5. Link `Lead.converted_student`.
6. Set validation/conversion audit timestamps and actor.
7. Set `Lead.status = FINALIZED`.
8. Create one FINALIZED activity and one customer-visible system message.

If validation, Student creation, document copying, or any later database step
fails, the transaction rolls back. The Lead therefore remains in its previous
lifecycle state (normally ASSIGNED), no intermediate VALIDATED activity is
created, and the agent receives the validation error on the Applicant page.

Program interests, messages, and Lead activity history remain attached to the
Lead; program interests do not automatically become Applications.
