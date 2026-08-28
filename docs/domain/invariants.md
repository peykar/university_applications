# Domain invariants

These invariants summarize cross-capability rules already established by the baselined specifications. Requirement IDs remain the authoritative source; this document is a navigation aid, not a replacement for specs.

- **INV-LEAD-001** — A finalized Lead is not an editable active applicant; finalization is duplicate-safe and links the Lead to a Student (`FIN-004`, `FIN-006`).
- **INV-APP-001** — Every formal Application belongs to exactly one Student and one concrete ProgramOffering (`APP-001`).
- **INV-APP-002** — The same Student and ProgramOffering cannot have a second active Application (`APP-004`).
- **INV-DOC-001** — Applicant document review state is explicit; approved documents are the documents eligible for established finalization/conversion behavior (`DOC-*`, `FIN-004`).
- **INV-TODO-001** — Every TODO belongs to exactly one Agent organization; its optional generic subject is represented by an all-or-nothing ContentType/object-id pair (`TODO-001`, `TODO-007`).
- **INV-TODO-002** — DONE records completion actor/time, and DONE/CANCELLED are reopenable (`TODO-004`).
- **INV-AGENT-001** — Agent-scoped operational data and actions remain within the active/owning Agent scope (`PERM-*`, `ASN-*`, `TODO-002`).

When an invariant changes, update the governing requirement first and then this summary.
