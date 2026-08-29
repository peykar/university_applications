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

| `CRQ-025` | customer Request header, Overview, context sidebar | `CustomerRequestWorkspaceTests.test_request_ui_uses_one_concept_one_label` | Named test |
| `CRQ-026` | `templates/includes/applicant_entity_header.html` | `CustomerRequestWorkspaceTests.test_customer_request_identity_is_not_repeated` | Named test |
| `CRQ-027` | `templates/leads/lead_detail.html` | `CustomerRequestWorkspaceTests.test_applied_programs_summary_has_no_redundant_labels_or_action` | Named test |
| `CRQ-028` | `templates/leads/lead_detail.html` | `CustomerRequestWorkspaceTests.test_progress_has_single_heading` | Named test |
| `CRQ-029` | `templates/leads/lead_detail.html` | `CustomerRequestWorkspaceTests.test_recent_messages_has_single_heading_and_view_all` | Named test |
| `CRQ-030` | `templates/includes/customer_request_context_sidebar.html` | `CustomerRequestWorkspaceTests.test_uploaded_documents_has_single_heading` | Named test |
| `CRQ-031` | `templates/includes/customer_request_context_sidebar.html` | `CustomerRequestWorkspaceTests.test_program_preferences_has_single_heading_and_edit_action` | Named test |
| `CRQ-032` | `templates/leads/lead_section.html` | `CustomerRequestWorkspaceTests.test_profile_starts_with_meaningful_sections_without_duplicate_identity` | Named test |
| `CRQ-033` | `templates/leads/lead_section.html` | `CustomerRequestWorkspaceTests.test_profile_groups_person_information_semantically` | Named test |
| `CRQ-034` | shared Request header and customer Profile section | `CustomerRequestWorkspaceTests.test_profile_has_one_contextual_customer_edit_action` | Named test |
| `CRQ-035` | `templates/leads/lead_section.html`, persistent context sidebar include | `CustomerRequestWorkspaceTests.test_profile_keeps_request_context_out_of_profile_body` | Named test |
| `CRQ-036` | Profile markup and `static/css/turkdemy.css` | `CustomerRequestWorkspaceTests.test_profile_uses_compact_grouped_panel_contract` | Named test |

| `CRQ-037` | `templates/leads/lead_section.html` | `CustomerRequestWorkspaceTests.test_profile_displays_all_customer_editable_data` | Named test |
| `CRQ-038` | `apps/leads/forms.py`, `templates/leads/lead_section.html` | `CustomerRequestWorkspaceTests.test_profile_and_customer_edit_form_are_field_aligned` | Named test |
| `CRQ-039` | `apps/leads/views.py`, `templates/leads/lead_form.html` | `CustomerRequestWorkspaceTests.test_customer_edit_profile_uses_request_safe_copy_and_actions` | Named test |
| `CRQ-040` | `apps/leads/forms.py`, `apps/leads/views.py`, `templates/leads/lead_form.html` | `CustomerRequestWorkspaceTests.test_customer_edit_profile_excludes_internal_recommendation_control` | Named test |
| `CRQ-041` | `templates/leads/lead_section.html`, `templates/leads/lead_form.html` | `CustomerRequestWorkspaceTests.test_profile_view_and_edit_share_semantic_sections` | Named test |
| `CRQ-042` | `templates/leads/lead_section.html` | `CustomerRequestWorkspaceTests.test_programs_tab_has_single_heading_and_primary_action` | Named test |
| `CRQ-043` | `templates/leads/lead_section.html`, `static/css/turkdemy.css` | `CustomerRequestWorkspaceTests.test_program_card_uses_detail_link_beside_management_controls` | Named test |
| `CRQ-044` | `templates/leads/lead_section.html`, `static/css/turkdemy.css` | `CustomerRequestWorkspaceTests.test_program_cards_keep_source_as_secondary_context` | Named test |
| `CRQ-045` | `templates/leads/lead_section.html` | `CustomerRequestWorkspaceTests.test_program_intake_copy_is_customer_friendly` | Named test |
| `CRQ-046` | `templates/leads/lead_section.html` | `CustomerRequestWorkspaceTests.test_programs_empty_state_does_not_duplicate_browse_action` | Named test |
| `CRQ-047` | `templates/leads/lead_section.html`, `templates/includes/customer_request_context_sidebar.html` | `CustomerRequestWorkspaceTests.test_programs_tab_does_not_duplicate_program_preferences` | Named test |


| `CRQ-048` | `templates/leads/lead_detail.html`, `apps/leads/views.py` | `CustomerRequestWorkspaceTests.test_overview_programs_show_compact_comparison_data` | Named test |
| `CRQ-049` | Request program templates, active-offering prefetch | `CustomerRequestWorkspaceTests.test_program_tuition_is_offering_backed` | Named test |
| `CRQ-050` | `templates/leads/lead_section.html` | `CustomerRequestWorkspaceTests.test_programs_tab_is_detailed_comparison_workspace` | Named test |
| `CRQ-051` | `apps/leads/views.py`, `apps/leads/urls.py`, Programs template | `CustomerRequestWorkspaceTests.test_programs_tab_exposes_intake_management_contract` | Named structural test + runtime validation path |
| `CRQ-052` | `apps/leads/views.py`, `apps/leads/urls.py`, Programs template | `CustomerRequestWorkspaceTests.test_programs_tab_exposes_remove_contract_with_guards` | Named structural test + runtime validation path |
| `CRQ-053` | Programs template/domain unchanged | `CustomerRequestWorkspaceTests.test_program_management_has_no_accept_reject_workflow` | Named test |
| `CRQ-054` | Programs card markup | `CustomerRequestWorkspaceTests.test_program_card_uses_detail_link_beside_management_controls` | Named test |

| `CRQ-055` | `templates/leads/lead_section.html`, intake update view | `CustomerRequestWorkspaceTests.test_program_intake_is_single_auto_submit_dropdown` | Named structural test + existing runtime validation |
| `CRQ-056` | `templates/leads/lead_section.html`, `static/css/turkdemy.css` | `CustomerRequestWorkspaceTests.test_program_removal_is_separate_accessible_trash_action` | Named test |
| `CRQ-057` | `templates/leads/lead_section.html`, `LeadProgramInterest.suggestion_reason` | `CustomerRequestWorkspaceTests.test_agent_suggestion_reason_is_customer_visible_without_internal_notes` | Named test |
| `CRQ-058` | `templates/leads/lead_section.html`, mutation views | `CustomerRequestWorkspaceTests.test_finalized_program_management_is_read_only` | Named structural test + mutation guards |
