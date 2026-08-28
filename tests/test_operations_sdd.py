from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from apps.operations.models import (
    CommunicationChannel,
    CommunicationCounterpartyType,
    TodoStatus,
)


class OperationsSDDTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)
        self.models = (self.root / "apps/operations/models.py").read_text(encoding="utf-8")
        self.services = (self.root / "apps/operations/services.py").read_text(encoding="utf-8")
        self.views = (self.root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (self.root / "apps/agents/urls.py").read_text(encoding="utf-8")

    def test_todo_lifecycle_matches_baseline(self):
        self.assertEqual(
            set(TodoStatus.values),
            {"created", "in_progress", "done", "cancelled"},
        )
        self.assertIn("completed_by", self.models)
        self.assertIn("completed_at", self.models)

    def test_todo_has_optional_generic_subject_and_single_assignee(self):
        self.assertIn("subject_content_type", self.models)
        self.assertIn("subject_object_id", self.models)
        self.assertIn("assignee = models.ForeignKey(", self.models)
        self.assertIn("todo_subject_pair_consistent", self.models)

    def test_todo_comments_are_immutable(self):
        comment_block = self.models.split("class TodoComment", 1)[1].split(
            "class CommunicationChannel", 1
        )[0]
        self.assertIn("immutable after posting", comment_block)

    def test_communication_v1_choices_match_baseline(self):
        self.assertEqual(
            set(CommunicationChannel.values),
            {"phone", "email", "whatsapp", "telegram", "in_person", "video_call", "other"},
        )
        self.assertEqual(
            set(CommunicationCounterpartyType.values),
            {"customer", "university", "other"},
        )

    def test_communication_edits_create_revision_first(self):
        edit_block = self.services.split("def edit_communication", 1)[1]
        self.assertIn("CommunicationLogRevision.objects.create(", edit_block)
        self.assertIn("communication.created_by_id != actor.pk", edit_block)

    def test_parent_aggregation_includes_applications_for_lead(self):
        scope_block = self.services.split("def subjects_for_parent", 1)[1].split(
            "def todos_for_subject_tree", 1
        )[0]
        self.assertIn("isinstance(subject, Lead)", scope_block)
        self.assertIn("Application.objects.filter", scope_block)

    def test_global_and_contextual_routes_exist(self):
        for route_name in (
            "agent-todo-list",
            "agent-communication-list",
            "agent-applicant-todos",
            "agent-applicant-communications",
            "agent-application-todos",
            "agent-application-communications",
        ):
            self.assertIn(f'name="{route_name}"', self.urls)

    def test_activity_integration_is_private_for_applicant(self):
        self.assertIn("is_customer_visible=False", self.services)
        self.assertIn('"title": "TODO"', self.views)
        self.assertIn('"title": "Communication Log"', self.views)
