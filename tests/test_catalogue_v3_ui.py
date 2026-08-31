from decimal import Decimal
from pathlib import Path

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.geography.models import City, Country, Province
from apps.universities.models import (
    AcademicYear,
    FeeBasis,
    Intake,
    OfferingFee,
    OfferingFeeType,
    Program,
    ProgramOffering,
    University,
)

ROOT = Path(__file__).resolve().parents[1]


class CatalogueV3UIContractTests(SimpleTestCase):
    def test_public_and_customer_templates_do_not_read_legacy_offering_fields(self):
        paths = [
            ROOT / "templates/public/program_detail.html",
            ROOT / "templates/public/program_list.html",
            ROOT / "templates/public/university_detail.html",
            ROOT / "templates/leads/lead_section.html",
            ROOT / "templates/leads/lead_detail.html",
            ROOT / "templates/applications/customer_detail.html",
            ROOT / "templates/agents/student_detail.html",
        ]
        legacy_tokens = (
            ".semester",
            ".tuition_discounted",
            ".tuition_cash",
            ".preparatory_tuition",
        )
        for path in paths:
            source = path.read_text()
            for token in legacy_tokens:
                self.assertNotIn(token, source, f"{path} still uses Catalogue v2 token {token}")

    def test_program_filters_use_canonical_intake_parameter(self):
        source = (ROOT / "apps/public/services/program_filters.py").read_text()
        self.assertIn('intake: str = ""', source)
        self.assertIn('params.get("intake")', source)
        self.assertIn("offerings.filter(intake_id=intake_id)", source)
        self.assertNotIn('params.get("semester")', source)

    def test_public_program_detail_uses_structured_fees(self):
        source = (ROOT / "templates/public/program_detail.html").read_text()
        self.assertIn("offering.display_tuition_fee", source)
        self.assertIn("offering.display_fees", source)
        self.assertIn("offering.intake.localized_name", source)
        self.assertIn("tuition_fee.display_label", source)
        self.assertIn("fee.display_label", source)


class PublicStructuredFeePresentationTests(TestCase):
    def setUp(self):
        country = Country.objects.create(
            name_en="Türkiye",
            slug_en="turkiye-fee-ui",
            iso2="TR",
            iso3="TUR",
        )
        province = Province.objects.create(
            country=country,
            name_en="Istanbul",
            slug_en="istanbul-fee-ui",
        )
        city = City.objects.create(
            province=province,
            name_en="Istanbul",
            slug_en="istanbul-fee-ui",
        )
        university = University.objects.create(
            name_en="Istanbul Atlas University",
            slug_en="istanbul-atlas-university-fee-ui",
            city=city,
            university_type="private",
        )
        year = AcademicYear.objects.create(name_en="2026-2027")
        intake = Intake.objects.create(
            university=university,
            academic_year=year,
            name_en="Academic Intake",
        )
        self.program = Program.objects.create(
            university=university,
            name_en="Artificial Intelligence and Smart Systems",
            degree="master",
            thesis_type="thesis",
        )
        offering = ProgramOffering.objects.create(
            program=self.program,
            academic_year=year,
            intake=intake,
        )
        OfferingFee.objects.create(
            offering=offering,
            fee_type=OfferingFeeType.TUITION,
            label="Tuition fee",
            currency="USD",
            amount=Decimal("5550.00"),
            basis=FeeBasis.ANNUAL,
        )
        OfferingFee.objects.create(
            offering=offering,
            fee_type=OfferingFeeType.DISCOUNTED_TUITION,
            label="Scholarship fee (10%)",
            currency="USD",
            amount=Decimal("4995.00"),
            percentage=Decimal("10.00"),
            basis=FeeBasis.ANNUAL,
        )
        OfferingFee.objects.create(
            offering=offering,
            fee_type=OfferingFeeType.ADVANCE_PAYMENT,
            label="Advance payment (15%)",
            currency="USD",
            amount=Decimal("4246.00"),
            percentage=Decimal("15.00"),
            basis=FeeBasis.ANNUAL,
        )
        OfferingFee.objects.create(
            offering=offering,
            fee_type=OfferingFeeType.DEPOSIT,
            label="Deposit payment",
            currency="USD",
            amount=Decimal("1000.00"),
            basis=FeeBasis.ONE_TIME,
        )

    def test_program_detail_preserves_fee_semantics_and_basis(self):
        response = self.client.get(reverse("program-detail", args=[self.program.slug_en]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Scholarship fee (10%)", count=1)
        self.assertContains(response, "$4,995 USD")
        self.assertContains(response, "Tuition fee")
        self.assertContains(response, "$5,550 USD")
        self.assertContains(response, "Advance payment (15%)", count=1)
        self.assertContains(response, "$4,246 USD")
        self.assertContains(response, "Deposit payment")
        self.assertContains(response, "$1,000 USD")
        self.assertNotContains(response, "$4,246 USD15%")
        self.assertGreaterEqual(response.content.decode().count("Annual"), 3)
        self.assertContains(response, "One time")

    def test_display_label_adds_percentage_only_when_source_label_omits_it(self):
        fee = OfferingFee.objects.create(
            offering=self.program.offerings.get(),
            fee_type=OfferingFeeType.CASH_PAYMENT,
            label="Cash payment",
            currency="USD",
            amount=Decimal("4000.00"),
            percentage=Decimal("12.50"),
            basis=FeeBasis.ANNUAL,
        )

        self.assertEqual(fee.display_label, "Cash payment (12.5%)")
