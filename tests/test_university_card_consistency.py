from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class UniversityCardConsistencyTests(SimpleTestCase):
    def setUp(self):
        base = Path(settings.BASE_DIR)
        self.home = (base / "templates" / "public" / "home.html").read_text(encoding="utf-8")
        self.university_list = (base / "templates" / "public" / "university_list.html").read_text(
            encoding="utf-8"
        )
        self.partial = (
            base / "templates" / "public" / "includes" / "university_card.html"
        ).read_text(encoding="utf-8")

    def test_home_and_university_list_use_same_card_partial(self):
        include = "public/includes/university_card.html"
        self.assertIn(include, self.home)
        self.assertIn(include, self.university_list)

    def test_shared_card_contains_catalogue_metadata(self):
        for value in (
            "active_program_count",
            "is_yok_recognized",
            "is_moe_approved",
            "is_moh_approved",
            "has_erasmus",
            "has_dormitory",
        ):
            self.assertIn(value, self.partial)

    def test_shared_card_is_fully_clickable_without_nested_links(self):
        self.assertIn(
            'class="university-feature-card university-catalogue-card university-card-link"',
            self.partial,
        )
        self.assertIn(
            "href=\"{% url 'university-detail' university.slug_en %}\"",
            self.partial,
        )
        self.assertEqual(self.partial.count("<a"), 1)
        self.assertEqual(self.partial.count("</a>"), 1)
