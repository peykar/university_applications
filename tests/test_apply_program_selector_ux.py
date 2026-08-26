from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class ApplyProgramSelectorUXTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates" / "leads" / "apply_program.html").read_text(
            encoding="utf-8"
        )
        self.forms = (root / "apps" / "leads" / "forms.py").read_text(encoding="utf-8")
        self.views = (root / "apps" / "leads" / "views.py").read_text(encoding="utf-8")

    def test_customer_language_does_not_expose_lead_or_offering_labels(self):
        self.assertIn("Who are you applying for?", self.template)
        self.assertIn("When would you like to start?", self.template)
        self.assertNotIn('<h2>{% trans "Choose an applicant" %}</h2>', self.template)

    def test_someone_new_is_inline_and_optional(self):
        self.assertIn('str(_("Someone new"))', self.forms)
        self.assertIn("All of these fields are optional", self.template)
        self.assertIn("data-new-applicant", self.template)

    def test_apply_form_supports_existing_self_and_new_applicant_choices(self):
        self.assertIn('"self_new"', self.forms)
        self.assertIn('"new"', self.forms)
        self.assertIn('f"lead:{lead.pk}"', self.forms)

    def test_apply_flow_creates_new_applicant_inside_transaction(self):
        self.assertIn("with transaction.atomic():", self.views)
        self.assertIn("Lead.objects.create(", self.views)
        self.assertIn("LeadProgramInterest.objects.get_or_create(", self.views)
