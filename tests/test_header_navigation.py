from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class HeaderNavigationTests(SimpleTestCase):
    def setUp(self):
        base = Path(settings.BASE_DIR)
        self.template = (base / "templates" / "base.html").read_text(encoding="utf-8")
        self.profile = (base / "templates" / "public" / "profile.html").read_text(encoding="utf-8")

    def test_sign_in_methods_is_in_account_menu(self):
        self.assertIn('class="account-menu"', self.template)
        self.assertIn("{% url 'sign-in-methods' %}", self.template)

    def test_logout_has_icon_based_account_action(self):
        self.assertIn('class="account-menu-logout"', self.template)
        self.assertIn("<svg", self.template)

    def test_profile_links_to_sign_in_methods(self):
        self.assertIn("{% url 'sign-in-methods' %}", self.profile)
        self.assertIn("profile-security-card", self.profile)

    def test_language_is_part_of_header_utility_group(self):
        utility_start = self.template.index('class="header-utility"')
        utility_end = self.template.index(
            '<button\n        class="mobile-nav-toggle"', utility_start
        )
        self.assertIn("header-language-form", self.template[utility_start:utility_end])

    def test_my_turkdemy_workspace_menu_is_in_header(self):
        self.assertIn('class="workspace-menu"', self.template)
        self.assertIn('{% trans "My TurkDemy" %}', self.template)
