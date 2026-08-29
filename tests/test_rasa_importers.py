import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from apps.content.models import FAQ, FAQCategory
from apps.geography.models import Country
from apps.universities.models import Program, ProgramOffering, University


class RasaImporterTests(TestCase):
    def setUp(self):
        Country.objects.create(
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
        )

    def test_import_rasa_catalogue_and_content(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp)

            (source / "universities.json").write_text(
                json.dumps(
                    {
                        "universities": [
                            {
                                "id": 1,
                                "slug": "example-university",
                                "name_en": "Example University",
                                "name_fa": "دانشگاه نمونه",
                                "name_tr": "Örnek Üniversitesi",
                                "city_en": "Istanbul",
                                "type": "private",
                                "moe_approved": True,
                                "moh_approved": False,
                                "erasmus": True,
                                "boost_score": 5,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            (source / "programs.json").write_text(
                json.dumps(
                    {
                        "programs": [
                            {
                                "id": 10,
                                "university_id": 1,
                                "slug": "computer-engineering",
                                "name_en": "Computer Engineering",
                                "degree": "bachelor",
                                "language": "english",
                                "duration_years": "4.0",
                                "tuition_usd": 6000,
                                "tuition_discounted_usd": 5000,
                                "quota": "40.0",
                                "boost_score": "2.0",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            (source / "faq_categories.json").write_text(
                json.dumps(
                    {
                        "cats": [
                            {
                                "id": 100,
                                "key": "admissions",
                                "name_en": "Admissions",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            (source / "faqs.json").write_text(
                json.dumps(
                    {
                        "faqs": [
                            {
                                "id": 101,
                                "category": "admissions",
                                "question_en": "How do I apply?",
                                "answer_en": "Submit an application.",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            call_command("import_rasa_data", str(source))

            self.assertEqual(University.objects.count(), 1)
            self.assertEqual(Program.objects.count(), 1)
            program = Program.objects.get()
            self.assertEqual(program.duration, 4)
            self.assertEqual(program.duration_months, 48)
            self.assertEqual(program.instruction_languages.count(), 1)
            self.assertEqual(program.listing_priority, 2)
            self.assertEqual(ProgramOffering.objects.count(), 1)
            offering = ProgramOffering.objects.get()
            self.assertEqual(offering.quota, 40)
            self.assertEqual(FAQCategory.objects.count(), 1)
            self.assertEqual(FAQ.objects.count(), 1)
            self.assertEqual(FAQ.objects.get().category.key, "admissions")

            system_user = get_user_model().objects.get(username="system")
            university = University.objects.get()
            program = Program.objects.get()
            faq = FAQ.objects.get()
            self.assertEqual(university.created_by, system_user)
            self.assertEqual(university.updated_by, system_user)
            self.assertEqual(program.created_by, system_user)
            self.assertEqual(program.updated_by, system_user)
            self.assertEqual(faq.created_by, system_user)
            self.assertEqual(faq.updated_by, system_user)

            # Idempotency
            call_command("import_rasa_data", str(source))
            self.assertEqual(University.objects.count(), 1)
            self.assertEqual(Program.objects.count(), 1)
            self.assertEqual(FAQ.objects.count(), 1)
