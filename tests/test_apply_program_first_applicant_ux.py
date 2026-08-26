from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.leads.models import Lead


class ApplyProgramFirstApplicantUXTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="apply-ux",
            email="apply@example.com",
            password="password",
            first_name="Ada",
            last_name="Applicant",
        )

    def test_lead_form_fields_are_optional(self):
        from apps.leads.forms import LeadForm

        form = LeadForm({})
        self.assertTrue(form.is_valid(), form.errors)

    def test_lead_model_allows_minimal_profile(self):
        lead = Lead(user=self.user)
        lead.full_clean(exclude=("created_by", "updated_by"))
        self.assertEqual(lead.first_name, "")
        self.assertEqual(lead.last_name, "")
