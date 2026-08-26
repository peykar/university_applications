from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class ApplicantHeaderFactsUiTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_email_is_a_fact_not_header_subtitle(self):
        self.assertIn(
            '<dt>{% trans "Email" %}</dt><dd>'
            '{{ lead.email|default:lead.user.email|default:"—" }}</dd>',
            self.template,
        )
        self.assertNotIn(
            "</div><p>{{ lead.email|default:lead.user.email }}</p></div>",
            self.template,
        )

    def test_updated_information_is_compact_audit_chip(self):
        self.assertIn("applicant-audit-chip", self.template)
        self.assertIn("aria-label=\"{% trans 'Applicant update information' %}\"", self.template)
        self.assertNotIn(
            '{% trans "Updated" %} {{ lead.updated_at|date:"M j, Y H:i" }}',
            self.template,
        )
        self.assertIn(".applicant-audit-chip{", self.css)

    def test_suggest_program_uses_shared_action_control(self):
        self.assertIn(
            "section-action agent-action-control program-suggest-action",
            self.template,
        )
