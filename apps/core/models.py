from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        populated = self._populate_missing_slugs()
        update_fields = kwargs.get("update_fields")
        if populated and update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | populated
        super().save(*args, **kwargs)

    def clean(self):
        self._populate_missing_slugs()
        super().clean()

    def _populate_missing_slugs(self) -> set[str]:
        """Populate supported blank slug fields from their related name fields.

        Localized ``slug_<locale>`` fields use ``name_<locale>``. A conventional
        ``slug`` uses ``name`` when present, and the existing FAQ category ``key``
        uses ``name_en``. Existing slug values are intentionally never rewritten.
        """
        populated: set[str] = set()
        for field in self._meta.fields:
            if not isinstance(field, models.SlugField):
                continue

            if field.name.startswith("slug_"):
                source_field = f"name_{field.name.removeprefix('slug_')}"
            elif field.name == "slug":
                source_field = "name"
            elif field.name == "key":
                source_field = "name_en"
            else:
                continue

            if not hasattr(self, source_field):
                continue
            current_slug = getattr(self, field.name, "")
            source_name = getattr(self, source_field, "")
            if str(current_slug or "").strip() or not str(source_name or "").strip():
                continue
            allow_unicode = bool(getattr(field, "allow_unicode", False))
            generated = slugify(str(source_name), allow_unicode=allow_unicode)
            if generated:
                setattr(self, field.name, generated)
                populated.add(field.name)
        return populated
