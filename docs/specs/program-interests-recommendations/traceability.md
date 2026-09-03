# Program interests and recommendations — traceability

Status: BASELINED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `PRG-001` | `apps/leads/views.py`, `LeadProgramInterest` | Existing lead/customer workflow tests | Baseline |
| `PRG-002` | `apps/leads/services/recommendations.py`; `apps/agents/views.py` | `LeadWorkflowTests.test_recommend_program_service_creates_interest_activity_and_message`; Agent recommendation structural tests | Named |
| `PRG-003` | `apps/leads/services/recommendations.py` | `LeadWorkflowTests.test_recommend_program_service_creates_interest_activity_and_message`; `LeadWorkflowTests.test_recommend_program_service_updates_existing_agent_recommendation` | Named |
| `PRG-004` | `apps/leads/services/recommendations.py` | `LeadWorkflowTests.test_recommend_program_service_creates_interest_activity_and_message`; `AgentProgramRecommendationStructureTests.test_recommendation_is_agent_sourced_and_audited_by_service` | Named |
| `PRG-005` | `apps/leads/services/recommendations.py` | `LeadWorkflowTests.test_recommend_program_service_preserves_user_interest` | Named |
| `PRG-006` | `apps/leads/services/recommendations.py` | `LeadWorkflowTests.test_recommend_program_service_creates_interest_activity_and_message`; structural service-boundary test | Named |
| `PRG-007` | `apps/agents/views.py::applicant_remove_recommendation` | `AgentProgramRecommendationStructureTests.test_agent_can_remove_own_recommendation` | Named structural |
| `PRG-008` | `LeadProgramInterest`; Lead→Student conversion services | Existing lead/finalization workflow tests | Baseline |
| `PRG-009` | Agent Program lookup plus service defensive validation | Agent recommendation structural tests; service validation path | Partial named |
| `PRG-010` | `templates/leads/lead_detail.html`; `apps/leads/views.py`; `templates/agents/applicant_activity.html` | `CustomerRequestWorkspaceTests.test_agent_suggestion_reason_is_visible_on_request_overview_program_card`; `CustomerRequestWorkspaceTests.test_program_suggestion_activity_exposes_reason_in_customer_progress`; `AgentActivityPageTests.test_program_suggestion_activity_shows_recommendation_reason` | Named |

## REF-0002

`REF-0002` is behavior-preserving. It resolves the former G-001 recommendation
service/atomicity code gap without adding new product requirements. The HTTP view
retains authorization/scoping and user-facing response behavior; the service is
now the canonical owner of recommendation domain mutations and creation side
effects.

## CHG-0011

`CHG-0011` makes the optional Agent recommendation reason visible on the customer
Request Overview program summary and alongside PROGRAM_SUGGESTED activity
presentations. It reuses existing structured recommendation/activity data and
does not change recommendation creation, authorization, or transaction semantics.
