from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentProgramSuggestionSearchableTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.forms = (root / "apps/agents/forms.py").read_text(encoding="utf-8")
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.js = (root / "static/js/searchable_program_suggestion.js").read_text(encoding="utf-8")

    def test_ajax_search_routes_exist(self):
        self.assertIn('name="agent-program-search"', self.urls)
        self.assertIn('name="agent-program-offering-search"', self.urls)

    def test_program_search_matches_program_and_university(self):
        self.assertIn("def agent_program_search", self.views)
        self.assertIn("name_en__icontains=query", self.views)
        self.assertIn("university__name_en__icontains=query", self.views)

    def test_offering_search_is_program_scoped(self):
        self.assertIn("def agent_program_offering_search", self.views)
        self.assertIn("program_id=program_id", self.views)

    def test_unbound_form_does_not_render_all_options(self):
        self.assertIn("program_field.queryset = Program.objects.none()", self.forms)
        self.assertIn(
            "offering_field.queryset = ProgramOffering.objects.none()",
            self.forms,
        )

    def test_bound_form_validates_posted_model_ids(self):
        self.assertIn("if self.is_bound:", self.forms)
        self.assertIn("Program.objects.filter(is_active=True)", self.forms)
        self.assertIn("ProgramOffering.objects.filter(", self.forms)

    def test_offering_picker_depends_on_selected_program(self):
        self.assertIn('url.searchParams.set("program_id", dependsOn.value)', self.js)
        self.assertIn("setDisabled(!dependsOn.value)", self.js)

    def test_template_loads_picker_script(self):
        self.assertIn("searchable-program-field", self.template)
        self.assertIn("searchable-offering-field", self.template)
        self.assertIn("searchable_program_suggestion.js", self.template)
