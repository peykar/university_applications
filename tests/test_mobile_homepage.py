from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class MobileHomepageTests(SimpleTestCase):
    def setUp(self):
        base = Path(settings.BASE_DIR)
        self.home = (base / "templates" / "public" / "home.html").read_text(encoding="utf-8")
        self.css = (base / "static" / "css" / "turkdemy.css").read_text(encoding="utf-8")

    def test_homepage_has_mobile_browse_all_fields_link(self):
        self.assertIn("mobile-browse-all-fields", self.home)

    def test_featured_universities_are_swipeable_on_mobile(self):
        self.assertIn("scroll-snap-type:x proximity;", self.css)
        self.assertIn(".university-feature-card{", self.css)

    def test_mobile_home_caps_visible_field_cards(self):
        self.assertIn(".field-chip:nth-child(n+9)", self.css)

    def test_city_destinations_are_swipeable_on_mobile(self):
        self.assertIn("city-destination-grid", self.home)
        self.assertIn(".city-destination-grid{", self.css)
        self.assertIn("scroll-snap-align:start;", self.css)

    def test_mobile_hero_hides_secondary_selects(self):
        self.assertIn(".hero-filter-row select{", self.css)
        self.assertIn("display:none!important;", self.css)
