from pathlib import Path

from django.test import SimpleTestCase


class SimilarProgramCardClickableTests(SimpleTestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.template = (root / "templates/public/program_detail.html").read_text()

    def test_similar_program_card_is_fully_clickable(self):
        self.assertIn(
            'class="related-program-card related-program-card-link"',
            self.template,
        )
        self.assertIn(
            "href=\"{% url 'program-detail' related.slug_en %}\"",
            self.template,
        )

    def test_similar_program_card_has_no_nested_program_links(self):
        self.assertNotIn(
            "<h3><a href=\"{% url 'program-detail' related.slug_en %}\">",
            self.template,
        )
        self.assertIn(
            '<span class="card-action">{% trans "View program" %}</span>',
            self.template,
        )
