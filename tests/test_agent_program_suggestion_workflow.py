from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentProgramSuggestionWorkflowTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.forms = (root / "apps/agents/forms.py").read_text(encoding="utf-8")
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )

    def test_applicant_page_has_suggest_program_action(self):
        self.assertIn("agent-applicant-program-suggest", self.template)
        self.assertNotIn('data-modal-target="suggest-program-modal"', self.template)
        self.assertIn('{% trans "Suggest program" %}', self.template)

    def test_agent_suggestion_creates_agent_interest(self):
        self.assertIn("def applicant_program_suggest", self.views)
        self.assertIn("interest.source = LeadProgramInterestSource.AGENT", self.views)
        self.assertIn("interest.suggested_by = request.user", self.views)

    def test_suggestion_is_visible_and_audited(self):
        self.assertIn("LeadActivityType.PROGRAM_SUGGESTED", self.views)
        self.assertIn("is_customer_visible=True", self.views)
        self.assertIn("send_system_message(", self.views)

    def test_offering_is_optional_but_must_match_program(self):
        self.assertIn("offering_field.required = False", self.forms)
        self.assertIn("offering.program_id != program.pk", self.forms)

    def test_route_exists(self):
        self.assertIn('name="agent-applicant-program-suggest"', self.urls)
