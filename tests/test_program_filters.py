from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.public.services.program_filters import (
    ProgramFilterState,
    apply_program_filters,
)
from apps.universities.models import (
    AcademicYear,
    Department,
    Program,
    ProgramLanguage,
    ProgramOffering,
    Semester,
    University,
)


class ProgramFilterTests(TestCase):
    def setUp(self):
        user = get_system_user()

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
            created_by=user,
            updated_by=user,
        )
        province = Province.objects.create(
            country=country,
            name_en="Istanbul",
            name_fa="Istanbul",
            name_tr="İstanbul",
            name_ar="Istanbul",
            slug_en="istanbul",
            slug_fa="istanbul",
            slug_tr="istanbul",
            slug_ar="istanbul",
            created_by=user,
            updated_by=user,
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
            created_by=user,
            updated_by=user,
        )
        university = University.objects.create(
            city=city,
            university_type="private",
            name_en="Example University",
            name_fa="",
            name_tr="",
            name_ar="",
            slug_en="example-university",
            slug_fa="example",
            slug_tr="example",
            slug_ar="example",
            created_by=user,
            updated_by=user,
        )
        department = Department.objects.create(
            university=university,
            name_en="Engineering",
            name_fa="",
            name_tr="",
            name_ar="",
            slug_en="engineering",
            slug_fa="engineering",
            slug_tr="engineering",
            slug_ar="engineering",
            created_by=user,
            updated_by=user,
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
            created_by=user,
            updated_by=user,
        )
        year = AcademicYear.objects.create(
            name_en="2026-2027",
            created_by=user,
            updated_by=user,
        )
        fall = Semester.objects.create(
            name_en="Fall",
            created_by=user,
            updated_by=user,
        )
        spring = Semester.objects.create(
            name_en="Spring",
            created_by=user,
            updated_by=user,
        )

        self.program = Program.objects.create(
            university=university,
            department=department,
            program_language=language,
            degree="bachelor",
            name_en="Computer Engineering",
            name_fa="",
            name_tr="",
            name_ar="",
            slug_en="computer-engineering",
            slug_fa="computer",
            slug_tr="computer",
            slug_ar="computer",
            created_by=user,
            updated_by=user,
        )

        ProgramOffering.objects.create(
            program=self.program,
            academic_year=year,
            semester=fall,
            fee_basis="annual",
            currency="USD",
            tuition=Decimal("8000"),
            deadline=timezone.localdate() + timedelta(days=30),
            created_by=user,
            updated_by=user,
        )
        ProgramOffering.objects.create(
            program=self.program,
            academic_year=year,
            semester=spring,
            fee_basis="annual",
            currency="USD",
            tuition=Decimal("12000"),
            deadline=timezone.localdate() + timedelta(days=90),
            created_by=user,
            updated_by=user,
        )

        self.fall = fall
        self.spring = spring
        self.language = language

    def test_program_level_filters(self):
        qs = apply_program_filters(
            Program.objects.all(),
            ProgramFilterState(
                q="Computer",
                degree="bachelor",
                language=self.language.slug_en,
                field="engineering",
            ),
        )
        self.assertEqual(qs.count(), 1)

    def test_offering_filters_must_match_same_offering(self):
        qs = apply_program_filters(
            Program.objects.all(),
            ProgramFilterState(
                semester=self.spring.slug_en,
                tuition_max="9000",
            ),
        )
        self.assertEqual(qs.count(), 0)

    def test_matching_offering_combination(self):
        qs = apply_program_filters(
            Program.objects.all(),
            ProgramFilterState(
                semester=self.fall.slug_en,
                tuition_max="9000",
                currency="USD",
                open_only=True,
            ),
        )
        self.assertEqual(qs.count(), 1)
