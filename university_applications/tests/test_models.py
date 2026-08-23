from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from university_applications.models import (
    AcademicYear, ApplicationDocument, City, Country, DegreeType, Department,
    FeeBasis, Gender, Program, ProgramLanguage, ProgramOffering, Province,
    Semester, Student, StudentDocument, ThesisType, University, UniversityType,
)
from university_applications.services import create_application_from_offering


class ModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("admin", "pass")
        self.country = Country.objects.create(name_en="Türkiye", slug_en="turkiye", iso2="TR", iso3="TUR")
        self.province = Province.objects.create(country=self.country, name_en="Istanbul", slug_en="istanbul")
        self.city = City.objects.create(province=self.province, name_en="Istanbul", slug_en="istanbul")
        self.university = University.objects.create(
            name_en="Example University", slug_en="example-university", city=self.city,
            university_type=UniversityType.PRIVATE,
        )
        self.language = ProgramLanguage.objects.create(name_en="English", slug_en="english", code="en")
        self.year = AcademicYear.objects.create(name_en="2026-2027")
        self.semester = Semester.objects.create(name_en="Fall")

    def test_thesis_type_rejected_for_bachelor(self):
        program = Program(
            university=self.university, name_en="Engineering", slug_en="engineering",
            degree=DegreeType.BACHELOR, thesis_type=ThesisType.THESIS,
            program_language=self.language,
        )
        with self.assertRaises(ValidationError):
            program.full_clean()

    def test_department_must_belong_to_same_university(self):
        other = University.objects.create(
            name_en="Other University", slug_en="other-university", city=self.city,
            university_type=UniversityType.PRIVATE,
        )
        department = Department.objects.create(university=other, name_en="Engineering", slug_en="engineering")
        program = Program(
            university=self.university, department=department, name_en="Engineering",
            slug_en="engineering", degree=DegreeType.BACHELOR,
            program_language=self.language,
        )
        with self.assertRaises(ValidationError):
            program.full_clean()

    def test_application_snapshots_offering_prices(self):
        program = Program.objects.create(
            university=self.university, name_en="Engineering", slug_en="engineering",
            degree=DegreeType.BACHELOR, program_language=self.language,
        )
        offering = ProgramOffering.objects.create(
            program=program, academic_year=self.year, semester=self.semester,
            fee_basis=FeeBasis.ANNUAL, currency="USD", tuition=Decimal("5000"),
            tuition_discounted=Decimal("4500"), deposit=Decimal("500"),
        )
        student = Student.objects.create(
            first_name="Test", last_name="Student", nationality=self.country, gender=Gender.OTHER,
        )
        application = create_application_from_offering(student=student, offering=offering)
        self.assertEqual(application.tuition, Decimal("4500"))
        self.assertEqual(application.deposit, Decimal("500"))

    def test_application_document_must_belong_to_student(self):
        program = Program.objects.create(
            university=self.university, name_en="Engineering", slug_en="engineering",
            degree=DegreeType.BACHELOR, program_language=self.language,
        )
        offering = ProgramOffering.objects.create(
            program=program, academic_year=self.year, semester=self.semester,
            fee_basis=FeeBasis.ANNUAL, currency="USD", tuition=Decimal("5000"),
        )
        student1 = Student.objects.create(first_name="A", last_name="One", nationality=self.country, gender=Gender.OTHER)
        student2 = Student.objects.create(first_name="B", last_name="Two", nationality=self.country, gender=Gender.OTHER)
        application = create_application_from_offering(student=student1, offering=offering)
        doc = StudentDocument(student=student2, document_type="other", file="dummy.pdf")
        doc.save()
        link = ApplicationDocument(application=application, student_document=doc)
        with self.assertRaises(ValidationError):
            link.full_clean()


class PhoneNumberTests(TestCase):
    def test_user_cell_is_normalized_to_e164(self):
        user = get_user_model().objects.create_user(
            username="phone-user",
            password="pass",
            cell="+31 6 1234 5678",
        )
        self.assertEqual(user.cell, "+31612345678")
        self.assertFalse(user.is_cell_verified)

    def test_invalid_user_cell_is_rejected(self):
        user = get_user_model()(username="bad-phone", cell="+31 123")
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_student_cell_is_normalized(self):
        country = Country.objects.create(
            name_en="Türkiye", slug_en="turkiye-phone", iso2="TP", iso3="TPH"
        )
        student = Student(
            first_name="Phone",
            last_name="Student",
            nationality=country,
            gender=Gender.OTHER,
            cell="+90 532 123 45 67",
        )
        student.full_clean()
        self.assertEqual(student.cell, "+905321234567")


class AgentOrganizationTests(TestCase):
    def test_agent_can_have_multiple_users(self):
        user1 = User.objects.create_user(
            username="agent-user-1",
            password="testpass123",
        )
        user2 = User.objects.create_user(
            username="agent-user-2",
            password="testpass123",
        )

        agent = Agent.objects.create(
            company_name="Example Education Agency",
        )
        agent.users.add(user1, user2)

        self.assertEqual(agent.company_name, "Example Education Agency")
        self.assertEqual(agent.users.count(), 2)
        self.assertIn(agent, user1.agents.all())
        self.assertIn(agent, user2.agents.all())

    def test_agent_logo_is_optional(self):
        agent = Agent.objects.create(
            company_name="No Logo Agency",
        )
        self.assertFalse(bool(agent.logo))


class AgentContactAndDocumentTests(TestCase):
    def test_agent_contact_details(self):
        agent = Agent.objects.create(
            company_name="Example Education Agency",
            email="hello@example.com",
            website="https://example.com",
            cell="+31 6 1234 5678",
            landline="+31 20 123 4567",
        )

        self.assertEqual(agent.email, "hello@example.com")
        self.assertEqual(agent.website, "https://example.com")
        self.assertEqual(agent.cell, "+31612345678")
        self.assertEqual(agent.landline, "+31201234567")

    def test_agent_document_metadata(self):
        agent = Agent.objects.create(
            company_name="Documented Agency",
        )

        document = AgentDocument(
            agent=agent,
            name="Agency Agreement",
            description="Signed agency agreement for internal staff reference.",
        )

        self.assertEqual(document.name, "Agency Agreement")
        self.assertEqual(
            document.description,
            "Signed agency agreement for internal staff reference.",
        )
        self.assertEqual(document.agent, agent)
