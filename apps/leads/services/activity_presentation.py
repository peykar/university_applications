from __future__ import annotations

import re
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from apps.students.models import DocumentType
from apps.universities.models import Program

from ..models import LeadActivity, LeadActivityType, LeadDocumentReviewStatus

_FINALIZED_RE = re.compile(
    r"^Finalized and converted to Student (?P<student>[^;]+); created "
    r"(?P<count>\d+) draft application\(s\)\.$"
)
_REFINALIZED_RE = re.compile(
    r"^Re-finalized existing Student (?P<student>[^;]+); created "
    r"(?P<count>\d+) new draft application\(s\)\.$"
)
_REASSIGNED_RE = re.compile(r"^Reassigned from (?P<old>.+) to (?P<new>.+)\.$")
_ASSIGNED_RE = re.compile(r"^Assigned to (?P<assignee>.+)\.$")
_DOCUMENT_REVIEWED_RE = re.compile(r"^Document reviewed: (?P<document>.+) → (?P<status>.+)\.$")


_FIELD_LABELS = {
    "first_name": gettext_lazy("First name"),
    "middle_name": gettext_lazy("Middle name"),
    "last_name": gettext_lazy("Last name"),
    "email": gettext_lazy("Email"),
    "cell": gettext_lazy("Cell"),
    "birthdate": gettext_lazy("Birthdate"),
    "gender": gettext_lazy("Gender"),
    "nationality": gettext_lazy("Nationality"),
    "country_of_birth": gettext_lazy("Country of birth"),
    "country_of_residence": gettext_lazy("Country of residence"),
    "city_of_residence": gettext_lazy("City of residence"),
    "address": gettext_lazy("Address"),
    "father_name": gettext_lazy("Father name"),
    "mother_name": gettext_lazy("Mother name"),
    "passport_no": gettext_lazy("Passport no"),
    "passport_issuing_authority": gettext_lazy("Passport issuing authority"),
    "passport_date_of_issue": gettext_lazy("Passport date of issue"),
    "passport_date_of_expiry": gettext_lazy("Passport date of expiry"),
    "english_test_type": gettext_lazy("English test type"),
    "english_language_test_score": gettext_lazy("English language test score"),
    "high_school_gpa": gettext_lazy("High school gpa"),
    "high_school_gpa_scale": gettext_lazy("High school gpa scale"),
    "educational_background": gettext_lazy("Educational background"),
    "notes": gettext_lazy("Notes"),
}


def localized_activity_changes(activity: LeadActivity) -> list[dict[str, Any]]:
    """Localize structured audit field labels without changing snapshot values."""
    localized: list[dict[str, Any]] = []
    for change in activity.metadata.get("changes", []):
        row = dict(change)
        field_name = str(row.get("field") or "")
        if field_name in _FIELD_LABELS:
            row["label"] = str(_FIELD_LABELS[field_name])
        localized.append(row)
    return localized


def _student_display_name(student_id: str) -> str:
    if not student_id:
        return ""

    from apps.students.models import Student

    try:
        student = Student.objects.filter(pk=student_id).first()
    except (TypeError, ValueError, ValidationError):
        return ""

    return str(student).strip() if student is not None else ""


def _program_name(activity: LeadActivity) -> str:
    program_id = activity.metadata.get("program_id")
    if program_id:
        try:
            program = Program.objects.filter(pk=program_id).first()
        except (TypeError, ValueError, ValidationError):
            program = None
        if program is not None:
            return program.localized_name
    return ""


def _document_label(metadata: dict[str, Any]) -> str:
    document_name = str(metadata.get("document_name") or "").strip()
    if document_name:
        return document_name
    document_type = metadata.get("document_type")
    if document_type:
        return str(dict(DocumentType.choices).get(document_type, document_type))
    return str(metadata.get("document_label") or "").strip()


def _review_status_label(metadata: dict[str, Any]) -> str:
    review_status = metadata.get("review_status")
    if review_status:
        return str(dict(LeadDocumentReviewStatus.choices).get(review_status, review_status))
    return str(metadata.get("review_status_label") or "").strip()


def _legacy_tail(description: str, prefix: str, *, suffix: str = ".") -> str:
    if not description.startswith(prefix):
        return ""
    value = description[len(prefix) :]
    if suffix and value.endswith(suffix):
        value = value[: -len(suffix)]
    return value.strip()


