
from django.contrib import admin
from django.utils.html import format_html

from apps.core.admin import ActiveActionsMixin, AuditAdminMixin

from .models import (
    AcademicYear,
    Department,
    Program,
    ProgramLanguage,
    ProgramOffering,
    Semester,
    University,
    UniversityMedia,
)


class UniversityMediaInline(admin.TabularInline):
    model = UniversityMedia
    extra = 0
    fields = ("image", "preview", "title", "sort_order", "is_active")
    readonly_fields = ("preview",)

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.pk or not obj.image:
            return "—"
        return format_html(
            '<img src="{}" style="max-height:70px;max-width:120px;" />',
            obj.image.url,
        )


class ProgramOfferingInline(admin.TabularInline):
    model = ProgramOffering
    extra = 0
    fields = (
        "academic_year",
        "semester",
        "currency",
        "tuition",
        "tuition_discounted",
        "quota",
        "deadline",
        "is_active",
    )
    autocomplete_fields = ("academic_year", "semester")
    show_change_link = True


@admin.register(University)
class UniversityAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = (
        "name_en",
        "city",
        "university_type",
        "is_yok_recognized",
        "is_moe_approved",
        "is_moh_approved",
        "has_erasmus",
        "has_dormitory",
        "listing_priority",
        "is_featured",
        "is_active",
    )
    list_filter = (
        "university_type",
        "is_yok_recognized",
        "is_moe_approved",
        "is_moh_approved",
        "has_erasmus",
        "has_dormitory",
        "is_featured",
        "is_active",
        "city__province__country",
    )
    search_fields = (
        "name_en",
        "name_fa",
        "name_tr",
        "name_ar",
        "slug_en",
        "city__name_en",
        "city__province__name_en",
        "city__province__country__name_en",
    )
    autocomplete_fields = ("city",)
    prepopulated_fields = {"slug_en": ("name_en",)}
    ordering = ("-listing_priority", "name_en")
    inlines = (UniversityMediaInline,)
    readonly_fields = ("logo_preview", "banner_preview")

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "name_en",
                    "name_fa",
                    "name_tr",
                    "name_ar",
                    "slug_en",
                    "slug_fa",
                    "slug_tr",
                    "slug_ar",
                    "university_type",
                    "city",
                    "website",
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "logo",
                    "logo_preview",
                    "banner",
                    "banner_preview",
                )
            },
        ),
        (
            "Recognition and features",
            {
                "fields": (
                    "is_yok_recognized",
                    "is_moe_approved",
                    "is_moh_approved",
                    "has_erasmus",
                    "has_dormitory",
                )
            },
        ),
        (
            "Ranking and listing",
            {
                "fields": (
                    "ranking_qs",
                    "ranking_the",
                    "ranking_arwu",
                    "ranking_urap",
                    "listing_priority",
                    "is_featured",
                    "is_active",
                )
            },
        ),
        (
            "Descriptions",
            {
                "classes": ("collapse",),
                "fields": (
                    "description_en",
                    "description_fa",
                    "description_tr",
                    "description_ar",
                ),
            },
        ),
        (
            "Audit",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                ),
            },
        ),
    )

    @admin.display(description="Logo")
    def logo_preview(self, obj):
        if not obj.logo:
            return "—"
        return format_html(
            '<img src="{}" style="max-height:80px;max-width:180px;" />',
            obj.logo.url,
        )

    @admin.display(description="Banner")
    def banner_preview(self, obj):
        if not obj.banner:
            return "—"
        return format_html(
            '<img src="{}" style="max-height:100px;max-width:260px;" />',
            obj.banner.url,
        )

    @admin.action(description="Feature selected universities")
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Unfeature selected universities")
    def mark_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)

    actions = (
        "mark_active",
        "mark_inactive",
        "mark_featured",
        "mark_unfeatured",
    )


@admin.register(UniversityMedia)
class UniversityMediaAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = ("university", "title", "sort_order", "is_active")
    list_filter = ("is_active", "university")
    search_fields = ("title", "university__name_en")
    autocomplete_fields = ("university",)


@admin.register(Department)
class DepartmentAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = ("name_en", "university", "is_active")
    list_filter = ("university", "is_active")
    search_fields = (
        "name_en",
        "name_fa",
        "name_tr",
        "name_ar",
        "university__name_en",
    )
    autocomplete_fields = ("university",)
    prepopulated_fields = {"slug_en": ("name_en",)}


@admin.register(ProgramLanguage)
class ProgramLanguageAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = ("name_en", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name_en", "name_fa", "name_tr", "name_ar")
    prepopulated_fields = {"slug_en": ("name_en",)}


@admin.register(AcademicYear)
class AcademicYearAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = ("name_en", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name_en", "name_fa", "name_tr", "name_ar")


@admin.register(Semester)
class SemesterAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = ("name_en", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name_en", "name_fa", "name_tr", "name_ar")


@admin.register(Program)
class ProgramAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = (
        "name_en",
        "university",
        "department",
        "degree",
        "program_language",
        "duration",
        "listing_priority",
        "is_active",
    )
    list_filter = (
        "degree",
        "program_language",
        "university",
        "is_active",
    )
    search_fields = (
        "name_en",
        "name_fa",
        "name_tr",
        "name_ar",
        "slug_en",
        "university__name_en",
        "department__name_en",
    )
    autocomplete_fields = (
        "university",
        "department",
        "program_language",
    )
    prepopulated_fields = {"slug_en": ("name_en",)}
    ordering = ("-listing_priority", "university__name_en", "name_en")
    inlines = (ProgramOfferingInline,)


@admin.register(ProgramOffering)
class ProgramOfferingAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = (
        "program",
        "academic_year",
        "semester",
        "currency",
        "tuition",
        "tuition_discounted",
        "quota",
        "deadline",
        "is_active",
    )
    list_filter = (
        "academic_year",
        "semester",
        "currency",
        "is_active",
        "program__university",
    )
    search_fields = (
        "program__name_en",
        "program__university__name_en",
    )
    autocomplete_fields = (
        "program",
        "academic_year",
        "semester",
    )
