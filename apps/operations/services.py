from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.applications.models import Application
from apps.leads.models import Lead, LeadActivity, LeadActivityType

from .models import CommunicationLog, CommunicationLogRevision, Todo, TodoStatus


def subject_pair(subject):
    if subject is None:
        return None, None
    return ContentType.objects.get_for_model(subject), subject.pk


def _subject_q(subjects) -> Q:
    query = Q(pk__in=[])
    for subject in subjects:
        content_type, object_id = subject_pair(subject)
        query |= Q(
            subject_content_type=content_type,
            subject_object_id=object_id,
        )
    return query


def subjects_for_parent(subject) -> list:
    subjects = [subject]
    if isinstance(subject, Lead) and subject.converted_student_id:
        subjects.extend(Application.objects.filter(student_id=subject.converted_student_id))
    return subjects


def todos_for_subject_tree(*, agent, subject) -> QuerySet[Todo]:
    return Todo.objects.filter(agent=agent).filter(_subject_q(subjects_for_parent(subject)))


def communications_for_subject_tree(*, agent, subject) -> QuerySet[CommunicationLog]:
    return CommunicationLog.objects.filter(agent=agent).filter(
        _subject_q(subjects_for_parent(subject))
    )


def _lead_for_subject(subject):
    if isinstance(subject, Lead):
        return subject
    if isinstance(subject, Application):
        source_lead = getattr(subject.student, "source_lead", None)
        return source_lead
    return None


def _record_private_activity(*, subject, actor, description, metadata=None):
    lead = _lead_for_subject(subject)
    if lead is None:
        return
    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.NOTE,
        description=description,
        metadata=metadata or {},
        is_customer_visible=False,
        created_by=actor,
        updated_by=actor,
    )


@transaction.atomic
def create_todo(*, agent, actor, title, description="", due_date=None, assignee=None, subject=None):
    if assignee is not None and not agent.users.filter(pk=assignee.pk).exists():
        raise PermissionDenied("Assignee must belong to the active Agent organization.")
    content_type, object_id = subject_pair(subject)
    todo = Todo.objects.create(
        agent=agent,
        title=title,
        description=description,
        due_date=due_date,
        assignee=assignee,
        subject_content_type=content_type,
        subject_object_id=object_id,
        created_by=actor,
        updated_by=actor,
    )
    _record_private_activity(
        subject=subject,
        actor=actor,
        description=f"TODO created: {todo.title}.",
        metadata={"todo_id": str(todo.pk), "event": "todo_created"},
    )
    return todo


@transaction.atomic
def update_todo(*, todo, actor, status=None, assignee_marker=False, assignee=None):
    if not todo.agent.users.filter(pk=actor.pk).exists():
        raise PermissionDenied("Active Agent membership is required.")
    fields = ["updated_by", "updated_at"]
    if assignee_marker:
        if assignee is not None and not todo.agent.users.filter(pk=assignee.pk).exists():
            raise PermissionDenied("Assignee must belong to the owning Agent organization.")
        todo.assignee = assignee
        fields.append("assignee")
    if status is not None:
        if status not in TodoStatus.values:
            raise ValueError("Invalid TODO status.")
        todo.status = status
        fields.append("status")
        if status == TodoStatus.DONE:
            todo.completed_by = actor
            todo.completed_at = timezone.now()
        else:
            todo.completed_by = None
            todo.completed_at = None
        fields.extend(["completed_by", "completed_at"])
    todo.updated_by = actor
    todo.save(update_fields=tuple(dict.fromkeys(fields)))
    _record_private_activity(
        subject=todo.subject,
        actor=actor,
        description=f"TODO updated: {todo.title} · {todo.get_status_display()}.",
        metadata={"todo_id": str(todo.pk), "event": "todo_updated"},
    )
    return todo


@transaction.atomic
def add_todo_comment(*, todo, actor, body):
    if not todo.agent.users.filter(pk=actor.pk).exists():
        raise PermissionDenied("Active Agent membership is required.")
    comment = todo.comments.create(
        author=actor,
        body=body,
        created_by=actor,
        updated_by=actor,
    )
    _record_private_activity(
        subject=todo.subject,
        actor=actor,
        description=f"Comment added to TODO: {todo.title}.",
        metadata={"todo_id": str(todo.pk), "event": "todo_comment"},
    )
    return comment


def _communication_snapshot(communication):
    return {
        "occurred_at": communication.occurred_at.isoformat(),
        "channel": communication.channel,
        "counterparty_type": communication.counterparty_type,
        "counterparty_name": communication.counterparty_name,
        "summary": communication.summary,
    }


@transaction.atomic
def create_communication(
    *,
    agent,
    actor,
    occurred_at,
    channel,
    counterparty_type,
    counterparty_name="",
    summary,
    subject=None,
):
    content_type, object_id = subject_pair(subject)
    communication = CommunicationLog.objects.create(
        agent=agent,
        performed_by=actor,
        occurred_at=occurred_at,
        channel=channel,
        counterparty_type=counterparty_type,
        counterparty_name=counterparty_name,
        summary=summary,
        subject_content_type=content_type,
        subject_object_id=object_id,
        created_by=actor,
        updated_by=actor,
    )
    _record_private_activity(
        subject=subject,
        actor=actor,
        description=f"Communication logged: {communication.get_channel_display()}.",
        metadata={
            "communication_id": str(communication.pk),
            "event": "communication_logged",
        },
    )
    return communication


@transaction.atomic
def edit_communication(*, communication, actor, values):
    if communication.created_by_id != actor.pk:
        raise PermissionDenied("Only the creator can edit this Communication Log entry.")
    CommunicationLogRevision.objects.create(
        communication=communication,
        revised_by=actor,
        snapshot=_communication_snapshot(communication),
        created_by=actor,
        updated_by=actor,
    )
    for field in (
        "occurred_at",
        "channel",
        "counterparty_type",
        "counterparty_name",
        "summary",
    ):
        if field in values:
            setattr(communication, field, values[field])
    communication.updated_by = actor
    communication.save()
    _record_private_activity(
        subject=communication.subject,
        actor=actor,
        description=f"Communication log edited: {communication.get_channel_display()}.",
        metadata={
            "communication_id": str(communication.pk),
            "event": "communication_edited",
        },
    )
    return communication
