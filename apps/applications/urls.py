from django.urls import path

from . import views

urlpatterns = [
    path(
        "applications/<uuid:application_id>/",
        views.customer_application_detail,
        name="customer-application-detail",
    ),
    path(
        "applications/<uuid:application_id>/requirements/",
        views.customer_application_requirements,
        name="customer-application-requirements",
    ),
    path(
        "applications/<uuid:application_id>/documents/",
        views.customer_application_documents,
        name="customer-application-documents",
    ),
    path(
        "applications/<uuid:application_id>/activity/",
        views.customer_application_activity,
        name="customer-application-activity",
    ),
    path(
        "applications/<uuid:application_id>/messages/",
        views.customer_application_messages,
        name="customer-application-messages",
    ),
    path(
        "applications/<uuid:application_id>/messages/send/",
        views.customer_application_send_message,
        name="customer-application-send-message",
    ),
]
