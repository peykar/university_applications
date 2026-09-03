from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.localization import localized_value
from apps.core.mixins import ActiveMixin, LocalizedNameMixin, LocalizedSlugMixin
from apps.core.models import BaseModel


class Country(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    iso2 = models.CharField(
        max_length=2,
        unique=True,
        help_text=_("ISO 3166-1 alpha-2 country code, for example NL, TR, or IR."),
    )
    iso3 = models.CharField(
        max_length=3,
        unique=True,
        help_text=_("ISO 3166-1 alpha-3 country code, for example NLD, TUR, or IRN."),
    )

    class Meta:
        ordering = ("name_en",)

    def __str__(self):
        return self.localized_name


class Province(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="provinces")

    def __str__(self):
        return self.localized_name


class City(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    province = models.ForeignKey(Province, on_delete=models.PROTECT, related_name="cities")
    description_en = models.TextField(blank=True)
    description_fa = models.TextField(blank=True)
    description_tr = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    seo_title_en = models.CharField(max_length=255, blank=True)
    seo_title_fa = models.CharField(max_length=255, blank=True)
    seo_title_tr = models.CharField(max_length=255, blank=True)
    seo_title_ar = models.CharField(max_length=255, blank=True)
    seo_description_en = models.TextField(blank=True)
    seo_description_fa = models.TextField(blank=True)
    seo_description_tr = models.TextField(blank=True)
    seo_description_ar = models.TextField(blank=True)

    banner = models.ImageField(
        upload_to="cities/banners/",
        blank=True,
        help_text=_("Main banner image used on the public City landing page."),
    )
    banner_alt_en = models.CharField(max_length=255, blank=True)
    banner_alt_fa = models.CharField(max_length=255, blank=True)
    banner_alt_tr = models.CharField(max_length=255, blank=True)
    banner_alt_ar = models.CharField(max_length=255, blank=True)

    @property
    def localized_banner_alt(self):
        return localized_value(self, "banner_alt") or self.localized_name

    @property
    def localized_seo_title(self):
        return localized_value(self, "seo_title")

    @property
    def localized_seo_description(self):
        return localized_value(self, "seo_description")

    def __str__(self):
        return self.localized_name
