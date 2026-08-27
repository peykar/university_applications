from django.urls import path

from . import views

urlpatterns = [
    path("messages/", views.customer_message_inbox, name="customer-message-inbox"),
    path(
        "messages/<uuid:conversation_id>/",
        views.customer_conversation_detail,
        name="customer-conversation-detail",
    ),
    path(
        "messages/<uuid:conversation_id>/send/",
        views.customer_conversation_send,
        name="customer-conversation-send",
    ),
]
