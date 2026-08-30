from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction
from django.utils.text import slugify

from apps.core.models import BaseModel


@dataclass(frozen=True)
class SlugChange:
    instance: BaseModel
    field_name: str
    source_field: str
    old_value: str
    new_value: str
    scope: tuple[Any, ...]


# Slug uniqueness is partly a domain/import invariant rather than a DB constraint.
# Keep the rebuild preflight aligned with the catalogue's deterministic lookup scopes.
SCOPE_FIELDS: dict[str, tuple[str, ...]] = {
    "universities.University": (),
    "universities.AcademicUnit": ("university_id",),
    "universities.Department": ("university_id",),
    "universities.ProgramLanguage": (),
    "universities.Program": ("university_id",),
    "geography.Country": (),
    "geography.Province": ("country_id",),
    "geography.City": ("province_id",),
    "content.FAQCategory": (),
}


class Command(BaseCommand):
    help = (
        "Rebuild supported slug fields from their current source names. "
        "Use --dry-run to preview changes without writing."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show the slug changes and collision checks without saving anything.",
        )

    def handle(self, *args, **options):
        dry_run = bool(options["dry_run"])
        changes = self._build_plan()
        self._raise_on_collisions(changes)

        changed = [change for change in changes if change.old_value != change.new_value]
        for change in changed:
            self.stdout.write(
                f"{change.instance._meta.label} {change.instance.pk} "
                f"{change.field_name}: {change.old_value!r} -> {change.new_value!r}"
            )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Dry run complete: {len(changes)} slug values checked; "
                    f"{len(changed)} would change."
                )
            )
            return

        with transaction.atomic():
            by_instance: dict[tuple[str, Any], tuple[BaseModel, set[str]]] = {}
            for change in changes:
                key = (change.instance._meta.label, change.instance.pk)
                instance, fields = by_instance.setdefault(key, (change.instance, set()))
                setattr(instance, change.field_name, "")
                fields.add(change.field_name)

            for instance, fields in by_instance.values():
                # BaseModel.save() regenerates the now-empty fields before persistence.
                instance.save(update_fields=fields)

        self.stdout.write(
            self.style.SUCCESS(
                f"Slug rebuild complete: {len(changes)} slug values rebuilt across "
                f"{len(by_instance)} objects; {len(changed)} values changed."
            )
        )

    def _build_plan(self) -> list[SlugChange]:
        plan: list[SlugChange] = []
        for model in apps.get_models():
            if not issubclass(model, BaseModel) or model._meta.abstract:
                continue
            scope_fields = SCOPE_FIELDS.get(model._meta.label)
            supported = self._supported_slug_fields(model)
            if not supported:
                continue
            if scope_fields is None:
                raise CommandError(
                    f"No rebuild collision scope is defined for {model._meta.label}. "
                    "Define the model's slug scope before rebuilding."
                )

            for instance in model._default_manager.all().iterator():
                scope = tuple(getattr(instance, name) for name in scope_fields)
                for field, source_field in supported:
                    source_value = str(getattr(instance, source_field, "") or "").strip()
                    if not source_value:
                        continue
                    allow_unicode = bool(getattr(field, "allow_unicode", False))
                    generated = slugify(source_value, allow_unicode=allow_unicode)
                    if not generated:
                        raise CommandError(
                            f"Cannot generate {model._meta.label}.{field.name} for "
                            f"{instance.pk} from {source_field}={source_value!r}."
                        )
                    plan.append(
                        SlugChange(
                            instance=instance,
                            field_name=field.name,
                            source_field=source_field,
                            old_value=str(getattr(instance, field.name, "") or ""),
                            new_value=generated,
                            scope=scope,
                        )
                    )
        return plan

    @staticmethod
    def _supported_slug_fields(model) -> list[tuple[models.SlugField, str]]:
        result: list[tuple[models.SlugField, str]] = []
        for field in model._meta.fields:
            if not isinstance(field, models.SlugField):
                continue
            if field.name.startswith("slug_"):
                source = f"name_{field.name.removeprefix('slug_')}"
            elif field.name == "slug":
                source = "name"
            elif field.name == "key":
                source = "name_en"
            else:
                continue
            if any(candidate.name == source for candidate in model._meta.fields):
                result.append((field, source))
        return result

    @staticmethod
    def _raise_on_collisions(changes: list[SlugChange]) -> None:
        grouped: dict[tuple[str, str, tuple[Any, ...], str], list[SlugChange]] = defaultdict(list)
        for change in changes:
            # Localized slugs are display metadata and are not lookup keys in the
            # current catalogue. Collision protection is required for canonical
            # English/conventional slugs and FAQCategory.key.
            if change.field_name not in {"slug_en", "slug", "key"}:
                continue
            key = (
                change.instance._meta.label,
                change.field_name,
                change.scope,
                change.new_value,
            )
            grouped[key].append(change)

        collisions = [items for items in grouped.values() if len(items) > 1]
        if not collisions:
            return

        lines = ["Slug rebuild aborted because generated values collide:"]
        for items in collisions:
            sample = items[0]
            ids = ", ".join(str(item.instance.pk) for item in items)
            lines.append(
                f"- {sample.instance._meta.label}.{sample.field_name} "
                f"{sample.new_value!r} scope={sample.scope!r}: {ids}"
            )
        raise CommandError("\n".join(lines))
