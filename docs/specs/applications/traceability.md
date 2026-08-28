# Formal applications — traceability

Status: BASELINED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `APP-001` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `APP-002` | `apps/leads/services/conversion.py::finalize_lead`, `templates/agents/student_record_create.html` | `tests/test_lead_workflow.py`, `tests/test_agent_finalize_workflow.py` | Covered |
| `APP-003` | `apps/agents/views.py::applicant_finalize`, `apps/leads/services/conversion.py::_validate_application_selections` | `tests/test_lead_workflow.py` | Covered |
| `APP-004` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `APP-005` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `APP-006` | `apps/leads/models.py::LeadProgramInterest`, `apps/applications/services.py::create_student_application` | `tests/test_student_application_workflow.py`, `tests/test_student_record_conversion_structure.py` | Covered |
| `APP-007` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `APP-008` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |

## Notes

This baseline intentionally starts at capability level. When a requirement is
changed or newly implemented, replace the family row with requirement-level
code paths and named tests. Do not claim exact traceability that has not been
verified.
