# Applicant management — traceability

Status: BASELINE STARTED

| Requirement family | Primary implementation area | Verification |
|---|---|---|
| `APL-*` | See `design.md` | Existing project tests + requirement-specific tests |

This baseline intentionally starts at capability level. When a requirement is
changed or newly implemented, replace the family row with requirement-level
code paths and named tests. Do not claim exact traceability that has not been
verified.


| Requirement | Implementation | Tests | Status |
|---|---|---|---|
| APL-003/004/005 | `apps/agents/views.py::applicant_edit`, `templates/agents/applicant_edit.html` | `tests/test_agent_edit_upload_workflow.py` | Covered |
