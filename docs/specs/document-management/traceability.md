# Document management — traceability

Status: BASELINE STARTED

| Requirement family | Primary implementation area | Verification |
|---|---|---|
| `DOC-*` | See `design.md` | Existing project tests + requirement-specific tests |

This baseline intentionally starts at capability level. When a requirement is
changed or newly implemented, replace the family row with requirement-level
code paths and named tests. Do not claim exact traceability that has not been
verified.

| DOC-001 | `apps/leads/views.py::lead_document_upload`, `lead_document_replace`, customer document templates | `tests/test_lead_workflow.py::LeadWorkflowTests::test_finalized_customer_cannot_upload_historical_lead_document`, `test_finalized_customer_cannot_replace_historical_lead_document`, `tests/test_finalized_customer_lead_mutations.py` | Covered |
