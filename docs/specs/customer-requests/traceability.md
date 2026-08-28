# Customer requests — traceability

Status: IMPLEMENTED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `CRQ-001` | `templates/customer/base.html`, `templates/leads/lead_list.html`, shared customer request header/nav | `CustomerRequestWorkspaceTests.test_customer_uses_request_terminology` | Named test |
| `CRQ-002` | `templates/customer/base.html` | `CustomerRequestWorkspaceTests.test_sidebar_contains_only_customer_menu_items` | Named test |
| `CRQ-003` | `turkdemy/settings/base.py`, `apps/core/context_processors.py`, `.env.example` | `CustomerRequestWorkspaceTests.test_support_links_are_configuration_driven` | Named test |
| `CRQ-004` | `turkdemy/settings/base.py`, `apps/public/views.py`, `templates/leads/lead_list.html` | `CustomerRequestWorkspaceTests.test_requests_are_customer_home_with_find_programs_action` | Named test |
| `CRQ-005` | `templates/leads/lead_list.html` | `CustomerRequestWorkspaceTests.test_request_card_shows_identity_and_contact` | Named test |
| `CRQ-006` | `apps/leads/views.py`, `templates/leads/lead_list.html` | `CustomerRequestWorkspaceTests.test_request_card_lists_all_programs_and_marks_agent_suggestions` | Named test |
| `CRQ-007` | `apps/leads/views.py`, `templates/leads/lead_list.html` | `CustomerRequestWorkspaceTests.test_request_attention_combines_messages_and_document_replacement` | Named test |
| `CRQ-008` | `templates/leads/lead_list.html` | `CustomerRequestWorkspaceTests.test_entire_request_card_is_clickable` | Named test |
| `CRQ-009` | `templates/leads/lead_list.html`, `static/css/turkdemy.css` | `CustomerRequestWorkspaceTests.test_request_actions_have_responsive_rtl_contract` | Named test |
| `CRQ-010` | presentation-only implementation; existing Lead/Student/Application services | existing SDD/domain tests plus `CustomerRequestWorkspaceTests.test_customer_abstraction_does_not_add_request_model` | Named + regression |
