from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class NavigationArchitectureTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.base = (root / "templates/base.html").read_text(encoding="utf-8")
        self.customer_nav = (root / "templates/customer/base.html").read_text(encoding="utf-8")
        self.agent_base = (root / "templates/agents/base.html").read_text(encoding="utf-8")
        self.docs = (root / "docs/navigation.md").read_text(encoding="utf-8")
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_header_has_single_my_turkdemy_entry(self):
        self.assertIn('class="workspace-menu"', self.base)
        self.assertIn('{% trans "My TurkDemy" %}', self.base)
        self.assertNotIn('class="workspace-nav"', self.base)

    def test_duplicate_customer_message_header_links_are_removed(self):
        header_start = self.base.index('<header class="site-header">')
        header_end = self.base.index("</header>", header_start)
        header = self.base[header_start:header_end]
        self.assertNotIn(
            '<nav class="workspace-nav"',
            header,
        )

    def test_customer_workspace_navigation_is_contextual(self):
        self.assertIn('{% trans "My Requests" %}', self.customer_nav)
        self.assertIn('{% trans "Messages" %}', self.customer_nav)
        self.assertIn('{% trans "Get Help" %}', self.customer_nav)
        self.assertIn('{% trans "Message us on WhatsApp" %}', self.customer_nav)
        self.assertIn("customer_unread_message_count", self.customer_nav)
        self.assertNotIn('{% trans "Overview" %}', self.customer_nav)
        self.assertNotIn('{% trans "Applicants" %}', self.customer_nav)

    def test_customer_workspace_mobile_actions_do_not_clip(self):
        self.assertIn(
            ".customer-workspace-sidebar .workspace-sidebar-nav,",
            self.css,
        )
        self.assertIn(
            "grid-template-columns:repeat(auto-fit,minmax(72px,1fr));",
            self.css,
        )
        self.assertIn("overflow-wrap:anywhere;", self.css)

    def test_agent_navigation_has_consistent_order(self):
        overview = self.agent_base.index("'agent-dashboard'")
        applicants = self.agent_base.index("'agent-applicant-list'")
        applications = self.agent_base.index("'agent-application-list'")
        messages = self.agent_base.index("'agent-message-inbox'")
        self.assertLess(overview, applicants)
        self.assertLess(applicants, applications)
        self.assertLess(applications, messages)

    def test_footer_uses_current_customer_workspace_terminology(self):
        footer_start = self.base.index('<footer class="site-footer">')
        footer_end = self.base.index("</footer>", footer_start)
        footer = self.base[footer_start:footer_end]
        self.assertIn('{% trans "My TurkDemy" %}', footer)
        self.assertIn("{% url 'lead-list' %}", footer)
        self.assertIn('{% trans "My Requests" %}', footer)
        self.assertIn("{% url 'customer-message-inbox' %}", footer)
        self.assertIn('{% trans "Messages" %}', footer)
        self.assertIn("{% url 'account_login' %}", footer)
        self.assertNotIn('{% trans "Students" %}', footer)
        self.assertNotIn("{% url 'dashboard' %}", footer)
        self.assertNotIn("{% url 'profile' %}", footer)

    def test_navigation_architecture_is_documented(self):
        self.assertIn("workspace-first", self.docs)
        self.assertIn("My TurkDemy workspace", self.docs)
        self.assertIn("Agent workspace", self.docs)
        self.assertIn("Mobile navigation", self.docs)

    def test_customer_workspace_uses_desktop_sidebar(self):
        self.assertIn('class="workspace-sidebar customer-workspace-sidebar"', self.customer_nav)
        self.assertIn('class="workspace-main"', self.customer_nav)

    def test_agent_workspace_uses_desktop_sidebar(self):
        self.assertIn('class="workspace-sidebar agent-workspace-sidebar"', self.agent_base)
        self.assertNotIn('class="agent-tabs"', self.agent_base)

    def test_agent_workspace_expands_into_released_context_space(self):
        self.assertIn(
            ".agent-workspace-page .page-shell{",
            self.css,
        )
        self.assertIn("max-width:1496px;", self.css)
        self.assertIn(
            "margin-inline-start:max(16px,calc((100vw - 1160px)/2));",
            self.css,
        )
        self.assertIn("margin-inline-end:16px;", self.css)

    def test_agent_workspace_uses_shared_workspace_visual_system(self):
        self.assertIn(
            'class="section-heading workspace-page-head agent-workspace-head"',
            self.agent_base,
        )
        self.assertNotIn('{% trans "AGENT WORKSPACE" %}', self.agent_base)
        self.assertNotIn(
            ".agent-workspace-page .container{",
            self.css,
        )
        self.assertNotIn(
            ".agent-workspace-page .workspace-shell{",
            self.css,
        )
        self.assertIn(
            ".agent-workspace-sidebar .workspace-sidebar-nav{",
            self.css,
        )
        self.assertIn("same outer visual system", self.docs)
