from __future__ import annotations

import ast
import gettext
import re
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings
from django.template import Context, Template
from django.test import SimpleTestCase
from django.utils import translation

from apps.core.localization import localized_value, normalized_language_code
from apps.public.forms import ContactForm

ROOT = Path(settings.BASE_DIR)
LOCALES = ("fa", "tr", "ar")
TRANSLATE_LITERAL_RE = re.compile(r"{%\s*(?:trans|translate)\s+[\"']([^\"']+)[\"']")


class LocalizedValueTests(SimpleTestCase):
    def test_active_locale_is_preferred_and_english_is_fallback(self):
        item = SimpleNamespace(name_en="English name", name_fa="نام فارسی")

        with translation.override("fa"):
            self.assertEqual(localized_value(item), "نام فارسی")

        item.name_fa = ""
        with translation.override("fa"):
            self.assertEqual(localized_value(item), "English name")

    def test_unsupported_locale_normalizes_to_english(self):
        self.assertEqual(normalized_language_code("de-DE"), "en")

    def test_template_filter_and_interface_copy_follow_same_locale(self):
        item = {"name_en": "English name", "name_fa": "نام فارسی"}
        template = Template(
            "{% load i18n localization %}"
            '{{ item|localized:"name" }} · {% translate "Available offerings" %}'
        )
        with translation.override("fa"):
            rendered = template.render(Context({"item": item}))

        self.assertIn("نام فارسی", rendered)
        self.assertIn("گزینه‌های پذیرش موجود", rendered)
        self.assertNotIn("Available offerings", rendered)


class TranslationEnabledSurfaceTests(SimpleTestCase):
    def _catalog(self, language: str):
        path = ROOT / "locale" / language / "LC_MESSAGES" / "django.mo"
        with path.open("rb") as handle:
            return gettext.GNUTranslations(handle)._catalog

    def _template_paths(self):
        for path in (ROOT / "templates").rglob("*.html"):
            if "emails" in path.parts or "admin_tools" in path.parts:
                continue
            yield path

    def _python_gettext_literals(self):
        msgids: set[str] = set()
        for path in (ROOT / "apps").rglob("*.py"):
            if (
                "migrations" in path.parts
                or "tests" in path.parts
                or "management" in path.parts
                or path.name == "admin.py"
            ):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not node.args:
                    continue
                if not isinstance(node.func, ast.Name):
                    continue
                if node.func.id not in {"_", "gettext", "gettext_lazy"}:
                    continue
                first = node.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    msgids.add(first.value)
        return msgids

    def test_translation_enabled_templates_do_not_force_english_model_fields(self):
        forbidden = re.compile(r"\.(?:name|description|question|answer)_en\b")
        offenders: list[str] = []
        for path in self._template_paths():
            if forbidden.search(path.read_text(encoding="utf-8")):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_literal_interface_translations_exist_for_all_supported_non_english_locales(self):
        msgids = self._python_gettext_literals()
        for path in self._template_paths():
            msgids.update(TRANSLATE_LITERAL_RE.findall(path.read_text(encoding="utf-8")))

        missing: dict[str, list[str]] = {}
        for language in LOCALES:
            catalog = self._catalog(language)
            gaps = sorted(msgid for msgid in msgids if not catalog.get(msgid))
            if gaps:
                missing[language] = gaps
        self.assertEqual(missing, {})

    def test_representative_surface_families_use_localization_contract(self):
        representatives = (
            "templates/public/program_detail.html",
            "templates/account/login.html",
            "templates/leads/lead_section.html",
            "templates/messaging/customer_inbox.html",
            "templates/agents/applicant_section.html",
            "templates/base.html",
        )
        for relative in representatives:
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertTrue(
                "{% trans " in source or "{% translate " in source or "{% blocktrans" in source,
                relative,
            )

    def test_model_generated_form_labels_are_translated(self):
        with translation.override("fa"):
            form = ContactForm()
            self.assertEqual(form.fields["name"].label, "نام")
            self.assertEqual(form.fields["email"].label, "ایمیل")
            self.assertEqual(form.fields["message"].label, "پیام")
