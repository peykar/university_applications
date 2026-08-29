from django.urls import path

from . import views

urlpatterns = [
    path("applicants/", views.lead_list, name="lead-list"),
    path("applicants/new/", views.lead_create, name="lead-create"),
    path("applicants/<uuid:lead_id>/", views.lead_detail, name="lead-detail"),
    path("applicants/<uuid:lead_id>/profile/", views.lead_profile, name="lead-profile"),
    path("applicants/<uuid:lead_id>/programs/", views.lead_programs, name="lead-programs"),
    path(
        "applicants/<uuid:lead_id>/programs/<uuid:interest_id>/intake/",
        views.lead_program_intake_update,
        name="lead-program-intake-update",
    ),
    path(
        "applicants/<uuid:lead_id>/programs/<uuid:interest_id>/remove/",
        views.lead_program_remove,
        name="lead-program-remove",
    ),
    path("applicants/<uuid:lead_id>/documents/", views.lead_documents, name="lead-documents"),
    path(
        "applicants/<uuid:lead_id>/applications/",
        views.lead_applications,
        name="lead-applications",
    ),
    path("applicants/<uuid:lead_id>/messages/", views.lead_messages, name="lead-messages"),
    path("applicants/<uuid:lead_id>/edit/", views.lead_edit, name="lead-edit"),
    path(
        "applicants/<uuid:lead_id>/preferences/",
        views.lead_preferences,
        name="lead-preferences",
    ),
    path(
        "applicants/<uuid:lead_id>/documents/upload/",
        views.lead_document_upload,
        name="lead-document-upload",
    ),
    path(
        "applicants/<uuid:lead_id>/documents/<uuid:document_id>/replace/",
        views.lead_document_replace,
        name="lead-document-replace",
    ),
    path(
        "applicants/<uuid:lead_id>/messages/send/",
        views.lead_send_message,
        name="lead-send-message",
    ),
    path("programs/<slug:slug>/apply/", views.apply_program, name="apply-program"),
]
