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
        "agent/applicants/<uuid:lead_id>/status/",
        views.applicant_status,
        name="agent-applicant-status",
    ),
    path(
        "agent/applicants/<uuid:lead_id>/messages/",
        views.applicant_message,
        name="agent-applicant-message",
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
