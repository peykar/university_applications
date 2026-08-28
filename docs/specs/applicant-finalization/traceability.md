# Applicant finalization — traceability

Status: BASELINED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `FIN-001` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `FIN-002` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `FIN-003` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `FIN-004` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `FIN-005` | `apps/leads/services/conversion.py::finalize_lead` | `tests/test_lead_workflow.py::LeadWorkflowTests::test_finalization_records_single_finalized_activity_and_validation_metadata`, `tests/test_atomic_lead_finalization.py` | Covered |
| `FIN-006` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |

## Notes

This baseline intentionally starts at capability level. When a requirement is
changed or newly implemented, replace the family row with requirement-level
code paths and named tests. Do not claim exact traceability that has not been
verified.
Finalization UI follow-up: `BUG-0006-applicant-modal-actions-not-working` verifies that the Agent finalization modal JavaScript is rendered.
