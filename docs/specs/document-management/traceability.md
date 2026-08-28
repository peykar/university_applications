# Document management — traceability

Status: BASELINED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `DOC-001` | `apps/leads/views.py::lead_document_upload`, `lead_document_replace`, customer document templates | `tests/test_lead_workflow.py::LeadWorkflowTests::test_finalized_customer_cannot_upload_historical_lead_document`, `test_finalized_customer_cannot_replace_historical_lead_document`, `tests/test_finalized_customer_lead_mutations.py` | Covered |
| `DOC-002` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `DOC-003` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `DOC-004` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `DOC-005` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `DOC-006` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `DOC-007` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `DOC-008` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `DOC-009` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |

## Notes

This baseline intentionally starts at capability level. When a requirement is
changed or newly implemented, replace the family row with requirement-level
code paths and named tests. Do not claim exact traceability that has not been
verified.
