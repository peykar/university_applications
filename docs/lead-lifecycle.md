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
