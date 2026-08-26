from django.test import SimpleTestCase
from django.utils import translation

from apps.core.services.email_branding import (
    branded_email_context,
    localized_email_brand_name,
)


class LocalizedEmailBrandTests(SimpleTestCase):
    def test_persian_brand_name_is_localized(self):
        with translation.override("fa"):
            context = branded_email_context(
                subject="Test",
                text_body="Body",
            )
        self.assertEqual(context["brand_name"], "ترک‌دمی")

    def test_arabic_brand_name_is_localized(self):
        with translation.override("ar"):
            context = branded_email_context(
                subject="Test",
                text_body="Body",
            )
        self.assertEqual(context["brand_name"], "ترك ديمي")

    def test_turkish_brand_name_remains_canonical(self):
        with translation.override("tr"):
            context = branded_email_context(
                subject="Test",
                text_body="Body",
            )
        self.assertEqual(context["brand_name"], "TurkDemy")

    def test_brand_helper_handles_region_variants(self):
        self.assertEqual(localized_email_brand_name("fa-IR"), "ترک‌دمی")
        self.assertEqual(localized_email_brand_name("ar-SA"), "ترك ديمي")
        self.assertEqual(localized_email_brand_name("en-US"), "TurkDemy")
