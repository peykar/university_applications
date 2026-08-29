from collections.abc import Sequence
from decimal import Decimal
from typing import ClassVar, cast

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html

from apps.core.admin import ActiveActionsMixin, AuditAdminMixin

from .models import (
    AcademicUnit,
    AcademicYear,
    Department,
    Program,
    ProgramInstructionLanguage,
    ProgramLanguage,
    ProgramOffering,
    Semester,
    University,
    UniversityCatalogueSource,
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


class ProgramOfferingAdminForm(forms.ModelForm):
    class Meta:
        model = ProgramOffering
        fields = (
            "program",
            "academic_year",
            "semester",
            "fee_basis",
            "currency",
            "tuition",
            "tuition_discount_percentage",
            "tuition_discounted",
            "cash_discount_percentage",
            "tuition_cash",
            "tuition_annual_installment",
            "deposit",
            "preparatory_tuition",
            "preparation_included",
            "quota",
            "deadline",
            "valid_from",
            "valid_until",
            "notes",
            "source",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        raw_source_field = self.fields.get("source")
        if raw_source_field is None:
            return
        source_field = cast(forms.ModelChoiceField, raw_source_field)
        university_id = None
        if self.instance and self.instance.program_id:
            university_id = self.instance.program.university_id
        elif self.data.get("program"):
            university_id = (
                Program.objects.filter(pk=str(self.data.get("program")))
                .values_list("university_id", flat=True)
                .first()
            )
        source_field.queryset = (
            UniversityCatalogueSource.objects.filter(university_id=university_id)
            if university_id
            else UniversityCatalogueSource.objects.none()
        )


class ProgramInstructionLanguageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        rows = [
            form.cleaned_data
            for form in self.forms
            if hasattr(form, "cleaned_data")
            and form.cleaned_data
            and not form.cleaned_data.get("DELETE")
            and form.cleaned_data.get("language")
        ]
        if not rows:
            raise ValidationError("A program must have at least one instruction language.")
        percentages = [row.get("percentage") for row in rows]
        populated = [value for value in percentages if value is not None]
        if populated and (len(populated) != len(rows) or sum(populated, Decimal("0")) != 100):
            raise ValidationError(
                "When percentages are supplied, all instruction-language percentages "
                "must be supplied and total 100%."
            )


class ProgramInstructionLanguageInline(admin.TabularInline):
    model = ProgramInstructionLanguage
    formset = ProgramInstructionLanguageInlineFormSet
    extra = 1
    fields = ("language", "percentage", "is_primary")
    autocomplete_fields = ("language",)


class ProgramOfferingInline(admin.StackedInline):
    model = ProgramOffering
    form = ProgramOfferingAdminForm
    extra = 0
    fields = (
        "academic_year",
        "semester",
        "fee_basis",
        "currency",
        "tuition",
        "tuition_discount_percentage",
        "tuition_discounted",
        "cash_discount_percentage",
        "tuition_cash",
        "tuition_annual_installment",
        "deposit",
        "preparatory_tuition",
        "preparation_included",
        "quota",
        "deadline",
        "valid_from",
        "valid_until",
        "source",
        "notes",
        "is_active",
    )
    autocomplete_fields = ("academic_year", "semester", "source")
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
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug_en": ("name_en",)}
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

    actions: Sequence[str] = (
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
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug_en": ("name_en",)}


@admin.register(AcademicUnit)
class AcademicUnitAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = ("name_en", "university", "unit_type", "is_active")
    list_filter = ("unit_type", "university", "is_active")
    search_fields = (
        "name_en",
        "name_fa",
        "name_tr",
        "name_ar",
        "university__name_en",
    )
    autocomplete_fields = ("university",)
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug_en": ("name_en",)}


@admin.register(ProgramLanguage)
class ProgramLanguageAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = ("name_en", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name_en", "name_fa", "name_tr", "name_ar")
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug_en": ("name_en",)}


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
        "academic_unit",
        "department",
        "degree",
        "study_mode",
        "language_summary",
        "duration_summary",
        "listing_priority",
        "is_active",
    )
    list_filter = (
        "degree",
        "study_mode",
        "instruction_languages",
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
        "academic_unit__name_en",
        "department__name_en",
    )
    autocomplete_fields = (
        "university",
        "academic_unit",
        "department",
    )
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug_en": ("name_en",)}
    ordering = ("-listing_priority", "university__name_en", "name_en")
    inlines = (ProgramInstructionLanguageInline, ProgramOfferingInline)
    fieldsets = (
        (
            "Academic identity",
            {
                "fields": (
                    "university",
                    "academic_unit",
                    "department",
                    "name_en",
                    "name_fa",
                    "name_tr",
                    "name_ar",
                    "slug_en",
                    "slug_fa",
                    "slug_tr",
                    "slug_ar",
                    "degree",
                    "thesis_type",
                    "study_mode",
                    "duration_months",
                    "listing_priority",
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
            "Internal",
            {
                "classes": ("collapse",),
                "fields": ("internal_notes",),
                "description": ("Staff/import notes only. This content is never customer-facing."),
            },
        ),
    )

    @admin.display(description="Instruction languages")
    def language_summary(self, obj):
        return obj.instruction_language_display or "—"

    @admin.display(description="Duration")
    def duration_summary(self, obj):
        return obj.duration_display or "—"


@admin.register(ProgramOffering)
class ProgramOfferingAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    form = ProgramOfferingAdminForm
    list_display = (
        "program",
        "academic_year",
        "semester",
        "currency",
        "tuition",
        "tuition_discounted",
        "tuition_cash",
        "deposit",
        "quota",
        "deadline",
        "is_active",
    )
    list_filter = (
        "academic_year",
        "semester",
        "fee_basis",
        "currency",
        "preparation_included",
        "is_active",
        "program__university",
    )
    search_fields = (
        "program__name_en",
        "program__university__name_en",
        "source__title",
        "notes",
    )
    autocomplete_fields = (
        "program",
        "academic_year",
        "semester",
        "source",
    )
    fieldsets = (
        (
            "Intake",
            {"fields": ("program", "academic_year", "semester", "is_active")},
        ),
        (
            "Pricing",
            {
                "fields": (
                    "fee_basis",
                    "currency",
                    "tuition",
                    "tuition_discount_percentage",
                    "tuition_discounted",
                    "cash_discount_percentage",
                    "tuition_cash",
                    "tuition_annual_installment",
                    "deposit",
                    "preparatory_tuition",
                    "preparation_included",
                )
            },
        ),
        (
            "Availability and provenance",
            {
                "fields": (
                    "quota",
                    "deadline",
                    "valid_from",
                    "valid_until",
                    "source",
                    "notes",
                )
            },
        ),
    )


@admin.register(UniversityCatalogueSource)
class UniversityCatalogueSourceAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "university",
        "received_at",
        "academic_year",
        "valid_from",
        "valid_until",
    )
    list_filter = ("university", "academic_year", "received_at")
    search_fields = ("title", "university__name_en", "notes")
    autocomplete_fields = ("university", "academic_year", "recorded_by")
