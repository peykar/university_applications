from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "public" / "program_detail.html"
CSS = ROOT / "static" / "css" / "turkdemy.css"


class ProgramDetailConversionLayoutTests(SimpleTestCase):
    def setUp(self):
        self.template = TEMPLATE.read_text(encoding="utf-8")
        self.css = CSS.read_text(encoding="utf-8")

    def test_request_card_remains_the_primary_program_conversion_action(self):
        self.assertIn('class="program-detail-sidebar"', self.template)
        self.assertIn('{% trans "Start a Request" %}', self.template)
        self.assertIn('class="button button-accent"', self.template)

    def test_single_offering_expands_across_the_content_column(self):
        self.assertIn(
            ".offering-card-grid>.offering-card:only-child{grid-column:1/-1}",
            self.css,
        )

    def test_conversion_sidebar_is_prominent_and_moves_before_content_on_tablet(self):
        self.assertIn("grid-template-columns:minmax(0,1fr) 320px", self.css)
        self.assertIn(".program-detail-sidebar{order:-1;position:static}", self.css)

    def test_mobile_request_card_returns_to_a_single_column_action_stack(self):
        self.assertIn(".program-contact-card{display:block;padding:20px}", self.css)
        self.assertIn(".program-contact-card .button{width:100%;margin-top:9px}", self.css)
