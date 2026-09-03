from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone, translation

from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.public.services.program_filters import (
    ProgramFilterState,
    apply_program_filters,
)
from apps.public.views import _program_filter_options
from apps.universities.models import (
    AcademicYear,
    Department,
    GeneralField,
    Intake,
    OfferingFee,
    OfferingFeeType,
    Program,
    ProgramInstructionLanguage,
    ProgramLanguage,
    ProgramOffering,
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
        self.university = university
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
        self.department = department
        general_field = GeneralField.objects.create(
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
        self.general_field = general_field
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
        fall = Intake.objects.create(
            university=university,
            academic_year=year,
            name_en="Fall",
            created_by=user,
            updated_by=user,
        )
        spring = Intake.objects.create(
            university=university,
            academic_year=year,
            name_en="Spring",
            created_by=user,
            updated_by=user,
        )

        self.program = Program.objects.create(
            university=university,
            department=department,
            general_field=general_field,
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
        ProgramInstructionLanguage.objects.create(
            program=self.program,
            language=language,
            is_primary=True,
            created_by=user,
            updated_by=user,
        )

        fall_offering = ProgramOffering.objects.create(
            program=self.program,
            academic_year=year,
            intake=fall,
            deadline=timezone.localdate() + timedelta(days=30),
            created_by=user,
            updated_by=user,
        )
        OfferingFee.objects.create(
            offering=fall_offering,
            fee_type=OfferingFeeType.TUITION,
            currency="USD",
            amount=Decimal("8000"),
            basis="annual",
            created_by=user,
            updated_by=user,
        )
        spring_offering = ProgramOffering.objects.create(
            program=self.program,
            academic_year=year,
            intake=spring,
            deadline=timezone.localdate() + timedelta(days=90),
            created_by=user,
            updated_by=user,
        )
        OfferingFee.objects.create(
            offering=spring_offering,
            fee_type=OfferingFeeType.TUITION,
            currency="USD",
            amount=Decimal("12000"),
            basis="annual",
            created_by=user,
            updated_by=user,
        )

        self.year = year
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

    def test_field_filter_uses_canonical_english_slug_identity(self):
        self.general_field.name_fa = "مهندسی"
        self.general_field.slug_fa = "مهندسی"
        self.general_field.save(update_fields=["name_fa", "slug_fa", "updated_at"])

        base = Program.objects.filter(
            is_active=True,
            university__is_active=True,
        )
        canonical = apply_program_filters(
            base,
            ProgramFilterState(field="engineering"),
        )
        localized_slug = apply_program_filters(
            base,
            ProgramFilterState(field="مهندسی"),
        )

        self.assertEqual(canonical.count(), 1)
        self.assertEqual(localized_slug.count(), 0)

    def test_field_filter_does_not_fall_back_to_department(self):
        self.program.general_field = None
        self.program.save(update_fields=["general_field", "updated_at"])

        qs = apply_program_filters(
            Program.objects.all(),
            ProgramFilterState(field="engineering"),
        )

        self.assertEqual(qs.count(), 0)

    def test_field_choice_localizes_label_but_keeps_canonical_slug(self):
        self.general_field.name_fa = "مهندسی"
        self.general_field.slug_fa = "مهندسی"
        self.general_field.save(update_fields=["name_fa", "slug_fa", "updated_at"])

        with translation.override("fa"):
            choices = _program_filter_options()["field_choices"]
            engineering = next(choice for choice in choices if choice.slug_en == "engineering")
            self.assertEqual(engineering.localized_name, "مهندسی")
            self.assertEqual(engineering.slug_en, "engineering")

    def test_field_choices_exclude_general_fields_without_active_university(self):
        self.university.is_active = False
        self.university.save(update_fields=["is_active", "updated_at"])

        choices = _program_filter_options()["field_choices"]

        self.assertNotIn("engineering", [choice.slug_en for choice in choices])

    def test_homepage_does_not_publish_dead_field_links(self):
        self.university.is_active = False
        self.university.save(update_fields=["is_active", "updated_at"])

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "engineering",
            [field.slug_en for field in response.context["study_fields"]],
        )
        self.assertEqual(response.context["program_count"], 0)

    def test_offering_filters_must_match_same_offering(self):
        qs = apply_program_filters(
            Program.objects.all(),
            ProgramFilterState(
                intake=str(self.spring.pk),
                tuition_max="9000",
            ),
        )
        self.assertEqual(qs.count(), 0)

    def test_matching_offering_combination(self):
        qs = apply_program_filters(
            Program.objects.all(),
            ProgramFilterState(
                intake=str(self.fall.pk),
                tuition_max="9000",
                open_only=True,
            ),
        )
        self.assertEqual(qs.count(), 1)

    def test_minimum_tuition_includes_matching_currency(self):
        program = self.program
        ProgramOffering.objects.filter(program=program).delete()

        usd_offering = ProgramOffering.objects.create(
            program=program,
            academic_year=self.year,
            intake=self.fall,
            is_active=True,
        )
        OfferingFee.objects.create(
            offering=usd_offering,
            fee_type=OfferingFeeType.TUITION,
            currency="USD",
            amount=Decimal("15000"),
            basis="annual",
        )
        eur_offering = ProgramOffering.objects.create(
            program=program,
            academic_year=self.year,
            intake=self.spring,
            is_active=True,
        )
        OfferingFee.objects.create(
            offering=eur_offering,
            fee_type=OfferingFeeType.TUITION,
            currency="EUR",
            amount=Decimal("12000"),
            basis="annual",
        )

        result = apply_program_filters(
            Program.objects.filter(pk=program.pk),
            ProgramFilterState(),
        ).get()

        self.assertEqual(result.min_active_tuition, Decimal("12000"))
        self.assertEqual(result.min_active_currency, "EUR")
