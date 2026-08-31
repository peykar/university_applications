from collections.abc import Sequence
from decimal import Decimal
from typing import ClassVar, cast

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html, format_html_join

from apps.core.admin import ActiveActionsMixin, AuditAdminMixin

from .models import (
    AcademicUnit,
    AcademicYear,
    Department,
    Intake,
    OfferingFee,
    OfferingFeeType,
    Program,
    ProgramInstructionLanguage,
    ProgramLanguage,
    ProgramOffering,
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
            "intake",
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


class OfferingFeeInline(admin.TabularInline):
    model = OfferingFee
    extra = 0
    fields = (
        "fee_type",
        "label",
        "language",
        "currency",
        "amount",
        "percentage",
        "basis",
        "notes",
        "is_active",
    )
    autocomplete_fields = ("language",)


class StructuredFeeSummaryMixin:
    FEE_TYPE_DISPLAY_ORDER: ClassVar[dict[str, int]] = {
        OfferingFeeType.TUITION: 10,
        OfferingFeeType.DISCOUNTED_TUITION: 20,
        OfferingFeeType.ADVANCE_PAYMENT: 30,
        OfferingFeeType.CASH_PAYMENT: 40,
        OfferingFeeType.INSTALLMENT_TOTAL: 50,
        OfferingFeeType.DEPOSIT: 60,
        OfferingFeeType.PREPARATORY: 70,
        OfferingFeeType.APPLICATION: 80,
        OfferingFeeType.REGISTRATION: 90,
        OfferingFeeType.OTHER: 100,
    }

    @admin.display(description="Structured fees (Catalogue v3)")
    def structured_fee_summary(self, obj):
        if not obj or not obj.pk:
            return "Save the offering first, then add structured fee rows."

        fees = list(obj.fees.select_related("language"))
        fees.sort(
            key=lambda fee: (
                self.FEE_TYPE_DISPLAY_ORDER.get(fee.fee_type, 999),
                fee.language.name_en if fee.language_id else "",
                str(fee.id),
            )
        )
        if not fees:
            return (
                "No structured fees yet. Add them in the Offering fees section on the "
                "offering change page."
            )

        rows = []
        for fee in fees:
            values = []
            if fee.amount is not None:
                values.append(f"{fee.currency} {fee.amount:,.2f}")
            if fee.percentage is not None:
                values.append(f"{fee.percentage:g}%")
            value = " + ".join(values)
            language_obj = fee.language if fee.language_id else None
            language = language_obj.name_en if language_obj is not None else "—"
            label = fee.label or "—"
            status = "active" if fee.is_active else "inactive"
            rows.append(
                (
                    fee.get_fee_type_display(),
                    label,
                    language,
                    value,
                    fee.get_basis_display(),
                    status,
                )
            )

        return format_html(
            '<table style="width:100%;max-width:900px">'
            "<thead><tr>"
            '<th style="text-align:left">Type</th>'
            '<th style="text-align:left">Source label</th>'
            '<th style="text-align:left">Language</th>'
            '<th style="text-align:left">Value</th>'
            '<th style="text-align:left">Basis</th>'
            '<th style="text-align:left">Status</th>'
            "</tr></thead><tbody>{}</tbody></table>",
            format_html_join(
                "",
                "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>",
                rows,
            ),
        )


class ProgramOfferingInline(StructuredFeeSummaryMixin, admin.StackedInline):
    model = ProgramOffering
    form = ProgramOfferingAdminForm
    extra = 0
    readonly_fields = ("structured_fee_summary",)
    fieldsets = (
        (
            "Canonical offering",
            {
                "fields": (
                    "academic_year",
                    "intake",
                    "preparation_included",
                    "is_active",
                )
            },
        ),
        (
            "Structured fees",
            {
                "fields": ("structured_fee_summary",),
                "description": (
                    "Catalogue v3 fees are canonical. Use the Change link on this offering "
                    "to add or edit individual OfferingFee rows."
                ),
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
    autocomplete_fields = ("academic_year", "intake", "source")
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
class ProgramOfferingAdmin(
    StructuredFeeSummaryMixin, AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin
):
    form = ProgramOfferingAdminForm
    inlines = (OfferingFeeInline,)
    readonly_fields = ("structured_fee_summary",)
    list_display = (
        "program",
        "academic_year",
        "intake",
        "structured_fee_count",
        "quota",
        "deadline",
        "is_active",
    )
    list_filter = (
        "academic_year",
        "intake",
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
        "intake",
        "source",
    )
    fieldsets = (
        (
            "Canonical offering",
            {
                "fields": (
                    "program",
                    "academic_year",
                    "intake",
                    "preparation_included",
                    "is_active",
                )
            },
        ),
        (
            "Structured fees",
            {
                "fields": ("structured_fee_summary",),
                "description": (
                    "Catalogue v3 OfferingFee rows are canonical. Add or edit them in the "
                    "Offering fees inline below this form."
                ),
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

    @admin.display(description="Structured fees")
    def structured_fee_count(self, obj):
        return obj.fees.count()


@admin.register(OfferingFee)
class OfferingFeeAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = (
        "offering",
        "fee_type",
        "label",
        "language",
        "currency",
        "amount",
        "percentage",
        "basis",
        "is_active",
    )
    list_filter = (
        "fee_type",
        "basis",
        "currency",
        "language",
        "is_active",
        "offering__program__university",
    )
    search_fields = (
        "offering__program__name_en",
        "offering__program__university__name_en",
        "label",
        "notes",
    )
    autocomplete_fields = ("offering", "language")


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


@admin.register(Intake)
class IntakeAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = (
        "name_en",
        "university",
        "academic_year",
        "start_date",
        "application_deadline",
        "is_active",
    )
    list_filter = ("academic_year", "is_active", "university")
    search_fields = ("name_en", "university__name_en", "academic_year__name_en")
    autocomplete_fields = ("university", "academic_year")