def localized_activity_description(activity: LeadActivity) -> str:
    """Render a predefined Lead activity in the viewer's active language.

    ``LeadActivity.description`` remains an immutable audit/fallback payload. New
    structured metadata is preferred for dynamic values, while legacy English
    descriptions are parsed so existing audit history also localizes without a
    data migration. Unknown/free-form descriptions are returned verbatim.
    """
    description = activity.description or ""
    metadata: dict[str, Any] = activity.metadata or {}
    activity_type = activity.activity_type

    if activity_type == LeadActivityType.CREATED and description == "Applicant profile created.":
        return _("Applicant profile created.")

    if (
        activity_type == LeadActivityType.INTERNAL_NOTES_UPDATED
        and description == "Internal notes updated."
    ):
        return _("Internal notes updated.")

    if activity_type == LeadActivityType.REOPENED:
        if (
            metadata.get("program_id")
            or description == "Request reopened after a new program was added."
        ):
            return _("Request reopened after a new program was added.")
        if description == "Lead reopened.":
            return _("Lead reopened.")

    if activity_type == LeadActivityType.CLOSED:
        reason = str(metadata.get("close_reason") or "").strip()
        if not reason and description.startswith("Lead closed. Reason: "):
            reason = description.removeprefix("Lead closed. Reason: ").strip()
        if reason:
            return _("Lead closed. Reason: %(reason)s") % {"reason": reason}
        if description == "Lead closed.":
            return _("Lead closed.")

    if activity_type == LeadActivityType.ASSIGNED:
        assignee = str(metadata.get("assignee_name") or "").strip()
        if not assignee:
            match = _ASSIGNED_RE.match(description)
            assignee = match.group("assignee") if match else ""
        if assignee:
            return _("Assigned to %(assignee)s.") % {"assignee": assignee}

    if activity_type == LeadActivityType.REASSIGNED:
        old_name = str(metadata.get("previous_assignee_name") or "").strip()
        new_name = str(metadata.get("assignee_name") or "").strip()
        if not (old_name and new_name):
            match = _REASSIGNED_RE.match(description)
            if match:
                old_name = match.group("old")
                new_name = match.group("new")
        if old_name and new_name:
            return _("Reassigned from %(old)s to %(new)s.") % {
                "old": old_name,
                "new": new_name,
            }

    if activity_type in {
        LeadActivityType.PROGRAM_ADDED,
        LeadActivityType.PROGRAM_SUGGESTED,
        LeadActivityType.PROGRAM_RESPONSE,
    }:
        program_name = _program_name(activity)
        action = metadata.get("action")
        if not program_name:
            prefixes: dict[str, str] = {
                LeadActivityType.PROGRAM_ADDED: "Program added: ",
                LeadActivityType.PROGRAM_SUGGESTED: "Program suggested: ",
            }
            prefix = prefixes.get(activity_type)
            if prefix:
                program_name = _legacy_tail(description, prefix)
            if activity_type == LeadActivityType.PROGRAM_RESPONSE:
                for candidate, candidate_action in (
                    ("Program intake updated: ", "intake_updated"),
                    ("Program removed: ", "program_removed"),
                    ("Program recommendation removed: ", "recommendation_removed"),
                ):
                    legacy_name = _legacy_tail(description, candidate)
                    if legacy_name:
                        program_name = legacy_name
                        action = action or candidate_action
                        break

        if program_name:
            if activity_type == LeadActivityType.PROGRAM_ADDED:
                return _("Program added: %(program)s.") % {"program": program_name}
            if activity_type == LeadActivityType.PROGRAM_SUGGESTED:
                return _("Program suggested: %(program)s.") % {"program": program_name}
            if action == "intake_updated":
                return _("Program intake updated: %(program)s.") % {"program": program_name}
            if action == "program_removed":
                return _("Program removed: %(program)s.") % {"program": program_name}
            if action == "recommendation_removed":
                return _("Program recommendation removed: %(program)s.") % {"program": program_name}

    if activity_type == LeadActivityType.DOCUMENT_UPLOADED:
        document = _document_label(metadata)
        action = metadata.get("action")
        if not document:
            candidates = (
                ("Document uploaded: ", "uploaded"),
                ("Replacement uploaded: ", "replacement_uploaded"),
                ("Chat attachment added to Documents: ", "chat_attachment_added"),
            )
            for prefix, candidate_action in candidates:
                legacy_document = _legacy_tail(description, prefix)
                if legacy_document:
                    document = legacy_document
                    action = action or candidate_action
                    break
            suffix = " uploaded and approved by agent user."
            if not document and description.endswith(suffix):
                document = description[: -len(suffix)].strip()
                action = action or "agent_uploaded_approved"
        if document:
            if action == "replacement_uploaded":
                return _("Replacement uploaded: %(document)s.") % {"document": document}
            if action == "agent_uploaded_approved":
                return _("%(document)s uploaded and approved by agent user.") % {
                    "document": document
                }
            if action == "chat_attachment_added":
                return _("Chat attachment added to Documents: %(document)s.") % {
                    "document": document
                }
            return _("Document uploaded: %(document)s.") % {"document": document}

    if activity_type == LeadActivityType.DOCUMENT_REVIEWED:
        document = _document_label(metadata)
        action = metadata.get("action")
        if action == "student_conversion_approved" or description.startswith(
            "Document approved during Student record creation: "
        ):
            if not document:
                document = _legacy_tail(
                    description,
                    "Document approved during Student record creation: ",
                )
            if document:
                return _("Document approved during Student record creation: %(document)s.") % {
                    "document": document
                }

        status = _review_status_label(metadata)
        if not (document and status):
            match = _DOCUMENT_REVIEWED_RE.match(description)
            if match:
                document = document or match.group("document")
                status = status or match.group("status")
        if document and status:
            return _("Document reviewed: %(document)s → %(status)s.") % {
                "document": document,
                "status": status,
            }

    if activity_type == LeadActivityType.FINALIZED:
        student_id = str(metadata.get("student_id") or "").strip()
        count = metadata.get("new_application_count")
        reopened = bool(metadata.get("reopened"))
        match = _REFINALIZED_RE.match(description) if reopened else _FINALIZED_RE.match(description)
        if match:
            student_id = student_id or match.group("student")
            if count is None:
                count = int(match.group("count"))

        if count is not None:
            student_name = _student_display_name(student_id)
            if reopened:
                if student_name:
                    message = _(
                        "Re-finalized existing Student %(student)s; created %(count)s "
                        "new draft application(s)."
                    )
                    return message % {"student": student_name, "count": count}
                return _(
                    "Re-finalized existing student record; created %(count)s "
                    "new draft application(s)."
                ) % {"count": count}

            if student_name:
                message = _(
                    "Finalized and converted to Student %(student)s; created %(count)s "
                    "draft application(s)."
                )
                return message % {"student": student_name, "count": count}
            return _(
                "Finalized and converted to a student record; created %(count)s "
                "draft application(s)."
            ) % {"count": count}

    return description
