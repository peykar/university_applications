from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class WorkspaceSidebarTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.customer_base = (root / "templates/customer/base.html").read_text(encoding="utf-8")
        self.agent_base = (root / "templates/agents/base.html").read_text(encoding="utf-8")
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_customer_sidebar_contains_workspace_links(self):
        self.assertIn("'lead-list'", self.customer_base)
        self.assertIn('"My Requests"', self.customer_base)
        self.assertIn("'customer-message-inbox'", self.customer_base)
        self.assertIn('"Messages"', self.customer_base)
        self.assertIn("'contact'", self.customer_base)
        self.assertIn('"Get Help"', self.customer_base)
        self.assertIn("customer_whatsapp_url", self.customer_base)
        self.assertIn('"Message us on WhatsApp"', self.customer_base)
        self.assertNotIn("'dashboard'", self.customer_base)
        self.assertNotIn('"MY TURKDEMY"', self.customer_base)
        self.assertNotIn('"Student workspace"', self.customer_base)

    def test_agent_sidebar_contains_workspace_links(self):
        self.assertIn("'agent-dashboard'", self.agent_base)
        self.assertIn("'agent-applicant-list'", self.agent_base)
        self.assertIn("'agent-application-list'", self.agent_base)
        self.assertIn("'agent-message-inbox'", self.agent_base)

    def test_desktop_layout_is_two_columns(self):
        self.assertIn(
            "grid-template-columns:220px minmax(0,1fr)",
            self.css,
        )

    def test_mobile_sidebar_collapses_to_horizontal_navigation(self):
        self.assertIn("@media(max-width:760px)", self.css)
        self.assertIn(".workspace-sidebar-nav{\n    display:flex;", self.css)
