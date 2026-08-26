from django.test import SimpleTestCase
from django.urls import reverse

from apps.core.urls import absolute_path, absolute_url


class CoreUrlHelpersAndRoutesTests(SimpleTestCase):
    def test_existing_absolute_url_helpers_remain_available(self):
        self.assertTrue(callable(absolute_path))
        self.assertTrue(callable(absolute_url))

    def test_email_preview_gallery_route_is_available(self):
        self.assertEqual(
            reverse("email-preview-gallery"),
            "/admin-tools/email-previews/",
        )
