# Canonical business rules

These rules are cross-capability invariants. Capability specs may refine them but
must not contradict them without an approved ADR and explicit rule change.

## Identity and ownership

BR-ID-001 — A User may own/manage multiple Leads.

BR-ID-002 — A User may belong to multiple Agent organizations.

BR-ID-003 — An Agent represents an organization, not a single user profile.

## Agent context and authorization

BR-AGT-001 — Agent workspace queries are scoped to exactly one active Agent.

BR-AGT-002 — A session-stored Agent ID is never trusted without revalidating
current membership.

BR-AGT-003 — `Lead.assigned_to` represents responsibility, not authorization.
Authorized active users of the Lead's Agent can access the Lead.

BR-AGT-004 — Entity-detail URLs must not be carried across an Agent organization
switch.

## Applicant lifecycle

BR-APL-001 — Lead data is provisional and may be incomplete before finalization.

BR-APL-002 — Active unassigned Leads are `new`; active assigned Leads are
`assigned`; successful conversion is `finalized`; explicitly stopped cases are
`closed`.

BR-APL-003 — A closed Lead can be reopened. It returns to `assigned` when an
assignee remains and otherwise to `new`.

BR-APL-004 — Only the responsible Agent user finalizes an active Lead.

## Finalization

BR-FIN-001 — Lead finalization validates before conversion and must not leave a
partial Student conversion.

BR-FIN-002 — Successful finalization creates/reuses the Student, copies approved
documents, links Lead→Student, records conversion time and marks the Lead
`finalized`.

BR-FIN-005 — Finalization allows the responsible Agent to select zero or more
discussed Program interests. Selecting none MUST NOT block Student finalization.
Each selected interest MUST resolve to a concrete active ProgramOffering and MUST
create a DRAFT Application as part of the same atomic finalization operation.

BR-FIN-003 — Failed finalization leaves the Lead active and reports validation
errors.

BR-FIN-004 — After finalization, person/document maintenance belongs to the
Student workflow rather than editing the historical Lead.

## Programs and offerings

BR-PRG-001 — A Program belongs to one University. A referenced Department must
belong to the same University.

BR-PRG-002 — Intake-specific tuition, quota and deadline belong to
ProgramOffering.

BR-PRG-003 — LeadProgramInterest is exploratory. It is never itself a formal
Application.

BR-PRG-004 — Program-interest source is `user` or `agent`. There is no
system-suggested source.

BR-PRG-005 — An Agent recommendation must not overwrite a user-created interest
for the same program-level interest.

## Applications

BR-APP-001 — Formal relationship:
`Student -> Application -> ProgramOffering -> Program -> University`.

BR-APP-002 — A formal Application belongs to the finalized Student and a concrete
ProgramOffering. Finalization itself creates draft Applications for the discussed
programs explicitly selected by the responsible Agent.

BR-APP-003 — Application tuition/deposit are snapshots; later Offering price
changes do not retroactively alter existing Application values.

BR-APP-004 — A second active Application for the same Student and
ProgramOffering is prohibited. Rejected, Withdrawn and Cancelled applications
are inactive for this duplicate rule.

## Documents

BR-DOC-001 — Student documents are reusable master documents.

BR-DOC-002 — ApplicationDocument is application-scoped and may reference only a
StudentDocument owned by the Application's Student.

BR-DOC-003 — Lead document review states are `pending`, `approved`, and
`replacement_requested`.

BR-DOC-004 — Customer replacement preserves the previous document/version and
review history.

BR-DOC-005 — Agent-uploaded Lead documents follow the established review/audit
workflow and are treated as trusted agent submissions according to the current
workflow.

BR-DOC-006 — Attaching an ApplicationDocument does not by itself define a
university requirement. Requirements are a separate concern.

## Messaging

BR-MSG-001 — Messaging is generic and subject-scoped rather than Lead-specific.

BR-MSG-002 — A Conversation binds Agent + customer + generic subject.

BR-MSG-003 — Read/unread state is per Conversation + User + participant role.

BR-MSG-004 — Agent users in the same organization have independent unread state.

## Audit

BR-AUD-001 — Applicant data changes made from customer or Agent workflows use
the shared audit normalization/recording behavior.

BR-AUD-002 — Internal notes are Agent/staff-only.

BR-AUD-003 — Audit/version history is preserved; it must not be deleted merely
to simplify current-state UI.

## Geography

BR-GEO-001 — Student country of residence uses the country catalogue.

BR-GEO-002 — City of residence is free text; a complete worldwide city
catalogue is not required.

## Catalogue

BR-CAT-001 — YÖK recognition and MOE/MOH approval belong to University, not
Program.

BR-CAT-002 — University/Program listing priority is an internal ordering input,
not a claim of quality, popularity, sponsorship or academic rank.
