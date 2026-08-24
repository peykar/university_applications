from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html

from apps.core.admin import AuditAdminMixin

from .models import (
    Lead,
    LeadActivity,
    LeadConversation,
    LeadDocument,
    LeadMessage,
    LeadMessageAttachment,
    LeadPreference,
    LeadProgramInterest,
    LeadProgramInterestSource,
)
from .services.conversion import convert_lead_to_student, finalize_lead
from .services.recommendations import recommend_programs_for_lead


class LeadPreferenceInline(admin.StackedInline):
    model = LeadPreference
    extra = 0
    max_num = 1
    filter_horizontal = (
        "preferred_languages",
        "preferred_cities",
        "preferred_universities",
        "preferred_departments",
    )


class LeadProgramInterestInline(admin.TabularInline):
    model = LeadProgramInterest
    extra = 0
    autocomplete_fields = (
        "program",
        "program_offering",
        "suggested_by",
    )
    fields = (
        "program",
        "program_offering",
        "source",
        "status",
        "suggested_by",
        "suggestion_reason",
        "converted_application",
    )
    readonly_fields = ("converted_application",)


class LeadDocumentInline(admin.TabularInline):
    model = LeadDocument
    extra = 0
    fields = (
        "document_type",
        "name",
        "file",
        "is_verified",
        "verified_by",
        "verified_at",
        "converted_student_document",
    )
    readonly_fields = ("converted_student_document",)


class LeadActivityInline(admin.TabularInline):
    model = LeadActivity
    extra = 0
    fields = (
        "activity_type",
        "description",
        "is_customer_visible",
        "created_at",
        "created_by",
    )
    readonly_fields = (
        "activity_type",
        "description",
        "is_customer_visible",
        "created_at",
        "created_by",
    )
    can_delete = False
    max_num = 0


@admin.register(Lead)
class LeadAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "full_name",
        "user",
        "status",
        "needs_program_recommendation",
        "assigned_to",
        "agent",
        "converted_student",
        "updated_at",
    )
    list_filter = (
        "status",
        "needs_program_recommendation",
        "source",
        "agent",
        "assigned_to",
        "created_at",
    )
    search_fields = (
        "first_name",
        "middle_name",
        "last_name",
        "email",
        "cell",
        "passport_no",
        "user__username",
        "user__email",
    )
    autocomplete_fields = (
        "user",
        "agent",
        "assigned_to",
        "country_of_birth",
        "nationality",
        "country_of_residence",
        "validated_by",
        "converted_student",
    )
    readonly_fields = (
        "validated_by",
        "validated_at",
        "converted_student",
        "converted_at",
        "conversation_link",
    )
    inlines = (
        LeadPreferenceInline,
        LeadProgramInterestInline,
        LeadDocumentInline,
        LeadActivityInline,
    )
    actions = (
        "generate_recommendations",
        "finalize_selected",
        "convert_selected",
    )

    fieldsets = (
        (
            "Ownership & workflow",
            {
                "fields": (
                    "user",
                    "agent",
                    "assigned_to",
                    "status",
                    "source",
                    "needs_program_recommendation",
                    "conversation_link",
                )
            },
        ),
        (
            "Identity",
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "gender",
                    "birthdate",
                    "country_of_birth",
                    "nationality",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "email",
                    "cell",
                    "country_of_residence",
                    "city_of_residence",
                    "address",
                )
            },
        ),
        (
            "Education",
            {
                "fields": (
                    "english_test_type",
                    "english_language_test_score",
                    "high_school_gpa",
                    "high_school_gpa_scale",
                    "educational_background",
                )
            },
        ),
        (
            "Passport",
            {
                "fields": (
                    "passport_no",
                    "passport_issuing_authority",
                    "passport_date_of_issue",
                    "passport_date_of_expiry",
                )
            },
        ),
        (
            "Validation / conversion",
            {
                "fields": (
                    "validated_by",
                    "validated_at",
                    "converted_student",
                    "converted_at",
                )
            },
        ),
        (
            "Internal",
            {
                "fields": (
                    "notes",
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                )
            },
        ),
    )

    @admin.display(description="Applicant", ordering="last_name")
    def full_name(self, obj):
        return str(obj)

    @admin.display(description="Messages")
    def conversation_link(self, obj):
        if not obj.pk:
            return "Save the lead first."
        conversation = getattr(obj, "conversation", None)
        if conversation is None:
            return "Conversation will be created automatically."
        url = reverse("admin:leads_leadmessage_changelist")
        return format_html(
            '<a href="{}?conversation__lead__id__exact={}">Open conversation</a>',
            url,
            obj.pk,
        )

    @admin.action(description="Generate system program recommendations")
    def generate_recommendations(self, request, queryset):
        total = 0
        for lead in queryset:
            total += len(
                recommend_programs_for_lead(
                    lead,
                    limit=10,
                    performed_by=request.user,
                )
            )
        self.message_user(
            request,
            f"{total} recommendation(s) generated.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Finalize / validate selected leads")
    def finalize_selected(self, request, queryset):
        success = 0
        for lead in queryset:
            try:
                finalize_lead(lead, performed_by=request.user)
                success += 1
            except ValidationError as exc:
                self.message_user(
                    request,
                    f"{lead}: {exc}",
                    level=messages.ERROR,
                )
        if success:
            self.message_user(
                request,
                f"{success} lead(s) finalized.",
                level=messages.SUCCESS,
            )

    @admin.action(description="Convert finalized leads to students")
    def convert_selected(self, request, queryset):
        success = 0
        for lead in queryset:
            try:
                convert_lead_to_student(lead, performed_by=request.user)
                success += 1
            except ValidationError as exc:
                self.message_user(
                    request,
                    f"{lead}: {exc}",
                    level=messages.ERROR,
                )
        if success:
            self.message_user(
                request,
                f"{success} lead(s) converted.",
                level=messages.SUCCESS,
            )


