from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.agents.models import Agent
from apps.geography.models import City, Country, Province
from apps.leads.models import (
    Lead,
    LeadProgramInterest,
    LeadProgramInterestSource,
    LeadStatus,
)
from apps.leads.services.conversion import finalize_lead
from apps.messaging.models import Message, MessageSenderRole
from apps.messaging.services import get_or_create_conversation
from apps.students.models import Gender, Student
from apps.universities.models import (
    AcademicYear,
    Currency,
    DegreeType,
    FeeBasis,
    Program,
    ProgramLanguage,
    ProgramOffering,
    Semester,
    University,
    UniversityType,
)

User = get_user_model()


class LeadWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="test-password-123",
        )
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="test-password-123",
            is_staff=True,
        )
        self.agent = Agent.objects.create(company_name="Workflow Agent")
        self.agent.users.add(self.staff)

        self.country = Country.objects.create(
            iso2="TR",
            iso3="TUR",
            name_en="Türkiye",
            name_fa="ترکیه",
            name_tr="Türkiye",
            name_ar="تركيا",
            slug_en="turkiye",
            slug_fa="turkiye",
            slug_tr="turkiye",
            slug_ar="turkiye",
            created_by=self.staff,
            updated_by=self.staff,
        )
        province = Province.objects.create(
            country=self.country,
            name_en="Istanbul",
            name_fa="Istanbul",
            name_tr="İstanbul",
            name_ar="Istanbul",
            slug_en="istanbul",
            slug_fa="istanbul",
            slug_tr="istanbul",
            slug_ar="istanbul",
            created_by=self.staff,
            updated_by=self.staff,
        )
        city = City.objects.create(
            province=province,
            name_en="Istanbul",
            name_fa="Istanbul",
            name_tr="İstanbul",
            name_ar="Istanbul",
            slug_en="istanbul",
            slug_fa="istanbul",
            slug_tr="istanbul",
            slug_ar="istanbul",
            created_by=self.staff,
            updated_by=self.staff,
        )
        university = University.objects.create(
            city=city,
            university_type=UniversityType.PRIVATE,
            name_en="Example University",
            name_fa="",
            name_tr="",
            name_ar="",
            slug_en="example-university",
            slug_fa="example",
            slug_tr="example",
            slug_ar="example",
            created_by=self.staff,
            updated_by=self.staff,
        )
        language = ProgramLanguage.objects.create(
            name_en="English",
            name_fa="",
            name_tr="",
            name_ar="",
            slug_en="english",
            slug_fa="english",
            slug_tr="english",
            slug_ar="english",
            created_by=self.staff,
            updated_by=self.staff,
        )
        self.program = Program.objects.create(
            university=university,
            program_language=language,
            degree=DegreeType.BACHELOR,
            name_en="Business Administration",
            name_fa="",
            name_tr="",
            name_ar="",
            slug_en="business-administration",
            slug_fa="business",
            slug_tr="business",
            slug_ar="business",
            created_by=self.staff,
            updated_by=self.staff,
        )
        year = AcademicYear.objects.create(
            name_en="2026-2027",
            created_by=self.staff,
            updated_by=self.staff,
        )
        semester = Semester.objects.create(
            name_en="Fall",
            created_by=self.staff,
            updated_by=self.staff,
        )
        self.offering = ProgramOffering.objects.create(
            program=self.program,
            academic_year=year,
            semester=semester,
            fee_basis=FeeBasis.ANNUAL,
            currency=Currency.USD,
            tuition=Decimal("8000"),
            created_by=self.staff,
            updated_by=self.staff,
        )

    def make_lead(self, first_name="Sara"):
        return Lead.objects.create(
            user=self.user,
            agent=self.agent,
            first_name=first_name,
            last_name="Example",
            nationality=self.country,
            gender=Gender.FEMALE,
            created_by=self.user,
            updated_by=self.user,
        )

    def test_user_can_have_multiple_leads(self):
        self.make_lead("Sara")
        self.make_lead("Amir")
        self.assertEqual(self.user.leads.count(), 2)

    def test_lead_creation_creates_preferences_and_conversation(self):
        lead = self.make_lead()
        self.assertIsNotNone(lead.preferences)
        self.assertIsNotNone(get_or_create_conversation(subject=lead))

    def test_only_logged_in_user_can_apply(self):
        url = reverse("apply-program", kwargs={"slug": self.program.slug_en})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_customer_can_add_program_interest(self):
        lead = self.make_lead()
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("apply-program", kwargs={"slug": self.program.slug_en}),
            {"applicant": f"lead:{lead.pk}", "offering": str(self.offering.pk)},
        )
        self.assertEqual(response.status_code, 302)
        interest = LeadProgramInterest.objects.get()
        self.assertEqual(interest.source, LeadProgramInterestSource.USER)

    def test_customer_cannot_open_other_users_lead(self):
        other = User.objects.create_user(
            username="other",
            password="test-password-123",
        )
        lead = self.make_lead()
        self.client.force_login(other)
        response = self.client.get(reverse("lead-detail", kwargs={"lead_id": lead.pk}))
        self.assertEqual(response.status_code, 404)

    def test_customer_message_is_bound_to_own_lead(self):
        lead = self.make_lead()
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("lead-send-message", kwargs={"lead_id": lead.pk}),
            {"body": "Can you check my options?"},
        )
        self.assertEqual(response.status_code, 302)
        conversation = get_or_create_conversation(subject=lead)
        message = Message.objects.get(conversation=conversation)
        self.assertEqual(message.sender, self.user)
        self.assertEqual(message.sender_role, MessageSenderRole.CUSTOMER)

    def test_finalizing_lead_creates_student_without_application(self):
        lead = self.make_lead()
        LeadProgramInterest.objects.create(
            lead=lead,
            program=self.program,
            program_offering=self.offering,
            source=LeadProgramInterestSource.AGENT,
            suggested_by=self.staff,
            created_by=self.staff,
            updated_by=self.staff,
        )

        student = finalize_lead(lead, performed_by=self.staff)

        self.assertIsInstance(student, Student)
        self.assertEqual(student.user, self.user)
        self.assertEqual(student.applications.count(), 0)

        lead.refresh_from_db()
        self.assertIsNotNone(lead.validated_at)
        self.assertEqual(lead.status, LeadStatus.FINALIZED)
        self.assertEqual(lead.converted_student, student)

    def test_finalization_is_idempotent_after_student_exists(self):
        lead = self.make_lead()
        first_student = finalize_lead(lead, performed_by=self.staff)
        lead.refresh_from_db()

        second_student = finalize_lead(lead, performed_by=self.staff)

        self.assertEqual(second_student.pk, first_student.pk)

    def test_finalization_rejects_invalid_lead(self):
        lead = self.make_lead(first_name="")
        with self.assertRaises(ValidationError):
            finalize_lead(lead, performed_by=self.staff)

        lead.refresh_from_db()
        self.assertNotEqual(lead.status, LeadStatus.FINALIZED)
        self.assertIsNone(lead.converted_student)
