from pathlib import Path

from django.test import SimpleTestCase


class ProgramCardClickableTests(SimpleTestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.partial = (root / "templates/public/includes/program_discovery_card.html").read_text()

    def test_whole_program_card_is_single_link(self):
        self.assertIn(
            'class="program-discovery-card program-card-link"',
            self.partial,
        )
        self.assertIn(
            "href=\"{% url 'program-detail' program.slug_en %}\"",
            self.partial,
        )
        self.assertEqual(self.partial.count("<a"), 1)

    def test_card_does_not_contain_nested_links(self):
        self.assertNotIn("<h2><a", self.partial)
        self.assertIn('<span class="program-card-cta">', self.partial)
