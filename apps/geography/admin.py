from collections.abc import Sequence
from typing import ClassVar

from django.contrib import admin
from django.utils.html import format_html

from apps.core.admin import ActiveActionsMixin, AuditAdminMixin

from .models import City, Country, Province


@admin.register(Country)
class CountryAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = ("name_en", "iso2", "iso3", "is_active")
    list_filter = ("is_active",)
    search_fields = (
        "name_en",
        "name_fa",
        "name_tr",
        "name_ar",
        "iso2",
        "iso3",
    )
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug_en": ("name_en",)}


@admin.register(Province)
class ProvinceAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = ("name_en", "country", "is_active")
    list_filter = ("country", "is_active")
    search_fields = (
        "name_en",
        "name_fa",
        "name_tr",
        "name_ar",
    )
    autocomplete_fields = ("country",)
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug_en": ("name_en",)}


@admin.register(City)
class CityAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = ("name_en", "province", "country_name", "is_active")
    list_filter = ("province__country", "is_active")
    search_fields = (
        "name_en",
        "name_fa",
        "name_tr",
        "name_ar",
        "province__name_en",
        "province__country__name_en",
    )
    autocomplete_fields = ("province",)
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug_en": ("name_en",)}
    readonly_fields = ("banner_preview",)
    fieldsets = (
        (None, {"fields": ("province", "is_active")}),
        ("Names", {"fields": ("name_en", "name_fa", "name_tr", "name_ar")}),
        ("Slugs", {"fields": ("slug_en", "slug_fa", "slug_tr", "slug_ar")}),
        (
            "Media",
            {
                "fields": (
                    "banner",
                    "banner_preview",
                    "banner_alt_en",
                    "banner_alt_fa",
                    "banner_alt_tr",
                    "banner_alt_ar",
                )
            },
        ),
        (
            "Descriptions",
            {"fields": ("description_en", "description_fa", "description_tr", "description_ar")},
        ),
        (
            "SEO",
            {
                "fields": (
                    "seo_title_en",
                    "seo_description_en",
                    "seo_title_fa",
                    "seo_description_fa",
                    "seo_title_tr",
                    "seo_description_tr",
                    "seo_title_ar",
                    "seo_description_ar",
                )
            },
        ),
    )

    @admin.display(description="Banner")
    def banner_preview(self, obj):
        if not obj.banner:
            return "—"
        return format_html(
            '<img src="{}" style="max-height:120px;max-width:320px;" alt="" />',
            obj.banner.url,
        )

    @admin.display(description="Country")
    def country_name(self, obj):
        return obj.province.country.name_en
