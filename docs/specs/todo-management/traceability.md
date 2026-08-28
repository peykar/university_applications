# TODO Management — Traceability

| Requirement | Implementation | Verification |
| --- | --- | --- |
| TODO-001..003 | `apps/operations/models.py::Todo`, `services.create_todo` | `tests/test_operations_sdd.py` |
| TODO-004 | `TodoStatus`, `services.update_todo` | `test_todo_lifecycle_matches_baseline` |
| TODO-005 | operations templates/CSS | source + UI verification |
| TODO-006 | `TodoComment` | `test_todo_comments_are_immutable` |
| TODO-007..008 | generic subject fields, `subjects_for_parent` | `test_parent_aggregation_includes_applications_for_lead` |
| TODO-009 | `_record_private_activity`, `_agent_application_activity` | `test_activity_integration_is_private_for_applicant` |
| TODO-010 | Agent URLs/sidebar/entity nav | `test_global_and_contextual_routes_exist` |

BUG-0005 follow-up: TODO form creation binds the active Agent before ModelForm model validation; covered by `tests/test_operations_sdd.py::OperationsSDDTests::test_todo_form_binds_active_agent_before_model_validation`.
