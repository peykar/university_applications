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
| `CRQ-011` | `templates/leads/lead_list.html` | `CustomerRequestWorkspaceTests.test_request_card_renders_program_and_university_names` | Named test |
| `CRQ-012` | `static/css/turkdemy.css` | `CustomerRequestWorkspaceTests.test_request_card_has_no_hover_visual_effect` | Named test |
| `CRQ-013` | `templates/leads/lead_detail.html`, `templates/leads/lead_section.html`, `static/css/turkdemy.css` | `CustomerRequestWorkspaceTests.test_request_detail_uses_parallel_main_and_context_sidebar_layout` | Named test |
| `CRQ-014` | shared Request header/nav | `CustomerRequestWorkspaceTests.test_request_navigation_stays_between_header_and_page_content` | Named test |
| `CRQ-015` | `templates/includes/customer_request_context_sidebar.html` | `CustomerRequestWorkspaceTests.test_context_sidebar_contains_documents_and_program_preferences` | Named test |
| `CRQ-016` | `apps/leads/views.py`, Request context sidebar | `CustomerRequestWorkspaceTests.test_context_sidebar_contains_documents_and_program_preferences` | Named test |
| `CRQ-017` | `apps/leads/views.py`, `templates/leads/lead_detail.html` | `CustomerRequestWorkspaceTests.test_overview_prioritizes_attention_programs_progress_and_messages_in_one_flow` | Named test |
| `CRQ-018` | `apps/leads/views.py` | `CustomerRequestWorkspaceTests.test_overview_does_not_mark_unread_messages_read` | Named test |
| `CRQ-019` | `templates/includes/applicant_entity_header.html` | `CustomerRequestWorkspaceTests.test_customer_request_header_uses_customer_friendly_statuses` | Named test |
| `CRQ-020` | Request Overview/context templates and `static/css/turkdemy.css` | `CustomerRequestWorkspaceTests.test_request_overview_is_compact_and_uses_explicit_attention_and_document_statuses` | Named test |

| `CRQ-021` | Request entity header and Overview semantics | `CustomerRequestWorkspaceTests.test_customer_header_is_status_only` | Named test |
| `CRQ-022` | Request Overview attention panel | `CustomerRequestWorkspaceTests.test_unread_messages_are_attention_not_required_action` | Named test |
| `CRQ-023` | customer activity presentation in `apps/leads/views.py` | `CustomerRequestWorkspaceTests.test_progress_uses_customer_specific_subject_labels` | Named test |
| `CRQ-024` | Request recent-message preview | `CustomerRequestWorkspaceTests.test_recent_messages_use_customer_safe_advisor_identity` | Named test |
