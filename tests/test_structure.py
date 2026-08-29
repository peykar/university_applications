from pathlib import Path

from django.conf import settings
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

    def test_critical_repository_files_are_preserved(self):
        root = Path(settings.BASE_DIR)
        required = [
            ".gitignore",
            "pyproject.toml",
            "Makefile",
            "README.md",
            "AGENTS.md",
            "docs/changes/features/.gitkeep",
            "docs/changes/discovery/.gitkeep",
            "docs/changes/bugs/.gitkeep",
            "docs/changes/conflicts/.gitkeep",
            "docs/changes/refactors/.gitkeep",
            "docs/changes/ui/.gitkeep",
            "docs/changes/changes/.gitkeep",
            "docs/changes/archived/.gitkeep",
        ]
        missing = [path for path in required if not (root / path).exists()]
        self.assertEqual(missing, [])
