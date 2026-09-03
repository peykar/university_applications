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

    def test_mobile_university_context_is_compact_and_expandable(self):
        self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))", self.css)
        self.assertIn("data-university-description-toggle", self.template)
        self.assertIn('{% trans "Read more" %}', self.template)
        self.assertIn('{% trans "Show less" %}', self.template)
        self.assertIn(
            ".university-media-item,.university-media-featured{display:block;width:100%;height:auto;aspect-ratio:16/9",
            self.css,
        )

    def test_mobile_similar_programs_use_horizontal_snap_scrolling(self):
        self.assertIn(".related-program-grid{display:flex;grid-template-columns:none", self.css)
        self.assertIn("scroll-snap-type:x mandatory", self.css)
        self.assertIn(".related-program-card{flex:0 0 min(84vw,280px)", self.css)

    def test_mobile_hero_has_safe_reading_space_and_avoids_duplicate_summaries(self):
        self.assertIn(".program-detail-hero{padding:88px 26px 48px}", self.css)
        self.assertIn(".program-university-mini-card{display:none}", self.css)
        self.assertIn(".program-summary-grid{display:none}", self.css)

    def test_mobile_request_copy_is_shorter(self):
        self.assertIn(
            '{% trans "Start a Request and let TurkDemy help with the next steps." %}',
            self.template,
        )
        self.assertNotIn(
            (
                "Start a Request and TurkDemy can help you with requirements, tuition, "
                "intake selection and the next steps."
            ),
            self.template,
        )
