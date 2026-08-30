from django.db import models


class LocalizedNameMixin(models.Model):
    name_en = models.CharField(max_length=255)
    name_fa = models.CharField(max_length=255, blank=True)
    name_tr = models.CharField(max_length=255, blank=True)
    name_ar = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True


class LocalizedSlugMixin(models.Model):
    slug_en = models.SlugField(max_length=255)
    slug_fa = models.SlugField(max_length=255, blank=True, allow_unicode=True)
    slug_tr = models.SlugField(max_length=255, blank=True, allow_unicode=True)
    slug_ar = models.SlugField(max_length=255, blank=True, allow_unicode=True)

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
