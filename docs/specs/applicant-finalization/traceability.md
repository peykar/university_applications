# Applicant finalization — traceability

Status: BASELINED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `FIN-001` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `FIN-002` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `FIN-003` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `FIN-004` | `apps/leads/services/conversion.py::finalize_lead`, `apps/leads/services/conversion.py::_copy_selected_documents` | `tests/test_lead_workflow.py`, `tests/test_student_record_conversion_structure.py` | Covered |
| `FIN-005` | `apps/leads/services/conversion.py::finalize_lead` | `tests/test_lead_workflow.py::LeadWorkflowTests::test_finalization_records_single_finalized_activity_and_validation_metadata`, `tests/test_atomic_lead_finalization.py` | Covered |
| `FIN-006` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `FIN-007` | `templates/agents/student_record_create.html`, `apps/agents/views.py::applicant_finalize` | `tests/test_agent_finalize_workflow.py`, `tests/test_student_record_conversion_structure.py` | Covered |
| `FIN-008` | `templates/agents/student_record_create.html`, `apps/agents/views.py::applicant_finalize`, `apps/leads/services/conversion.py::_validate_application_selections` | `tests/test_lead_workflow.py`, `tests/test_student_record_conversion_structure.py` | Covered |
| `FIN-009` | `apps/leads/services/conversion.py::finalize_lead`, `apps/applications/services.py::create_student_application` | `tests/test_lead_workflow.py`, `tests/test_student_application_workflow.py` | Covered |
| `FIN-010` | `templates/agents/applicant_detail.html`, `templates/agents/student_record_create.html`, `apps/agents/views.py::applicant_finalize` | `tests/test_agent_finalize_workflow.py`, `tests/test_student_record_conversion_structure.py` | Covered |
| `FIN-011` | `apps/agents/views.py::applicant_finalize`, `templates/agents/student_record_create.html` | `tests/test_student_record_conversion_structure.py` | Covered |
| `FIN-012` | `templates/agents/student_record_create.html`, `apps/leads/services/conversion.py::_copy_selected_documents` | `tests/test_student_record_conversion_structure.py` | Covered |
| `FIN-013` | `apps/leads/services/conversion.py::_copy_selected_documents` | `tests/test_student_record_conversion_structure.py` | Covered |
| `FIN-014` | `apps/leads/services/conversion.py::_copy_selected_documents` | `tests/test_student_record_conversion_structure.py` | Covered |
| `FIN-015` | `apps/agents/views.py::applicant_finalize`, `apps/agents/views.py::_student_conversion_programs` | `tests/test_agent_finalize_workflow.py` | Covered |
| `FIN-016` | `apps/leads/services/conversion.py::finalize_lead` | `tests/test_atomic_lead_finalization.py` | Covered |
| `FIN-017` | `apps/leads/models.py::LeadDocument.converted_student_document`, `apps/leads/services/conversion.py::_copy_selected_documents` | `tests/test_student_record_conversion_structure.py`, `tests/test_student_application_workflow.py` | Covered |

## Notes

This baseline intentionally starts at capability level. When a requirement is
changed or newly implemented, replace the family row with requirement-level
code paths and named tests. Do not claim exact traceability that has not been
verified.
Historical note: `BUG-0006-applicant-modal-actions-not-working` covered the former modal workflow, which CHG-0004 replaced with a dedicated page.
