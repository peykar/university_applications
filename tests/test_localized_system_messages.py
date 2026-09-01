from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import translation

from apps.agents.models import Agent
from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.leads.models import Lead
from apps.messaging.models import Message, MessageSenderRole, SystemMessageEventType
from apps.messaging.services import send_system_message
from apps.universities.models import DegreeType, Program, University, UniversityType


class LocalizedSystemMessageTests(TestCase):
    def setUp(self):
        self.system_user = get_system_user()
        customer = get_user_model().objects.create_user(
            username="system-message-customer",
            email="system-message-customer@example.com",
        )
        self.agent = Agent.objects.create(
            company_name="Example Agent",
            created_by=self.system_user,
            updated_by=self.system_user,
        )
        self.lead = Lead.objects.create(
            user=customer,
            agent=self.agent,
            first_name="Example",
            last_name="Applicant",
            created_by=customer,
            updated_by=customer,
        )

        country = Country.objects.create(
            iso2="TR",
            iso3="TUR",
            name_en="Türkiye",
            name_fa="ترکیه",
            name_tr="Türkiye",
            name_ar="تركيا",
            slug_en="turkiye",
            slug_fa="ترکیه",
            slug_tr="turkiye",
            slug_ar="تركيا",
            created_by=self.system_user,
            updated_by=self.system_user,
        )
        province = Province.objects.create(
            country=country,
            name_en="Istanbul",
            name_fa="استانبول",
            name_tr="İstanbul",
            name_ar="إسطنبول",
            slug_en="istanbul",
            slug_fa="استانبول",
            slug_tr="istanbul",
            slug_ar="إسطنبول",
            created_by=self.system_user,
            updated_by=self.system_user,
        )
        city = City.objects.create(
            province=province,
            name_en="Istanbul",
            name_fa="استانبول",
            name_tr="İstanbul",
            name_ar="إسطنبول",
            slug_en="istanbul",
            slug_fa="استانبول",
            slug_tr="istanbul",
            slug_ar="إسطنبول",
            created_by=self.system_user,
            updated_by=self.system_user,
        )
        university = University.objects.create(
            city=city,
            university_type=UniversityType.PRIVATE,
            name_en="Example University",
            name_fa="دانشگاه نمونه",
            name_tr="Örnek Üniversitesi",
            name_ar="جامعة نموذجية",
            slug_en="example-university",
            slug_fa="دانشگاه-نمونه",
            slug_tr="ornek-universitesi",
            slug_ar="جامعة-نموذجية",
            created_by=self.system_user,
            updated_by=self.system_user,
        )
        self.program = Program.objects.create(
            university=university,
            degree=DegreeType.BACHELOR,
            name_en="Computer Programming",
            name_fa="برنامه‌نویسی کامپیوتر",
            name_tr="Bilgisayar Programc\u0131l\u0131\u011f\u0131",
            name_ar="برمجة الحاسوب",
            created_by=self.system_user,
            updated_by=self.system_user,
        )

    def test_program_recommendation_is_stored_as_structured_event(self):
        message = send_system_message(
            self.lead,
            event_type=SystemMessageEventType.PROGRAM_RECOMMENDED,
            event_data={
                "program_id": str(self.program.pk),
                "reason": "Good fit",
            },
            performed_by=self.system_user,
        )

        self.assertEqual(message.event_type, SystemMessageEventType.PROGRAM_RECOMMENDED)
        self.assertEqual(message.event_data["program_id"], str(self.program.pk))
        self.assertIn("Computer Programming", message.body)
        self.assertIn("Example University", message.body)

    def test_program_recommendation_renders_in_active_locale(self):
        message = Message(
            sender_role=MessageSenderRole.SYSTEM,
            event_type=SystemMessageEventType.PROGRAM_RECOMMENDED,
            event_data={
                "program_id": str(self.program.pk),
                "reason": "Good fit",
            },
            body="English historical fallback",
        )

        with translation.override("fa"):
            rendered = message.localized_body

        self.assertIn("برنامه‌نویسی کامپیوتر", rendered)
        self.assertIn("دانشگاه نمونه", rendered)
        self.assertIn("Good fit", rendered)
        self.assertNotIn("Computer Programming", rendered)

    def test_document_system_event_localizes_document_type(self):
        message = Message(
            sender_role=MessageSenderRole.SYSTEM,
            event_type=SystemMessageEventType.DOCUMENT_REPLACEMENT_UPLOADED,
            event_data={"document_type": "id_card"},
            body="English historical fallback",
        )

        with translation.override("fa"):
            rendered = message.localized_body

        self.assertIn("کارت شناسایی", rendered)
        self.assertNotEqual(rendered, message.body)

    def test_legacy_and_human_messages_keep_stored_body(self):
        legacy_system = Message(
            sender_role=MessageSenderRole.SYSTEM,
            body="Legacy system message",
        )
        human = Message(
            sender_role=MessageSenderRole.AGENT,
            body="Human-authored text",
        )

        with translation.override("fa"):
            self.assertEqual(legacy_system.localized_body, "Legacy system message")
            self.assertEqual(human.localized_body, "Human-authored text")
