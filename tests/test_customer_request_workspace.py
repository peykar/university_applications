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
