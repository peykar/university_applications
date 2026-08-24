from django.test import TestCase, override_settings

from apps.core.urls import absolute_path


class AbsoluteUrlTests(TestCase):
    @override_settings(SITE_URL="https://turkdemy.com")
    def test_absolute_path_uses_site_url(self):
        self.assertEqual(
            absolute_path("/en/dashboard/"),
            "https://turkdemy.com/en/dashboard/",
        )
