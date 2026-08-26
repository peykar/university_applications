from django.urls import path

from . import views

urlpatterns = [
    path("agent/", views.dashboard, name="agent-dashboard"),
    path("agent/applicants/", views.applicant_list, name="agent-applicant-list"),
    path(
        "agent/applicants/<uuid:lead_id>/",
        views.applicant_detail,
        name="agent-applicant-detail",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/edit/",
        views.applicant_edit,
        name="agent-applicant-edit",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/internal-notes/",
        views.applicant_internal_notes,
        name="agent-applicant-internal-notes",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/documents/upload/",
        views.applicant_document_upload,
        name="agent-applicant-document-upload",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/status/",
        views.applicant_status,
        name="agent-applicant-status",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/assign-to-me/",
        views.applicant_assign_to_me,
        name="agent-applicant-assign-to-me",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/assign/",
        views.applicant_assign,
        name="agent-applicant-assign",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/finalize/",
        views.applicant_finalize,
        name="agent-applicant-finalize",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/messages/",
        views.applicant_message,
        name="agent-applicant-message",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/documents/<uuid:document_id>/review/",
        views.applicant_document_review,
        name="agent-applicant-document-review",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/attachments/<uuid:attachment_id>/document/",
        views.applicant_attachment_to_document,
        name="agent-applicant-attachment-to-document",
    ),
    path("agent/messages/", views.message_inbox, name="agent-message-inbox"),
    path("agent/applications/", views.application_list, name="agent-application-list"),
    path(
        "agent/applications/<uuid:application_id>/",
        views.application_detail,
        name="agent-application-detail",
    ),
    path(
        "agent/applications/<uuid:application_id>/status/",
        views.application_status,
        name="agent-application-status",
    ),
]
