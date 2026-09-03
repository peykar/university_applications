from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentProgramRecommendationStructureTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.service = (root / "apps/leads/services/recommendations.py").read_text(encoding="utf-8")
        self.section = (root / "templates/agents/applicant_section.html").read_text(
            encoding="utf-8"
        )
        self.header = (root / "templates/includes/applicant_entity_header.html").read_text(
            encoding="utf-8"
        )
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_agent_can_recommend_program_from_programs_tab(self):
        self.assertIn("def applicant_recommend_program", self.views)
        self.assertIn('name="agent-applicant-program-recommend"', self.urls)
        self.assertIn("Recommend another program", self.section)
        self.assertIn('name="program_id"', self.section)
        self.assertIn('name="suggestion_reason"', self.section)

    def test_recommendation_is_agent_sourced_and_audited_by_service(self):
        self.assertIn("recommend_program(", self.views)
        self.assertIn("@transaction.atomic", self.service)
        self.assertIn("source=LeadProgramInterestSource.AGENT", self.service)
        self.assertIn("suggested_by=agent_user", self.service)
        self.assertIn("LeadActivityType.PROGRAM_SUGGESTED", self.service)
        self.assertIn("send_system_message(", self.service)

    def test_agent_program_reason_uses_bidi_aware_note_treatment(self):
        self.assertIn('class="program-recommendation-reason" dir="auto"', self.section)
        self.assertIn("border-inline-start:2px solid #cad9e5", self.css)

    def test_agent_can_remove_own_recommendation(self):
        self.assertIn("def applicant_remove_recommendation", self.views)
        self.assertIn('name="agent-applicant-program-remove"', self.urls)
        self.assertIn("Remove recommendation", self.section)
        self.assertIn('source="agent"', self.views)

    def test_overview_has_direct_recommendation_entry_point(self):
        self.assertIn("Recommend program", self.header)
        self.assertIn("#recommend-program", self.header)

    def test_agent_workspace_uses_shared_shell_and_compact_overview(self):
        self.assertNotIn(".agent-workspace-page .container{", self.css)
        self.assertNotIn("width:min(1500px,calc(100% - 48px))", self.css)
        self.assertIn(".agent-applicant-overview>#messages", self.css)
        self.assertIn(".applicant-overview-links{", self.css)
