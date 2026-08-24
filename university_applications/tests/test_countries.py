from django.core.management import call_command
from django.test import TestCase

from university_applications.models import Country


class PopulateCountriesCommandTests(TestCase):
    def test_populate_countries_creates_iso_and_translated_names(self):
        call_command("populate_countries")
        nl = Country.objects.get(iso2="NL")
        self.assertEqual(nl.iso3, "NLD")
        self.assertTrue(nl.name_en)
        self.assertTrue(nl.name_fa)
        self.assertTrue(nl.name_tr)
        self.assertTrue(nl.name_ar)
        self.assertTrue(nl.slug_en)

    def test_populate_countries_is_idempotent(self):
        call_command("populate_countries")
        count_before = Country.objects.count()
        call_command("populate_countries")
        self.assertEqual(count_before, Country.objects.count())
