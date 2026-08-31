from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.geography.models import City, Country, Province
from apps.universities.models import (
    AcademicYear,
    FeeBasis,
    Intake,
    OfferingFee,
    OfferingFeeType,
    Program,
    ProgramLanguage,
    ProgramOffering,
    University,
)


class CatalogueV3Tests(TestCase):
    def setUp(self):
        country = Country.objects.create(
            name_en="Türkiye", slug_en="turkiye", iso2="TR", iso3="TUR"
        )
        province = Province.objects.create(country=country, name_en="Istanbul", slug_en="istanbul")
        city = City.objects.create(province=province, name_en="Istanbul", slug_en="istanbul")
        self.university = University.objects.create(
            name_en="Example University",
            slug_en="example-university",
            city=city,
            university_type="private",
        )
        self.year = AcademicYear.objects.create(name_en="2026-2027")
        self.intake = Intake.objects.create(
            university=self.university, academic_year=self.year, name_en="Academic Intake"
        )
        self.program = Program.objects.create(
            university=self.university, name_en="Medicine", slug_en="medicine", degree="bachelor"
        )
        self.offering = ProgramOffering.objects.create(
            program=self.program,
            academic_year=self.year,
            intake=self.intake,
        )
        OfferingFee.objects.create(
            offering=self.offering,
            fee_type=OfferingFeeType.TUITION,
            currency="USD",
            amount=Decimal("44000"),
            basis=FeeBasis.ANNUAL,
        )

    def test_intake_is_canonical(self):
        self.assertEqual(self.offering.intake.name_en, "Academic Intake")
        self.assertEqual(self.offering.intake_name, "Academic Intake")

    def test_intake_date_order_is_validated(self):
        intake = Intake(
            university=self.university,
            academic_year=self.year,
            name_en="Fall",
            application_open="2026-09-01",
            application_deadline="2026-08-01",
        )
        with self.assertRaises(ValidationError):
            intake.full_clean()

    def test_language_specific_preparatory_fees_are_independent(self):
        english = ProgramLanguage.objects.create(name_en="English", slug_en="english")
        turkish = ProgramLanguage.objects.create(name_en="Turkish", slug_en="turkish")
        OfferingFee.objects.create(
            offering=self.offering,
            fee_type=OfferingFeeType.PREPARATORY,
            language=english,
            currency="USD",
            amount=Decimal("17000"),
            basis=FeeBasis.ANNUAL,
        )
        OfferingFee.objects.create(
            offering=self.offering,
            fee_type=OfferingFeeType.PREPARATORY,
            language=turkish,
            currency="USD",
            amount=Decimal("1390"),
            basis=FeeBasis.ANNUAL,
        )
        self.assertEqual(self.offering.fees.filter(fee_type="preparatory").count(), 2)

    def test_fee_basis_supports_real_world_shapes(self):
        self.assertIn("semester", FeeBasis.values)
        self.assertIn("per_credit", FeeBasis.values)
        self.assertIn("one_time", FeeBasis.values)


class CatalogueV3AdminPresentationTests(TestCase):
    def setUp(self):
        country = Country.objects.create(
            name_en="Türkiye", slug_en="turkiye-admin", iso2="TR", iso3="TUR"
        )
        province = Province.objects.create(
            country=country, name_en="Istanbul", slug_en="istanbul-admin"
        )
        city = City.objects.create(province=province, name_en="Istanbul", slug_en="istanbul-admin")
        self.university = University.objects.create(
            name_en="Admin Example University",
            slug_en="admin-example-university",
            city=city,
            university_type="private",
        )
        self.year = AcademicYear.objects.create(name_en="2026-2027")
        self.intake = Intake.objects.create(
            university=self.university,
            academic_year=self.year,
            name_en="Academic Intake",
        )
        self.program = Program.objects.create(
            university=self.university,
            name_en="Pharmacy Services",
            slug_en="pharmacy-services",
            degree="associate",
        )
        self.offering = ProgramOffering.objects.create(
            program=self.program,
            academic_year=self.year,
            intake=self.intake,
        )

    def test_program_offering_admin_prioritizes_structured_fees(self):
        from django.contrib import admin

        from apps.universities.admin import OfferingFeeInline, ProgramOfferingAdmin

        admin_instance = admin.site._registry[ProgramOffering]
        self.assertIsInstance(admin_instance, ProgramOfferingAdmin)
        self.assertEqual(admin_instance.inlines, (OfferingFeeInline,))
        self.assertIn("structured_fee_summary", admin_instance.readonly_fields)

        fieldsets = {title: options for title, options in admin_instance.fieldsets}
        self.assertIn("Structured fees", fieldsets)
        self.assertNotIn("Legacy compatibility pricing", fieldsets)
        self.assertIn("structured_fee_summary", fieldsets["Structured fees"]["fields"])

    def test_structured_fee_summary_uses_semantic_fee_order(self):
        from django.contrib import admin

        OfferingFee.objects.create(
            offering=self.offering,
            fee_type=OfferingFeeType.PREPARATORY,
            currency="USD",
            amount=Decimal("1390"),
            basis=FeeBasis.ANNUAL,
        )
        OfferingFee.objects.create(
            offering=self.offering,
            fee_type=OfferingFeeType.ADVANCE_PAYMENT,
            currency="USD",
            amount=Decimal("2925"),
            basis=FeeBasis.ANNUAL,
        )
        OfferingFee.objects.create(
            offering=self.offering,
            fee_type=OfferingFeeType.TUITION,
            currency="USD",
            amount=Decimal("3250"),
            basis=FeeBasis.ANNUAL,
        )

        admin_instance = admin.site._registry[ProgramOffering]
        summary = str(admin_instance.structured_fee_summary(self.offering))

        self.assertLess(summary.index("Tuition / list fee"), summary.index("Advance payment"))
        self.assertLess(
            summary.index("Advance payment"),
            summary.index("Preparatory / foundation tuition"),
        )

    def test_program_inline_has_no_legacy_pricing_section(self):
        from django.contrib import admin

        from apps.universities.admin import ProgramOfferingInline

        inline = ProgramOfferingInline(Program, admin.site)
        fieldsets = {title: options for title, options in inline.fieldsets}
        self.assertIn("Structured fees", fieldsets)
        self.assertNotIn("Legacy compatibility pricing", fieldsets)
        self.assertIn("structured_fee_summary", inline.readonly_fields)
