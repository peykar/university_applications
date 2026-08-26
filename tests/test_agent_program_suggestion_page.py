from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentProgramSuggestionPageTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.detail = (root / "templates/agents/applicant_detail.html").read_text(encoding="utf-8")
        self.page = (root / "templates/agents/program_suggest.html").read_text(encoding="utf-8")

    def test_programs_card_links_to_page_not_modal(self):
        self.assertIn("agent-applicant-program-suggest", self.detail)
        self.assertNotIn('data-modal-target="suggest-program-modal"', self.detail)
        self.assertNotIn('<dialog id="suggest-program-modal"', self.detail)

    def test_program_suggestion_view_supports_get_and_post(self):
        self.assertIn("def applicant_program_suggest", self.views)
        self.assertIn('if request.method == "POST":', self.views)
        self.assertIn('"agents/program_suggest.html"', self.views)

    def test_page_keeps_searchable_dependent_fields(self):
        self.assertIn("searchable-program-field", self.page)
        self.assertIn("searchable-offering-field", self.page)
        self.assertIn("searchable_program_suggestion.js", self.page)

    def test_page_has_applicant_context_and_navigation(self):
        self.assertIn("Back to applicant", self.page)
        self.assertIn("Responsible", self.page)
        self.assertIn("Status", self.page)
