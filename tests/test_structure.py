from django.test import TestCase

from apps.agents.models import Agent
from apps.content.models import FAQCategory
from apps.geography.models import Country
from apps.universities.models import University


class StructureSmokeTests(TestCase):
    def test_models_import(self):
        self.assertIsNotNone(Agent)
        self.assertIsNotNone(FAQCategory)
        self.assertIsNotNone(Country)
        self.assertIsNotNone(University)
