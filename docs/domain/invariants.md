# Domain invariants

These invariants summarize cross-capability rules already established by the baselined specifications. Requirement IDs remain the authoritative source; this document is a navigation aid, not a replacement for specs.

- **INV-LEAD-001** — A finalized Lead is not an editable active applicant; finalization is duplicate-safe and links the Lead to a Student (`FIN-004`, `FIN-006`).
- **INV-FIN-001** — Successful conversion creates the Student even when zero discussed programs are selected; every selected discussed program requires an active offering and creates one DRAFT Application, selected documents alone transfer, and all resulting database changes are atomic (`FIN-007`–`FIN-017`).
- **INV-APP-001** — Every formal Application belongs to exactly one Student and one concrete ProgramOffering (`APP-001`).
- **INV-APP-002** — The same Student and ProgramOffering cannot have a second active Application (`APP-004`).
- **INV-DOC-001** — Applicant document review state is explicit. Verified documents default to transfer; any document may be selected or deselected, and a selected unverified document is approved during successful conversion before transfer (`DOC-*`, `FIN-011`–`FIN-014`).
- **INV-TODO-001** — Every TODO belongs to exactly one Agent organization; its optional generic subject is represented by an all-or-nothing ContentType/object-id pair (`TODO-001`, `TODO-007`).
- **INV-TODO-002** — DONE records completion actor/time, and DONE/CANCELLED are reopenable (`TODO-004`).
- **INV-AGENT-001** — Agent-scoped operational data and actions remain within the active/owning Agent scope (`PERM-*`, `ASN-*`, `TODO-002`).

When an invariant changes, update the governing requirement first and then this summary.

- **INV-APP-003** — Discussion history is not persistently coupled to formal Applications; `LeadProgramInterest` does not own an Application pointer (`FIN-009`, `APP-006`).
