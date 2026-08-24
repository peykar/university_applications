from django.db import models
from django.utils.translation import gettext_lazy as _

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
        ordering = ["name_en"]

    def __str__(self):
        return self.name_en


class Province(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="provinces")

    def __str__(self):
        return self.name_en


class City(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    province = models.ForeignKey(Province, on_delete=models.PROTECT, related_name="cities")

    def __str__(self):
        return self.name_en
