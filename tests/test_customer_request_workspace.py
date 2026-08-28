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
        self.views = (root / "apps/leads/views.py").read_text(encoding="utf-8")
        self.settings_source = (root / "turkdemy/settings/base.py").read_text(encoding="utf-8")
        self.support_context = (root / "apps/core/context_processors.py").read_text(
            encoding="utf-8"
        )
        self.public_views = (root / "apps/public/views.py").read_text(encoding="utf-8")
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_customer_uses_request_terminology(self):
        self.assertIn('{% trans "My Requests" %}', self.customer_base)
        self.assertIn('{% trans "Request" %}', self.request_header)

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

    def test_request_detail_uses_main_and_context_sidebar_layout(self):
        self.assertIn('class="request-detail-layout"', self.request_detail)
        self.assertIn('class="request-detail-main"', self.request_detail)
        self.assertIn("includes/customer_request_context_sidebar.html", self.request_detail)
        self.assertIn("includes/customer_request_context_sidebar.html", self.request_section)
        self.assertIn("grid-template-columns:minmax(0,1fr) 310px", self.css)

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

    def test_overview_prioritizes_attention_programs_progress_and_messages(self):
        self.assertIn('{% trans "Action required" %}', self.request_detail)
        self.assertIn('{% trans "Applied for" %}', self.request_detail)
        self.assertIn('{% trans "Request progress" %}', self.request_detail)
        self.assertIn('{% trans "Recent messages" %}', self.request_detail)
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

    def test_customer_request_header_uses_customer_friendly_statuses(self):
        self.assertIn('{% trans "Received" %}', self.request_header)
        self.assertIn('{% trans "In progress" %}', self.request_header)
        self.assertIn('{% trans "Completed" %}', self.request_header)
        self.assertIn("{{ lead.get_status_display }}", self.request_header)
