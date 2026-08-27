from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class EntityLevelNavigationTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.applicant_nav = (root / "templates/includes/applicant_entity_nav.html").read_text(
            encoding="utf-8"
        )
        self.application_nav = (root / "templates/includes/application_entity_nav.html").read_text(
            encoding="utf-8"
        )
        self.lead_urls = (root / "apps/leads/urls.py").read_text(encoding="utf-8")
        self.agent_urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.application_urls = (root / "apps/applications/urls.py").read_text(encoding="utf-8")
        self.docs = (root / "docs/entity-navigation.md").read_text(encoding="utf-8")

    def test_applicant_has_six_entity_sections(self):
        for label in (
            "Overview",
            "Profile",
            "Programs",
            "Documents",
            "Applications",
            "Messages",
        ):
            self.assertIn(f'{{% trans "{label}" %}}', self.applicant_nav)

    def test_application_has_five_entity_sections(self):
        for label in (
            "Overview",
            "Requirements",
            "Documents",
            "Activity",
            "Messages",
        ):
            self.assertIn(f'{{% trans "{label}" %}}', self.application_nav)

    def test_customer_applicant_routes_are_bookmarkable_get_pages(self):
        self.assertIn('name="lead-profile"', self.lead_urls)
        self.assertIn('name="lead-programs"', self.lead_urls)
        self.assertIn('name="lead-documents"', self.lead_urls)
        self.assertIn('name="lead-applications"', self.lead_urls)
        self.assertIn('name="lead-messages"', self.lead_urls)

    def test_customer_application_routes_exist(self):
        self.assertIn('name="customer-application-detail"', self.application_urls)
        self.assertIn('name="customer-application-requirements"', self.application_urls)
        self.assertIn('name="customer-application-documents"', self.application_urls)
        self.assertIn('name="customer-application-activity"', self.application_urls)
        self.assertIn('name="customer-application-messages"', self.application_urls)

    def test_agent_entity_routes_exist(self):
        self.assertIn('name="agent-applicant-profile"', self.agent_urls)
        self.assertIn('name="agent-applicant-applications"', self.agent_urls)
        self.assertIn('name="agent-application-requirements"', self.agent_urls)
        self.assertIn('name="agent-application-activity"', self.agent_urls)

    def test_post_message_routes_are_separate_from_get_navigation(self):
        self.assertIn("messages/send/", self.lead_urls)
        self.assertIn("messages/send/", self.application_urls)
        self.assertIn("messages/send/", self.agent_urls)

    def test_architecture_is_documented(self):
        self.assertIn("three persistent conceptual levels", self.docs)
        self.assertIn("Applicant entity", self.docs)
        self.assertIn("Application entity", self.docs)