@admin.register(LeadProgramInterest)
class LeadProgramInterestAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "lead",
        "program",
        "program_offering",
        "source",
        "status",
        "suggested_by",
        "created_at",
    )
    list_filter = ("source", "status", "created_at")
    search_fields = (
        "lead__first_name",
        "lead__last_name",
        "program__name_en",
        "program__university__name_en",
    )
    autocomplete_fields = (
        "lead",
        "program",
        "program_offering",
        "suggested_by",
    )

    def save_model(self, request, obj, form, change):
        if obj.source == LeadProgramInterestSource.AGENT and not obj.suggested_by_id:
            obj.suggested_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(LeadDocument)
class LeadDocumentAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "lead",
        "document_type",
        "name",
        "is_verified",
        "verified_by",
        "created_at",
    )
    list_filter = ("document_type", "is_verified", "created_at")
    search_fields = (
        "lead__first_name",
        "lead__last_name",
        "name",
    )
    autocomplete_fields = (
        "lead",
        "verified_by",
    )


class LeadMessageAttachmentInline(admin.TabularInline):
    model = LeadMessageAttachment
    extra = 0


@admin.register(LeadMessage)
class LeadMessageAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "lead_name",
        "sender_type",
        "sender",
        "short_body",
        "created_at",
    )
    list_filter = ("sender_type", "created_at")
    search_fields = (
        "conversation__lead__first_name",
        "conversation__lead__last_name",
        "body",
        "sender__username",
        "sender__email",
    )
    autocomplete_fields = ("conversation", "sender")
    inlines = (LeadMessageAttachmentInline,)

    @admin.display(description="Lead")
    def lead_name(self, obj):
        return obj.conversation.lead

    @admin.display(description="Message")
    def short_body(self, obj):
        return obj.body[:100]

    def save_model(self, request, obj, form, change):
        if not obj.sender_id:
            obj.sender = request.user
        if not obj.sender_type:
            obj.sender_type = "staff"
        super().save_model(request, obj, form, change)


@admin.register(LeadConversation)
class LeadConversationAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ("lead", "is_closed", "updated_at")
    list_filter = ("is_closed",)
    search_fields = ("lead__first_name", "lead__last_name")
    autocomplete_fields = ("lead",)


@admin.register(LeadActivity)
class LeadActivityAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "lead",
        "activity_type",
        "is_customer_visible",
        "created_at",
    )
    list_filter = ("activity_type", "is_customer_visible", "created_at")
    search_fields = (
        "lead__first_name",
        "lead__last_name",
        "description",
    )
    readonly_fields = (
        "lead",
        "activity_type",
        "description",
        "is_customer_visible",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
