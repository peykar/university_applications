from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class CustomerRequestWorkspaceTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.customer_base = (root / "templates/customer/base.html").read_text(encoding="utf-8")
        self.request_list = (root / "templates/leads/lead_list.html").read_text(encoding="utf-8")
        self.request_header = (root / "templates/includes/applicant_entity_header.html").read_text(
            encoding="utf-8"
        )
        self.request_nav = (root / "templates/includes/applicant_entity_nav.html").read_text(
            encoding="utf-8"
        )
        self.request_detail = (root / "templates/leads/lead_detail.html").read_text(
            encoding="utf-8"
        )
        self.request_section = (root / "templates/leads/lead_section.html").read_text(
            encoding="utf-8"
        )
        self.request_context_sidebar = (
            root / "templates/includes/customer_request_context_sidebar.html"
        ).read_text(encoding="utf-8")
        self.request_form = (root / "templates/leads/lead_form.html").read_text(encoding="utf-8")
        self.forms = (root / "apps/leads/forms.py").read_text(encoding="utf-8")
        self.views = (root / "apps/leads/views.py").read_text(encoding="utf-8")
        self.settings_source = (root / "turkdemy/settings/base.py").read_text(encoding="utf-8")
        self.support_context = (root / "apps/core/context_processors.py").read_text(
            encoding="utf-8"
        )
        self.public_views = (root / "apps/public/views.py").read_text(encoding="utf-8")
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_customer_uses_request_terminology(self):
        self.assertIn('{% trans "My Requests" %}', self.customer_base)
        self.assertIn('{% trans "My Requests" %}', self.request_header)
        self.assertIn('class="request-back-link"', self.request_header)
        self.assertNotIn('<p class="eyebrow">{% trans "Request" %}</p>', self.request_header)

        # Customer links in the shared entity nav intentionally omit the
        # agent-only Applications tab.
        self.assertIn("{% url 'lead-detail' lead.pk %}", self.request_nav)
        self.assertIn("{% url 'lead-profile' lead.pk %}", self.request_nav)
        self.assertIn("{% url 'lead-programs' lead.pk %}", self.request_nav)
        self.assertIn("{% url 'lead-documents' lead.pk %}", self.request_nav)
        self.assertIn("{% url 'lead-messages' lead.pk %}", self.request_nav)
        self.assertNotIn("{% url 'customer-application-list'", self.request_nav)

    def test_sidebar_contains_only_customer_menu_items(self):
        self.assertIn('{% trans "My Requests" %}', self.customer_base)
        self.assertIn('{% trans "Messages" %}', self.customer_base)
        self.assertIn('{% trans "Get Help" %}', self.customer_base)
        self.assertIn('{% trans "Message us on WhatsApp" %}', self.customer_base)
        self.assertNotIn("workspace-sidebar-head", self.customer_base)
        self.assertNotIn('{% trans "MY TURKDEMY" %}', self.customer_base)
        self.assertNotIn('{% trans "Student workspace" %}', self.customer_base)
        self.assertNotIn("workspace-sidebar-section", self.customer_base)

    def test_support_links_are_configuration_driven(self):
        self.assertIn(
            'WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "").strip()',
            self.settings_source,
        )
        self.assertIn('getattr(settings, "WHATSAPP_NUMBER", "")', self.support_context)
        self.assertIn('f"https://wa.me/{digits}" if digits else ""', self.support_context)
        self.assertIn("{% if customer_whatsapp_url %}", self.customer_base)
        self.assertIn("{% url 'contact' %}", self.customer_base)

    def test_requests_are_customer_home_with_find_programs_action(self):
        self.assertIn('LOGIN_REDIRECT_URL = "lead-list"', self.settings_source)
        self.assertIn('return redirect("lead-list")', self.public_views)
        self.assertIn('{% trans "Find Programs" %}', self.request_list)
        self.assertIn("{% url 'program-list' %}", self.request_list)

    def test_request_card_shows_identity_and_contact(self):
        self.assertIn("<h2>{{ lead }}</h2>", self.request_list)
        self.assertIn("{{ lead.email }}", self.request_list)
        self.assertIn("{{ lead.cell }}", self.request_list)

    def test_request_card_lists_all_programs_and_marks_agent_suggestions(self):
        self.assertIn("programs = list(lead.program_interests.all())", self.views)
        self.assertIn('{% trans "Applied for" %}', self.request_list)
        self.assertIn('interest.source == "agent"', self.request_list)
        self.assertIn('{% trans "Suggested by your agent" %}', self.request_list)

    def test_request_card_renders_program_and_university_names(self):
        self.assertIn("{{ interest.program.name_en }}", self.request_list)
        self.assertIn("{{ interest.program.university.name_en }}", self.request_list)
        self.assertNotIn("{{ interest.program.name }}", self.request_list)
        self.assertNotIn("{{ interest.program.university.name }}", self.request_list)

    def test_request_card_has_no_hover_visual_effect(self):
        self.assertIn(".request-card:hover{color:inherit;text-decoration:none}", self.css)
        self.assertNotIn(".request-card:hover{border-color:", self.css)
        self.assertNotIn(".request-card:hover{transform:", self.css)
        self.assertNotIn(".request-card:hover{box-shadow:", self.css)

    def test_request_attention_combines_messages_and_document_replacement(self):
        self.assertIn("unread_count_for_conversation(", self.views)
        self.assertIn("LeadDocumentReviewStatus.REPLACEMENT_REQUESTED", self.views)
        self.assertIn(
            '"needs_attention": bool(unread_message_count or needs_document_action)',
            self.views,
        )
        self.assertIn('{% trans "Action required" %}', self.request_list)
        self.assertIn('{% trans "A document needs replacement" %}', self.request_list)

    def test_entire_request_card_is_clickable(self):
        self.assertIn('<a class="request-card', self.request_list)
        self.assertIn("href=\"{% url 'lead-detail' lead.id %}\"", self.request_list)
        self.assertNotIn('<article class="request-card', self.request_list)

    def test_request_actions_have_responsive_rtl_contract(self):
        self.assertIn(".request-page-heading", self.css)
        self.assertIn('[dir="rtl"] .request-attention', self.css)
        self.assertIn("@media(max-width:700px)", self.css)

    def test_customer_abstraction_does_not_add_request_model(self):
        models = (Path(settings.BASE_DIR) / "apps/leads/models.py").read_text(encoding="utf-8")
        self.assertNotIn("class Request(", models)

    def test_request_detail_uses_parallel_main_and_context_sidebar_layout(self):
        self.assertIn('class="request-detail-layout"', self.request_detail)
        self.assertIn('class="request-detail-main"', self.request_detail)
        self.assertIn("includes/customer_request_context_sidebar.html", self.request_detail)
        self.assertIn("includes/customer_request_context_sidebar.html", self.request_section)
        self.assertIn("grid-template-columns:minmax(0,1fr) 310px", self.css)

        detail_layout = self.request_detail.split('<div class="request-detail-layout">', 1)[1]
        main = detail_layout.split('<main class="request-detail-main">', 1)[1]
        main_before_close = main.split("</main>", 1)[0]
        after_main = main.split("</main>", 1)[1]
        self.assertIn("includes/applicant_entity_header.html", main_before_close)
        self.assertNotIn("includes/customer_request_context_sidebar.html", main_before_close)
        self.assertIn("includes/customer_request_context_sidebar.html", after_main)

    def test_request_navigation_stays_between_header_and_page_content(self):
        self.assertIn("includes/applicant_entity_nav.html", self.request_header)
        self.assertIn('{% trans "Overview" %}', self.request_nav)
        self.assertIn('{% trans "Profile" %}', self.request_nav)
        self.assertIn('{% trans "Programs" %}', self.request_nav)
        self.assertIn('{% trans "Documents" %}', self.request_nav)
        self.assertIn('{% trans "Messages" %}', self.request_nav)

    def test_context_sidebar_contains_documents_and_program_preferences(self):
        self.assertIn('{% trans "Uploaded documents" %}', self.request_context_sidebar)
        self.assertIn(
            'document.review_status == "replacement_requested"',
            self.request_context_sidebar,
        )
        self.assertIn("{% url 'lead-documents' lead.pk %}", self.request_context_sidebar)
        self.assertIn('{% trans "Program preferences" %}', self.request_context_sidebar)
        self.assertIn("{% url 'lead-preferences' lead.pk %}", self.request_context_sidebar)
        self.assertIn("preferred_degrees", self.request_context_sidebar)
        self.assertIn("preferred_languages", self.request_context_sidebar)
        self.assertIn("preferences.tuition_min", self.request_context_sidebar)

    def test_overview_prioritizes_attention_programs_progress_and_messages_in_one_flow(self):
        attention = self.request_detail.index('{% trans "Action required" %}')
        programs = self.request_detail.index('<h2>{% trans "Programs" %}</h2>')
        progress = self.request_detail.index('{% trans "Progress" %}')
        messages = self.request_detail.index('{% trans "Recent messages" %}')
        self.assertLess(attention, programs)
        self.assertLess(programs, progress)
        self.assertLess(progress, messages)
        self.assertIn(".request-overview-grid{display:grid;grid-template-columns:1fr;", self.css)
        self.assertIn('"attention_documents": attention_documents', self.views)
        self.assertIn('"recent_messages": message_qs.order_by("-created_at")[:3]', self.views)

    def test_overview_does_not_mark_unread_messages_read(self):
        overview = self.views[
            self.views.index("def lead_detail") : self.views.index("def lead_profile")
        ]
        self.assertIn("_lead_entity_context(request=request, lead=lead)", overview)
        self.assertNotIn("mark_read=True", overview)
        messages_view = self.views[
            self.views.index("def lead_messages") : self.views.index("def lead_document_upload")
        ]
        self.assertIn("mark_read=True", messages_view)

    def test_request_overview_is_compact_and_uses_explicit_attention_and_document_statuses(self):
        self.assertNotIn('{% trans "You have something to review" %}', self.request_detail)
        self.assertIn("You have {{ counter }} unread message", self.request_detail)
        self.assertIn("{{ document_name }} needs to be replaced", self.request_detail)
        self.assertIn('{% trans "Approved" %}', self.request_context_sidebar)
        self.assertIn('{% trans "Under review" %}', self.request_context_sidebar)
        self.assertIn('{% trans "Needs replacement" %}', self.request_context_sidebar)
        self.assertIn(
            ".request-detail-main>.lead-panel,.request-overview-grid>.lead-panel"
            "{padding:18px;margin-bottom:14px}",
            self.css,
        )
        self.assertIn(
            ".request-overview-grid{display:grid;grid-template-columns:1fr;gap:14px}",
            self.css,
        )

    def test_customer_header_is_status_only(self):
        self.assertNotIn('class="request-next-step"', self.request_header)
        self.assertNotIn('{% trans "Next step" %}', self.request_header)
        self.assertNotIn('{% trans "Program recommendations" %}', self.request_header)
        self.assertIn(
            "agent_context and lead.needs_program_recommendation",
            self.request_header,
        )

    def test_unread_messages_are_attention_not_required_action(self):
        self.assertIn('"has_required_action": bool(attention_documents)', self.views)
        self.assertIn('{% trans "Needs your attention" %}', self.request_detail)
        self.assertIn("{% if has_required_action %}", self.request_detail)

    def test_progress_uses_customer_specific_subject_labels(self):
        self.assertIn('activity.description.partition(":")[2]', self.views)
        self.assertIn("%(document)s uploaded", self.views)
        self.assertIn("%(program)s added to your request", self.views)
        self.assertIn("Your advisor suggested %(program)s", self.views)

    def test_recent_messages_use_customer_safe_advisor_identity(self):
        self.assertIn('message.sender_role == "agent"', self.request_detail)
        self.assertIn('{% trans "Your advisor" %}', self.request_detail)
        recent = self.request_detail.split('class="request-message-preview-meta"', 1)[1]
        self.assertNotIn("message.sender.username }}{% else %}TurkDemy", recent)

    def test_request_ui_uses_one_concept_one_label(self):
        self.assertNotIn('{% trans "Applied for" %}', self.request_detail)
        self.assertNotIn('{% trans "Request progress" %}', self.request_detail)
        self.assertNotIn('{% trans "Files" %}', self.request_context_sidebar)
        self.assertNotIn('{% trans "Study" %}', self.request_context_sidebar)

    def test_customer_request_identity_is_not_repeated(self):
        customer = self.request_header.split("{% else %}", 1)[1]
        self.assertIn('class="request-back-link"', customer)
        self.assertIn('← {% trans "My Requests" %}', customer)
        self.assertNotIn("<span>{{ lead }}</span>", customer)
        self.assertNotIn('{% trans "Request" %}', customer)

    def test_applied_programs_summary_has_no_redundant_labels_or_action(self):
        self.assertIn('<h2>{% trans "Programs" %}</h2>', self.request_detail)
        self.assertNotIn('{% trans "Applied programs" %}', self.request_detail)
        self.assertNotIn('{% trans "View programs" %}', self.request_detail)
        self.assertIn("{% url 'program-detail' interest.program.slug_en %}", self.request_detail)

    def test_progress_has_single_heading(self):
        self.assertIn('<h2>{% trans "Progress" %}</h2>', self.request_detail)
        self.assertNotIn('{% trans "Request progress" %}', self.request_detail)

    def test_recent_messages_has_single_heading_and_view_all(self):
        self.assertIn('<h2>{% trans "Recent messages" %}</h2>', self.request_detail)
        self.assertIn('{% trans "View all" %} →', self.request_detail)
        self.assertNotIn('{% trans "View messages" %}', self.request_detail)

    def test_uploaded_documents_has_single_heading(self):
        self.assertIn('<h2>{% trans "Uploaded documents" %}</h2>', self.request_context_sidebar)
        self.assertNotIn('{% trans "Files" %}', self.request_context_sidebar)

    def test_program_preferences_has_single_heading_and_edit_action(self):
        self.assertIn('<h2>{% trans "Program preferences" %}</h2>', self.request_context_sidebar)
        self.assertNotIn('{% trans "Study" %}', self.request_context_sidebar)
        self.assertEqual(self.request_context_sidebar.count('{% trans "Edit" %} →'), 1)
        self.assertNotIn('{% trans "Edit preferences" %}', self.request_context_sidebar)

    def test_profile_starts_with_meaningful_sections_without_duplicate_identity(self):
        profile = self.request_section.split('{% if entity_tab == "profile" %}', 1)[1].split(
            '{% elif entity_tab == "programs" %}', 1
        )[0]
        self.assertNotIn('{% trans "Request profile" %}', profile)
        self.assertNotIn('<p class="eyebrow">{% trans "Profile" %}</p>', profile)
        self.assertIn('<h2>{% trans "Personal information" %}</h2>', profile)
        self.assertNotIn("<h1>{{ lead }}</h1>", profile)

    def test_profile_groups_person_information_semantically(self):
        profile = self.request_section.split('{% if entity_tab == "profile" %}', 1)[1].split(
            '{% elif entity_tab == "programs" %}', 1
        )[0]
        for heading in (
            "Personal information",
            "Identity & nationality",
            "Residence",
            "Passport",
            "Education & language",
        ):
            self.assertIn(f'{{% trans "{heading}" %}}', profile)
        for field in (
            "Email",
            "Phone",
            "Birthdate",
            "Gender",
            "Nationality",
            "Country of birth",
            "Country of residence",
            "City of residence",
            "Address",
            "Passport number",
            "Issuing authority",
            "Date of issue",
            "Date of expiry",
            "English test type",
            "English test score",
            "High school GPA",
            "High school GPA scale",
            "Educational background",
        ):
            self.assertIn(f'{{% trans "{field}" %}}', profile)

    def test_profile_has_one_contextual_customer_edit_action(self):
        profile = self.request_section.split('{% if entity_tab == "profile" %}', 1)[1].split(
            '{% elif entity_tab == "programs" %}', 1
        )[0]
        self.assertEqual(profile.count('{% trans "Edit profile" %}'), 1)
        self.assertIn("{% url 'lead-edit' lead.pk %}", profile)
        self.assertIn('{% if lead.status != "finalized" %}', profile)
        self.assertNotIn('{% trans "Edit profile" %}', self.request_header)
        self.assertIn('{% trans "Edit applicant" %}', self.request_header)

    def test_profile_keeps_request_context_out_of_profile_body(self):
        profile = self.request_section.split('{% if entity_tab == "profile" %}', 1)[1].split(
            '{% elif entity_tab == "programs" %}', 1
        )[0]
        self.assertNotIn('{% trans "Program preferences" %}', profile)
        self.assertNotIn('{% trans "Uploaded documents" %}', profile)
        self.assertIn("includes/customer_request_context_sidebar.html", self.request_section)

    def test_profile_uses_compact_grouped_panel_contract(self):
        profile = self.request_section.split('{% if entity_tab == "profile" %}', 1)[1].split(
            '{% elif entity_tab == "programs" %}', 1
        )[0]
        self.assertEqual(
            profile.count('class="lead-panel entity-section request-profile-panel"'),
            1,
        )
        self.assertIn('class="request-profile-section', profile)
        self.assertIn(".request-profile-section{", self.css)
        self.assertIn(".request-profile-section-heading{", self.css)
        self.assertIn(".request-profile-facts-single{", self.css)
        self.assertIn("grid-template-columns:1fr;", self.css)

    def test_profile_displays_all_customer_editable_data(self):
        profile = self.request_section.split('{% if entity_tab == "profile" %}', 1)[1].split(
            '{% elif entity_tab == "programs" %}', 1
        )[0]
        for field in (
            "Email",
            "Phone",
            "Birthdate",
            "Gender",
            "Nationality",
            "Country of birth",
            "Country of residence",
            "City of residence",
            "Address",
            "Passport number",
            "Issuing authority",
            "Date of issue",
            "Date of expiry",
            "English test type",
            "English test score",
            "High school GPA",
            "High school GPA scale",
            "Educational background",
        ):
            self.assertIn(f'{{% trans "{field}" %}}', profile)
        self.assertNotIn('{% trans "First name" %}', profile)
        self.assertIn("{{ lead.first_name }}", self.request_header)
        self.assertIn(
            "{% if lead.middle_name %} {{ lead.middle_name }}{% endif %}",
            self.request_header,
        )
        self.assertIn(
            "{% if lead.last_name %} {{ lead.last_name }}{% endif %}",
            self.request_header,
        )
        self.assertIn('|default:"—"', profile)
        self.assertIn('|default_if_none:"—"', profile)

    def test_profile_and_customer_edit_form_are_field_aligned(self):
        edit_form = self.forms.split("class CustomerLeadEditForm", 1)[1].split(
            "class LeadPreferenceForm", 1
        )[0]
        self.assertIn('if field_name != "needs_program_recommendation"', edit_form)
        self.assertIn("class Meta(LeadForm.Meta)", edit_form)
        profile_sources = (
            "lead.country_of_birth",
            "lead.country_of_residence",
            "lead.city_of_residence",
            "lead.address",
            "lead.passport_issuing_authority",
            "lead.passport_date_of_issue",
            "lead.passport_date_of_expiry",
            # Choice fields should use their human-readable display value.
            "lead.get_english_test_type_display",
            "lead.english_language_test_score",
            "lead.high_school_gpa",
            "lead.high_school_gpa_scale",
            "lead.educational_background",
        )
        for profile_source in profile_sources:
            self.assertIn(profile_source, self.request_section)

    def test_customer_edit_profile_uses_request_safe_copy_and_actions(self):
        edit_view = self.views.split("def lead_edit", 1)[1].split("def lead_preferences", 1)[0]
        self.assertIn('"title": "Edit profile"', edit_view)
        self.assertIn('"Profile updated."', edit_view)
        self.assertIn('{% trans "Save changes" %}', self.request_form)
        self.assertIn("{% url 'lead-profile' lead.pk %}", self.request_form)
        self.assertNotIn(
            (
                '{% trans "This information is provisional until TurkDemy staff '
                'validate and finalize it." %}'
            ),
            self.request_form,
        )
        self.assertIn(
            '{% if not lead %}<p class="eyebrow">{% trans "Request profile" %}</p>{% endif %}',
            self.request_form,
        )

    def test_customer_edit_profile_excludes_internal_recommendation_control(self):
        edit_view = self.views.split("def lead_edit", 1)[1].split("def lead_preferences", 1)[0]
        self.assertIn("CustomerLeadEditForm", edit_view)
        self.assertIn('field_name != "needs_program_recommendation"', self.forms)
        self.assertIn(
            (
                '{% if not lead %}<div class="applicant-form-field '
                'applicant-form-field-wide applicant-recommendation-field">'
            ),
            self.request_form,
        )

    def test_profile_view_and_edit_share_semantic_sections(self):
        profile = self.request_section.split('{% if entity_tab == "profile" %}', 1)[1].split(
            '{% elif entity_tab == "programs" %}', 1
        )[0]
        for heading in (
            "Personal information",
            "Passport",
            "Education & language",
        ):
            self.assertIn(f'{{% trans "{heading}" %}}', profile)
            self.assertIn(f'{{% trans "{heading}" %}}', self.request_form)
        self.assertIn('{% trans "Identity & nationality" %}', profile)
        self.assertIn('{% trans "Residence" %}', profile)
        self.assertIn('{% trans "Residence" %}', self.request_form)

    def test_programs_tab_has_single_heading_and_primary_action(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertEqual(programs.count('{% trans "Programs" %}'), 1)
        self.assertNotIn('<p class="eyebrow">{% trans "Programs" %}</p>', programs)
        self.assertEqual(programs.count('{% trans "Find programs" %}'), 1)
        self.assertIn("{% url 'program-list' %}", programs)

    def test_program_card_uses_detail_link_beside_management_controls(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertIn('<article class="lead-interest-card request-program-card">', programs)
        detail_link = (
            '<a class="request-program-detail-link" '
            "href=\"{% url 'program-detail' interest.program.slug_en %}\">"
        )
        self.assertIn(detail_link, programs)
        self.assertIn("<h3>{{ interest.program.name_en }}</h3>", programs)
        self.assertIn('class="request-program-university"', programs)
        self.assertIn('class="request-program-meta"', programs)
        self.assertIn('class="request-program-management"', programs)
        self.assertIn(".request-program-detail-link{", self.css)

    def test_program_cards_keep_source_as_secondary_context(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        name_index = programs.index("{{ interest.program.name_en }}")
        source_index = programs.index('{% trans "Suggested by your advisor" %}')
        self.assertLess(name_index, source_index)
        self.assertIn('{% trans "Suggested by your advisor" %}', programs)
        self.assertIn('{% trans "Added by you" %}', programs)
        self.assertIn("request-program-source", programs)

    def test_agent_suggestion_reason_is_separate_bidi_aware_note(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertIn('<p class="request-program-suggestion-reason" dir="auto">', programs)
        self.assertIn("{{ interest.suggestion_reason }}", programs)
        self.assertIn(".request-program-source{display:grid;gap:5px;", self.css)
        self.assertIn("unicode-bidi:plaintext", self.css)
        self.assertNotIn(
            '<span class="interest-source interest-source-agent">'
            '{% trans "Suggested by your advisor" %}</span>'
            "{{ interest.suggestion_reason }}",
            programs,
        )

    def test_program_intake_copy_is_customer_friendly(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertIn("interest.program_offering.semester.name_en", programs)
        self.assertIn("interest.program_offering.academic_year.name_en", programs)
        self.assertIn('{% trans "Select intake" %}', programs)
        self.assertNotIn('{% trans "Any intake / decide later" %}', programs)

    def test_programs_empty_state_does_not_duplicate_browse_action(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertIn(
            '{% trans "No programs have been added to this request yet." %}',
            programs,
        )
        self.assertNotIn('{% trans "Browse programs" %}', programs)
        self.assertEqual(programs.count("{% url 'program-list' %}"), 1)

    def test_programs_tab_does_not_duplicate_program_preferences(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertNotIn('{% trans "Program preferences" %}', programs)
        self.assertIn(
            '<h2>{% trans "Program preferences" %}</h2>',
            self.request_context_sidebar,
        )

    def test_customer_request_header_uses_customer_friendly_statuses(self):
        self.assertIn('{% trans "Received" %}', self.request_header)
        self.assertIn('{% trans "In progress" %}', self.request_header)
        self.assertIn('{% trans "Completed" %}', self.request_header)
        self.assertIn("{{ lead.get_status_display }}", self.request_header)

    def test_overview_programs_show_compact_comparison_data(self):
        self.assertIn("interest.program.get_degree_display", self.request_detail)
        self.assertIn("interest.program.program_language.name_en", self.request_detail)
        self.assertIn("currency_amount:interest.program_offering.currency", self.request_detail)
        self.assertIn('{% trans "From" %}', self.request_detail)

    def test_program_tuition_is_offering_backed(self):
        self.assertIn('Prefetch("program__offerings"', self.views)
        self.assertIn("ProgramOffering.objects.filter(is_active=True)", self.views)
        self.assertIn("interest.program_offering.tuition_discounted", self.request_section)
        self.assertNotIn("interest.program.tuition", self.request_section)

    def test_programs_tab_is_detailed_comparison_workspace(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        for token in (
            "program.get_degree_display",
            "program.program_language.name_en",
            "program.duration",
            "request-program-tuition",
            '{% trans "Intake" %}',
        ):
            self.assertIn(token, programs)

    def test_programs_tab_exposes_intake_management_contract(self):
        urls = (Path(settings.BASE_DIR) / "apps/leads/urls.py").read_text(encoding="utf-8")
        self.assertIn('name="lead-program-intake-update"', urls)
        self.assertIn("def lead_program_intake_update(", self.views)
        self.assertIn("program=interest.program", self.views)
        self.assertIn("is_active=True", self.views)
        self.assertIn("lead.status == LeadStatus.FINALIZED", self.views)
        self.assertIn(
            "{% url 'lead-program-intake-update' lead.pk interest.pk %}",
            self.request_section,
        )

    def test_program_intake_is_single_auto_submit_dropdown(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertIn('name="program_offering" onchange="this.form.submit()"', programs)
        self.assertIn('{% trans "Select intake" %}', programs)
        self.assertIn("interest.program_offering_id == offering.pk", programs)
        self.assertNotIn('{% trans "Change intake" %}', programs)
        self.assertNotIn('class="button button-secondary small-button" type="submit"', programs)

    def test_program_removal_is_separate_accessible_trash_action(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        intake_form = programs.split('class="request-program-intake-form"', 1)[1].split(
            "</form>", 1
        )[0]
        self.assertNotIn("lead-program-remove", intake_form)
        self.assertIn('class="request-program-remove-form"', programs)
        self.assertIn(
            "confirm('{% trans \"Remove this program from your Request?\" %}')",
            programs,
        )
        self.assertIn(
            "aria-label=\"{% trans 'Remove program' %}\"",
            programs,
        )
        self.assertIn('<svg viewBox="0 0 24 24"', programs)
        self.assertIn('class="button-reset request-program-remove"', programs)
        self.assertIn('<span>{% trans "Remove" %}</span>', programs)
        self.assertIn("border:0;background:transparent;color:#7c8994", self.css)

    def test_program_cards_fill_programs_column(self):
        program_list_css = (
            ".request-program-list{display:grid;"
            "grid-template-columns:minmax(0,1fr);gap:8px;width:100%}"
        )
        self.assertIn(program_list_css, self.css)
        self.assertIn(
            ".request-program-card{position:relative;width:100%;box-sizing:border-box}",
            self.css,
        )

    def test_program_card_actions_have_distinct_spacing(self):
        self.assertIn(
            ".request-program-detail-link{padding-inline-end:0}",
            self.css,
        )
        self.assertIn(
            ".request-program-footer-actions{display:flex;"
            "justify-content:flex-end;margin-top:10px}",
            self.css,
        )

    def test_program_card_actions_are_borderless_and_separated_by_role(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertIn('class="request-program-chevron" aria-hidden="true"', programs)
        self.assertIn("M5 12h12m-5-5 5 5-5 5", programs)
        self.assertNotIn('request-program-chevron" aria-hidden="true">→', programs)
        self.assertIn("border:0;background:transparent;color:#587b98", self.css)
        self.assertIn('class="request-program-footer-actions"', programs)
        self.assertIn('<span>{% trans "Remove" %}</span>', programs)
        self.assertIn(".request-program-remove-form{position:static;margin:0}", self.css)
        self.assertIn("border:0;background:transparent;color:#7c8994", self.css)

    def test_agent_suggestion_reason_is_customer_visible_without_internal_notes(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertIn("{% if interest.suggestion_reason %}", programs)
        self.assertIn("{{ interest.suggestion_reason }}", programs)
        self.assertNotIn("{{ interest.notes }}", programs)

    def test_finalized_program_management_is_read_only(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertIn('{% if lead.status != "finalized" %}', programs)
        self.assertIn('class="request-program-intake-readonly"', programs)
        self.assertIn('{% trans "Not selected" %}', programs)

    def test_programs_tab_exposes_remove_contract_with_guards(self):
        urls = (Path(settings.BASE_DIR) / "apps/leads/urls.py").read_text(encoding="utf-8")
        self.assertIn('name="lead-program-remove"', urls)
        self.assertIn("def lead_program_remove(", self.views)
        self.assertIn("pk=interest_id, lead=lead", self.views)
        self.assertIn(
            "{% url 'lead-program-remove' lead.pk interest.pk %}",
            self.request_section,
        )

    def test_program_management_has_no_accept_reject_workflow(self):
        programs = self.request_section.split('{% elif entity_tab == "programs" %}', 1)[1].split(
            '{% elif entity_tab == "documents" %}', 1
        )[0]
        self.assertNotIn("Accept", programs)
        self.assertNotIn("Reject", programs)
        self.assertNotIn("Add to my request", programs)

    def test_documents_workspace_has_single_page_identity(self):
        documents = self.request_section.split('{% elif entity_tab == "documents" %}', 1)[1].split(
            '{% elif entity_tab == "applications" %}', 1
        )[0]
        self.assertIn('<h2>{% trans "Documents" %}</h2>', documents)
        self.assertNotIn('{% trans "Request documents" %}', documents)
        self.assertNotIn('<p class="eyebrow">{% trans "Documents" %}</p>', documents)

    def test_documents_workspace_uses_document_type_not_filename(self):
        documents = self.request_section.split('{% elif entity_tab == "documents" %}', 1)[1].split(
            '{% elif entity_tab == "applications" %}', 1
        )[0]
        self.assertIn("{{ document.get_document_type_display }}", documents)
        self.assertNotIn("{{ document.name }}", documents)

    def test_document_cards_show_customer_status_and_open_affordance(self):
        self.assertIn('{% trans "Approved" %}', self.request_section)
        self.assertIn('{% trans "Under review" %}', self.request_section)
        self.assertIn('{% trans "Needs replacement" %}', self.request_section)
        self.assertIn('class="request-document-open"', self.request_section)
        self.assertIn(".request-document-open svg", self.css)

    def test_replacement_document_card_exposes_reason_and_replace_action(self):
        self.assertIn("{{ document.review_note }}", self.request_section)
        self.assertIn('{% trans "Replace document" %}', self.request_section)
        self.assertIn("request-document-replace", self.request_section)

    def test_documents_workspace_has_one_contextual_upload_action(self):
        documents = self.request_section.split('{% elif entity_tab == "documents" %}', 1)[1].split(
            '{% elif entity_tab == "applications" %}', 1
        )[0]
        self.assertIn('{% if documents and lead.status != "finalized" %}', documents)
        self.assertIn("empty-state request-document-empty", documents)
        self.assertNotIn('{% trans "Add another document" %}', documents)

    def test_documents_tab_has_no_request_context_sidebar(self):
        self.assertIn(
            '{% if entity_tab != "documents" %}',
            self.request_section,
        )
        self.assertIn(
            '{% include "includes/customer_request_context_sidebar.html" %}',
            self.request_section,
        )
        self.assertIn(
            "request-detail-layout-documents",
            self.request_section,
        )
        self.assertIn(
            ".request-detail-layout-documents{grid-template-columns:minmax(0,1fr)}",
            self.css,
        )
        self.assertIn('{% trans "Program preferences" %}', self.request_context_sidebar)

    def test_document_type_is_a_direct_file_link(self):
        documents = self.request_section.split('{% elif entity_tab == "documents" %}', 1)[1].split(
            '{% elif entity_tab == "applications" %}', 1
        )[0]
        self.assertIn('class="request-document-title-link"', documents)
        self.assertIn('href="{{ document.file.url }}"', documents)
        self.assertIn("{{ document.get_document_type_display }}</a>", documents)
        self.assertIn(".request-document-title-link{", self.css)

    def test_documents_mobile_layout_is_compact_and_upload_stays_in_heading(self):
        self.assertIn(
            ".request-documents-heading{display:flex;align-items:center;",
            self.css,
        )
        self.assertIn(".request-documents-heading .button{", self.css)
        self.assertIn("min-height:82px", self.css)
        self.assertIn("inset-block-start:50%", self.css)
        self.assertIn("transform:translateY(-50%)", self.css)

    def test_customer_request_mobile_tabs_fit_without_clipping(self):
        self.assertIn(
            "customer-request-entity-nav",
            self.request_nav,
        )
        self.assertIn(
            ".customer-request-entity-nav{display:grid;"
            "grid-template-columns:repeat(5,minmax(0,1fr));",
            self.css,
        )
        self.assertIn(
            "font-size:clamp(.64rem,2.7vw,.72rem)",
            self.css,
        )
