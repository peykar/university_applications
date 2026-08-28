from django.contrib import admin

from apps.core.admin import AuditAdminMixin

from .models import Conversation, ConversationParticipantState, Message, MessageAttachment


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ("sender", "sender_role", "body", "edited_at", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("sender",)
    show_change_link = True


class ConversationParticipantStateInline(admin.TabularInline):
    model = ConversationParticipantState
    extra = 0
    fields = ("user", "participant_role", "last_read_message", "last_read_at")
    autocomplete_fields = ("user", "last_read_message")
    show_change_link = True


class MessageAttachmentInline(admin.TabularInline):
    model = MessageAttachment
    extra = 0
    fields = ("file", "original_name", "content_type", "size", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True


@admin.register(Conversation)
class ConversationAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ("agent", "customer", "subject_label", "is_closed", "updated_at")
    list_filter = ("is_closed", "agent", "subject_content_type", "created_at", "updated_at")
    search_fields = (
        "agent__company_name",
        "customer__username",
        "customer__email",
        "customer__first_name",
        "customer__last_name",
    )
    autocomplete_fields = ("agent", "customer")
    list_select_related = ("agent", "customer", "subject_content_type")
    ordering = ("-updated_at",)
    list_per_page = 50
    inlines = (MessageInline, ConversationParticipantStateInline)


@admin.register(Message)
class MessageAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ("conversation", "sender_role", "sender", "body_preview", "created_at")
    list_filter = ("sender_role", "conversation__agent", "created_at", "edited_at")
    search_fields = (
        "body",
        "sender__username",
        "sender__email",
        "conversation__customer__email",
        "conversation__agent__company_name",
    )
    autocomplete_fields = ("conversation", "sender")
    list_select_related = ("conversation", "conversation__agent", "sender")
    date_hierarchy = "created_at"
    list_per_page = 50
    inlines = (MessageAttachmentInline,)

    @admin.display(description="Message")
    def body_preview(self, obj):
        if not obj.body:
            return "—"
        return obj.body if len(obj.body) <= 100 else f"{obj.body[:97]}..."


@admin.register(MessageAttachment)
class MessageAttachmentAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ("original_name", "message", "content_type", "size", "created_at")
    list_filter = ("content_type", "message__conversation__agent", "created_at")
    search_fields = (
        "original_name",
        "message__body",
        "message__conversation__customer__email",
        "message__conversation__agent__company_name",
    )
    autocomplete_fields = ("message",)
    list_select_related = ("message", "message__conversation")
    date_hierarchy = "created_at"
    list_per_page = 50


@admin.register(ConversationParticipantState)
class ConversationParticipantStateAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ("conversation", "user", "participant_role", "last_read_at", "updated_at")
    list_filter = ("participant_role", "conversation__agent", "last_read_at", "updated_at")
    search_fields = (
        "user__username",
        "user__email",
        "conversation__customer__email",
        "conversation__agent__company_name",
    )
    autocomplete_fields = ("conversation", "user", "last_read_message")
    list_select_related = ("conversation", "user", "last_read_message")
    list_per_page = 50
