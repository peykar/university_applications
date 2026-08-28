# Communication Log — Traceability

| Requirement | Implementation | Verification |
| --- | --- | --- |
| COM-001..005 | `CommunicationLog`, enums, `create_communication` | `tests/test_operations_sdd.py` |
| COM-006 | separate `apps.operations` persistence | architecture/source review |
| COM-007 | `CommunicationLogRevision`, `edit_communication` | `test_communication_edits_create_revision_first` |
| COM-008..009 | generic subject fields, parent aggregation service | `test_parent_aggregation_includes_applications_for_lead` |
| COM-010 | `communication_create_todo` | route/source review |
| COM-011 | private Lead activity + Application composed activity | `test_activity_integration_is_private_for_applicant` |
| COM-012 | global/contextual routes and navigation | `test_global_and_contextual_routes_exist` |
| COM-013 | separate models with shared presentation-ready subject scope | architecture review |
