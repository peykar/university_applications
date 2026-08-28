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

| APL-005 | `apps/leads/views.py::lead_edit`, customer applicant header | `tests/test_lead_workflow.py::LeadWorkflowTests::test_finalized_customer_cannot_edit_historical_lead`, `tests/test_finalized_customer_lead_mutations.py` | Covered |

| APL-007 | `apps/agents/forms.py::AgentLeadEditForm`, `apps/agents/views.py::applicant_internal_notes`, `templates/agents/applicant_detail.html` | `tests/test_agent_internal_notes_activity.py`, `tests/test_agent_edit_upload_workflow.py` | Covered |

APL-007 follow-up: `BUG-0004-internal-notes-hidden-on-agent-overview` verifies the note card is rendered outside the hidden legacy aside.
