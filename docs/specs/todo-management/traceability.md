# TODO Management — Specification — traceability

Status: BASELINED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `TODO-001` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `TODO-002` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `TODO-003` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `TODO-004` | `TodoStatus`, `services.update_todo` | `test_todo_lifecycle_matches_baseline` | Covered |
| `TODO-005` | operations templates/CSS | source + UI verification | Covered |
| `TODO-006` | `TodoComment` | `test_todo_comments_are_immutable` | Covered |
| `TODO-007` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `TODO-008` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `TODO-009` | `_record_private_activity`, `_agent_application_activity` | `test_activity_integration_is_private_for_applicant` | Covered |
| `TODO-010` | Agent URLs/sidebar/entity nav | `test_global_and_contextual_routes_exist` | Covered |

## Notes

BUG-0005 follow-up: TODO form creation binds the active Agent before ModelForm model validation; covered by `tests/test_operations_sdd.py::OperationsSDDTests::test_todo_form_binds_active_agent_before_model_validation`.
