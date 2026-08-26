from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentApplicantHolisticUiTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_applicant_detail_has_scoped_visual_system(self):
        self.assertIn("applicant-workspace-detail", self.template)
        self.assertIn(".applicant-workspace-detail .agent-panel{", self.css)
        self.assertIn(".applicant-workspace-detail .agent-facts>div{", self.css)

    def test_conversation_has_no_inner_scrollbar(self):
        self.assertIn(".applicant-workspace-detail .agent-chat{", self.css)
        scoped = self.css.split(
            ".applicant-workspace-detail .agent-chat{",
            1,
        )[1].split("}", 1)[0]
        self.assertIn("max-height:none", scoped)
        self.assertIn("overflow:visible", scoped)
        self.assertNotIn("overflow-y:auto", scoped)

    def test_messages_are_more_readable(self):
        self.assertIn(".applicant-workspace-detail .agent-message{", self.css)
        self.assertIn("font-size:.86rem", self.css)
        self.assertIn("line-height:1.5", self.css)

    def test_mobile_layout_remains_single_column(self):
        self.assertIn("@media(max-width:900px)", self.css)
        self.assertIn("grid-template-columns:1fr", self.css)
