from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.phone import normalize_phone_number
from apps.core.validators import validate_phone_number


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True, null=True, blank=True)  # type: ignore[assignment]
    cell = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_phone_number],
    )
    cell_verified_at = models.DateTimeField(null=True, blank=True)

    telegram = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="Telegram username without @.",
    )
    telegram_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.cell:
            self.cell = normalize_phone_number(self.cell)
        return super().save(*args, **kwargs)

    @property
    def is_cell_verified(self) -> bool:
        return bool(self.cell and self.cell_verified_at)
