
from django.contrib import admin

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
    prepopulated_fields = {"slug_en": ("name_en",)}


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
    prepopulated_fields = {"slug_en": ("name_en",)}


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
    prepopulated_fields = {"slug_en": ("name_en",)}

    @admin.display(description="Country")
    def country_name(self, obj):
        return obj.province.country.name_en
