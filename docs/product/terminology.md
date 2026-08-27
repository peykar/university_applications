# Domain terminology

This vocabulary is normative. New specs should use these terms consistently.

**User** — authenticated TurkDemy account. One user may manage multiple
Applicants and may also belong to one or more Agent organizations.

**Agent** — an agency/company organization. It is not a user profile.

**Agent user** — a User associated with an Agent organization.

**Active Agent** — the one Agent organization currently selected for an Agent
workspace session. It determines workspace scope.

**Applicant / Lead** — provisional admissions case owned by a User. `Lead` is
the current model name; UI generally says Applicant.

**Responsible agent** — Agent user assigned to a Lead. Responsibility does not
restrict visibility from other authorized users of the same Agent.

**Study preferences** — optional constraints/interests stored for a Lead, such
as tuition range, languages, cities, universities and departments.

**Program interest** — exploratory relationship between a Lead and Program,
optionally a concrete ProgramOffering. It is not a formal Application.

**Agent recommendation** — Program interest whose source is `agent`, optionally
with a recommendation reason and suggesting Agent user.

**Student** — validated/finalized admissions person created from a Lead.

**Program** — academic program belonging to one University.

**ProgramOffering** — intake-specific instance of a Program with academic year,
semester, tuition, quota/deadline and related commercial data.

**Application** — formal Student application to a concrete ProgramOffering.

**StudentDocument** — reusable master document belonging to a Student.

**ApplicationDocument** — document attached/selected for one Application.

**Conversation** — generic Agent/customer communication channel scoped to a
domain subject such as Lead, Student or Application.

**Activity** — auditable Lead workflow event, potentially customer-visible or
internal.

**Workspace** — authenticated information architecture context. Current primary
workspaces are My TurkDemy and Agent workspace.

**Entity navigation** — contextual third-level navigation for one Applicant or
one Application.
