from django.urls import path

from . import views

urlpatterns = [
    path("agent/choose/", views.choose_agent, name="agent-choose"),
    path("agent/switch/", views.switch_agent, name="agent-switch"),
    path("agent/", views.dashboard, name="agent-dashboard"),
    path("agent/applicants/", views.applicant_list, name="agent-applicant-list"),
    path(
        "agent/applicants/<uuid:lead_id>/",
        views.applicant_detail,
        name="agent-applicant-detail",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/profile/",
        views.applicant_section,
        {"section": "profile"},
        name="agent-applicant-profile",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/programs/",
        views.applicant_section,
        {"section": "programs"},
        name="agent-applicant-programs",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/programs/recommend/",
        views.applicant_recommend_program,
        name="agent-applicant-program-recommend",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/programs/<uuid:interest_id>/remove/",
        views.applicant_remove_recommendation,
        name="agent-applicant-program-remove",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/documents/",
        views.applicant_section,
        {"section": "documents"},
        name="agent-applicant-documents",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/applications/",
        views.applicant_section,
        {"section": "applications"},
        name="agent-applicant-applications",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/messages/",
        views.applicant_section,
        {"section": "messages"},
        name="agent-applicant-messages",
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
        "agent/applicants/<uuid:lead_id>/activity/",
        views.applicant_activity,
        name="agent-applicant-activity",
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
        "agent/applicants/<uuid:lead_id>/messages/send/",
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
    path(
        "agent/students/<uuid:student_id>/",
        views.student_detail,
        name="agent-student-detail",
    ),
    path(
        "agent/students/<uuid:student_id>/messages/",
        views.student_message,
        name="agent-student-message",
    ),
    path(
        "agent/students/<uuid:student_id>/documents/upload/",
        views.student_document_upload,
        name="agent-student-document-upload",
    ),
    path(
        "agent/students/<uuid:student_id>/applications/new/",
        views.student_new_application,
        name="agent-student-new-application",
    ),
    path(
        "agent/students/<uuid:student_id>/programs/<uuid:interest_id>/start-application/",
        views.student_start_discussed_application,
        name="agent-student-start-discussed-application",
    ),
    path("agent/applications/", views.application_list, name="agent-application-list"),
    path(
        "agent/applications/<uuid:application_id>/",
        views.application_detail,
        name="agent-application-detail",
    ),
    path(
        "agent/applications/<uuid:application_id>/requirements/",
        views.application_section,
        {"section": "requirements"},
        name="agent-application-requirements",
    ),
    path(
        "agent/applications/<uuid:application_id>/documents/",
        views.application_section,
        {"section": "documents"},
        name="agent-application-documents",
    ),
    path(
        "agent/applications/<uuid:application_id>/activity/",
        views.application_section,
        {"section": "activity"},
        name="agent-application-activity",
    ),
    path(
        "agent/applications/<uuid:application_id>/messages/",
        views.application_section,
        {"section": "messages"},
        name="agent-application-messages",
    ),
    path(
        "agent/applications/<uuid:application_id>/messages/send/",
        views.application_message,
        name="agent-application-message",
    ),
    path(
        "agent/applications/<uuid:application_id>/documents/add/",
        views.application_add_existing_document,
        name="agent-application-add-existing-document",
    ),
    path(
        "agent/applications/<uuid:application_id>/documents/upload/",
        views.application_upload_document,
        name="agent-application-upload-document",
    ),
    path(
        "agent/applications/<uuid:application_id>/status/",
        views.application_status,
        name="agent-application-status",
    ),
]
