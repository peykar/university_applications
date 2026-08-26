from django.urls import path

from . import views

urlpatterns = [
    path("applicants/", views.lead_list, name="lead-list"),
    path("applicants/new/", views.lead_create, name="lead-create"),
    path("applicants/<uuid:lead_id>/", views.lead_detail, name="lead-detail"),
    path("applicants/<uuid:lead_id>/edit/", views.lead_edit, name="lead-edit"),
    path(
        "applicants/<uuid:lead_id>/preferences/",
        views.lead_preferences,
        name="lead-preferences",
    ),
    path(
        "applicants/<uuid:lead_id>/documents/",
        views.lead_document_upload,
        name="lead-document-upload",
    ),
    path(
        "applicants/<uuid:lead_id>/documents/<uuid:document_id>/replace/",
        views.lead_document_replace,
        name="lead-document-replace",
    ),
    path(
        "applicants/<uuid:lead_id>/messages/",
        views.lead_send_message,
        name="lead-send-message",
    ),
    path("programs/<slug:slug>/apply/", views.apply_program, name="apply-program"),
]
