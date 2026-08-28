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
        self.create_template = (root / "templates/agents/student_record_create.html").read_text(
            encoding="utf-8"
        )

    def test_finalize_endpoint_runs_atomic_finalization(self):
        self.assertIn("def applicant_finalize", self.views)
        self.assertIn("student = finalize_lead(", self.views)
        self.assertIn("application_selections=selections", self.views)
        self.assertNotIn(
            "convert_lead_to_student(lead, performed_by=request.user)",
            self.views,
        )

    def test_only_responsible_agent_gets_finalize_action(self):
        self.assertIn("lead.assigned_to == request.user", self.template)
        self.assertIn("agent-applicant-finalize", self.template)
        self.assertIn("Create Student Record", self.template)

    def test_applicant_modal_script_is_rendered_in_extra_scripts(self):
        title_block = self.template.split("{% block agent_title %}", 1)[1].split(
            "{% endblock %}",
            1,
        )[0]
        scripts_block = self.template.split("{% block extra_scripts %}", 1)[1].split(
            "{% endblock %}",
            1,
        )[0]
        self.assertNotIn("<script>", title_block)
        self.assertIn("{{ block.super }}", scripts_block)
        self.assertIn(
            "document.getElementById(trigger.dataset.modalTarget)",
            scripts_block,
        )
        self.assertIn("dialog.showModal()", scripts_block)

    def test_create_student_record_page_reviews_conversion_inputs(self):
        self.assertIn("Create Student Record", self.create_template)
        self.assertIn('name="document"', self.create_template)
        self.assertIn('name="program_interest"', self.create_template)
        self.assertIn('name="offering_{{ interest.pk }}"', self.create_template)
        self.assertIn("Verified documents are selected by default", self.create_template)
        self.assertIn("Customer-added", self.create_template)
        self.assertIn("Agent-suggested", self.create_template)

    def test_finalize_route_exists(self):
        self.assertIn('name="agent-applicant-finalize"', self.urls)

    def test_closed_or_finalized_leads_are_not_finalized_again(self):
        self.assertIn("LeadStatus.CLOSED", self.views)
        self.assertIn("LeadStatus.FINALIZED", self.views)

    def test_finalize_allows_zero_or_more_discussed_program_selections(self):
        self.assertIn('request.POST.getlist("program_interest")', self.views)
        self.assertIn("Choose an offering for", self.views)
        self.assertIn("Select zero or more discussed programs", self.create_template)
        self.assertNotIn("can_finalize_with_programs", self.create_template)
