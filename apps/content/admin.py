
from django.contrib import admin
from django.utils import timezone

from apps.core.admin import ActiveActionsMixin, AuditAdminMixin

from .models import ContactSubmission, FAQ, FAQCategory


class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 0
    fields = ("question_en", "sort_order", "is_active")
    show_change_link = True


@admin.register(FAQCategory)
class FAQCategoryAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = (
        "name_en",
        "key",
        "faq_count",
        "sort_order",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = (
        "key",
        "name_en",
        "name_fa",
        "name_tr",
        "name_ar",
    )
    prepopulated_fields = {"key": ("name_en",)}
    inlines = (FAQInline,)


@admin.register(FAQ)
class FAQAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = (
        "question_en",
        "category",
        "sort_order",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "category",
        "is_active",
        "updated_at",
    )
    search_fields = (
        "question_en",
        "question_fa",
        "question_tr",
        "question_ar",
        "answer_en",
        "answer_fa",
        "answer_tr",
        "answer_ar",
    )
    autocomplete_fields = ("category",)


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "subject",
        "is_handled",
        "created_at",
        "handled_at",
    )
    list_filter = (
        "is_handled",
        "created_at",
        "handled_at",
    )
    search_fields = (
        "name",
        "email",
        "phone",
        "subject",
        "message",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    @admin.action(description="Mark selected submissions handled")
    def mark_handled(self, request, queryset):
        queryset.filter(is_handled=False).update(
            is_handled=True,
            handled_at=timezone.now(),
        )

    @admin.action(description="Mark selected submissions unhandled")
    def mark_unhandled(self, request, queryset):
        queryset.update(
            is_handled=False,
            handled_at=None,
        )

    actions = (
        "mark_handled",
        "mark_unhandled",
    )
