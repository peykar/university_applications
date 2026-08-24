from django.template.loader import render_to_string
from django.test import SimpleTestCase
from django.utils import translation


class RTLLayoutTests(SimpleTestCase):
    def test_persian_base_template_is_rtl(self):
        with translation.override("fa"):
            html = render_to_string("base.html")
        self.assertIn('lang="fa"', html)
        self.assertIn('dir="rtl"', html)

    def test_arabic_base_template_is_rtl(self):
        with translation.override("ar"):
            html = render_to_string("base.html")
        self.assertIn('lang="ar"', html)
        self.assertIn('dir="rtl"', html)

    def test_english_base_template_is_ltr(self):
        with translation.override("en"):
            html = render_to_string("base.html")
        self.assertIn('lang="en"', html)
        self.assertIn('dir="ltr"', html)

    def test_turkish_base_template_is_ltr(self):
        with translation.override("tr"):
            html = render_to_string("base.html")
        self.assertIn('lang="tr"', html)
        self.assertIn('dir="ltr"', html)
