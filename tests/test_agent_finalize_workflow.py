from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentFinalizeWorkflowTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )

    def test_finalize_endpoint_runs_atomic_finalization(self):
        self.assertIn("def applicant_finalize", self.views)
        self.assertIn(
            "student = finalize_lead(lead, performed_by=request.user)",
            self.views,
        )
        self.assertNotIn(
            "convert_lead_to_student(lead, performed_by=request.user)",
            self.views,
        )

    def test_only_responsible_agent_gets_finalize_action(self):
        self.assertIn("lead.assigned_to == request.user", self.template)
        self.assertIn('data-modal-target="finalize-applicant-modal"', self.template)

    def test_finalize_modal_reviews_required_student_data(self):
        for field in ("First name", "Last name", "Nationality", "Gender"):
            self.assertIn(field, self.template)
        self.assertIn("Finalize and create student", self.template)

    def test_finalize_route_exists(self):
        self.assertIn('name="agent-applicant-finalize"', self.urls)

    def test_closed_or_finalized_leads_are_not_finalized_again(self):
        self.assertIn("LeadStatus.CLOSED", self.views)
        self.assertIn("LeadStatus.FINALIZED", self.views)
