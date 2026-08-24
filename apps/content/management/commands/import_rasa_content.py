
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.content.models import FAQ, FAQCategory
from apps.core.audit import audited_update_or_create, get_system_user


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CommandError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CommandError(f"Invalid JSON in {path}: {exc}") from exc


class Command(BaseCommand):
    help = "Import FAQ categories and FAQs from a downloaded RasaStudy data directory."

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            nargs="?",
            default="data/rasa",
            help="Directory containing faq_categories.json and faqs.json.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        source = Path(options["source"]).resolve()
        self.system_user = get_system_user()

        categories_payload = load_json(source / "faq_categories.json")
        faqs_payload = load_json(source / "faqs.json")

        categories = (
            categories_payload.get("cats")
            or categories_payload.get("categories")
            or categories_payload.get("faq_categories")
            or categories_payload
        )
        faqs = faqs_payload.get("faqs") or faqs_payload.get("faq") or faqs_payload

        if not isinstance(categories, list):
            raise CommandError("FAQ category payload must contain a list.")

        if not isinstance(faqs, list):
            raise CommandError("FAQ payload must contain a list.")

        category_by_source_id: dict[Any, FAQCategory] = {}
        created_categories = updated_categories = 0
        created_faqs = updated_faqs = 0

        for item in categories:
            category, created = self._upsert_category(item)
            category_by_source_id[item.get("id")] = category

            if created:
                created_categories += 1
            else:
                updated_categories += 1

        for item in faqs:
            category = self._resolve_category(item, category_by_source_id)
            if category is None:
                self.stderr.write(
                    self.style.WARNING(
                        f"Skipping FAQ {item.get('id')}: no category could be resolved."
                    )
                )
                continue

            _, created = self._upsert_faq(item, category)
            if created:
                created_faqs += 1
            else:
                updated_faqs += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Rasa content import complete. "
                f"FAQ categories created={created_categories}, updated={updated_categories}; "
                f"FAQs created={created_faqs}, updated={updated_faqs}."
            )
        )

    def _upsert_category(self, item: dict[str, Any]) -> tuple[FAQCategory, bool]:
        key = str(
            item.get("key")
            or item.get("slug")
            or slugify(str(item.get("name_en") or item.get("name_fa") or item.get("id") or "faq"))
        )

        defaults = {
            "name_en": str(item.get("name_en") or item.get("title_en") or key),
            "name_fa": str(item.get("name_fa") or item.get("title_fa") or ""),
            "name_tr": str(item.get("name_tr") or item.get("title_tr") or ""),
            "name_ar": str(item.get("name_ar") or item.get("title_ar") or ""),
            "icon": str(item.get("icon") or ""),
            "color": str(item.get("color") or ""),
            "sort_order": int(item.get("sort_order") or item.get("order") or 0),
            "is_active": bool(item.get("active", item.get("is_active", True))),
        }

        return audited_update_or_create(
            FAQCategory.objects,
            lookup={"key": key},
            defaults=defaults,
            actor=self.system_user,
        )

    def _resolve_category(
        self,
        item: dict[str, Any],
        category_by_source_id: dict[Any, FAQCategory],
    ) -> FAQCategory | None:
        category_id = item.get("category_id") or item.get("cat_id")
        if category_id in category_by_source_id:
            return category_by_source_id[category_id]

        category_key = item.get("category_key") or item.get("cat_key")
        if category_key:
            return FAQCategory.objects.filter(key=str(category_key)).first()

        if len(category_by_source_id) == 1:
            return next(iter(category_by_source_id.values()))

        return None

    def _upsert_faq(self, item: dict[str, Any], category: FAQCategory) -> tuple[FAQ, bool]:
        question_en = str(item.get("question_en") or item.get("question") or "").strip()
        question_fa = str(item.get("question_fa") or "").strip()
        question_tr = str(item.get("question_tr") or "").strip()
        question_ar = str(item.get("question_ar") or "").strip()

        canonical_question = question_en or question_fa or question_tr or question_ar
        if not canonical_question:
            raise CommandError(f"FAQ {item.get('id')} has no question text.")

        defaults = {
            "question_en": question_en or canonical_question,
            "question_fa": question_fa,
            "question_tr": question_tr,
            "question_ar": question_ar,
            "answer_en": str(item.get("answer_en") or item.get("answer") or ""),
            "answer_fa": str(item.get("answer_fa") or ""),
            "answer_tr": str(item.get("answer_tr") or ""),
            "answer_ar": str(item.get("answer_ar") or ""),
            "sort_order": int(item.get("sort_order") or item.get("order") or 0),
            "is_active": bool(item.get("active", item.get("is_active", True))),
        }

        return audited_update_or_create(
            FAQ.objects,
            lookup={
                "category": category,
                "question_en": question_en or canonical_question,
            },
            defaults=defaults,
            actor=self.system_user,
        )
