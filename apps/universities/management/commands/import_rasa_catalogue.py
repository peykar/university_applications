
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from mimetypes import guess_type
from pathlib import Path
from typing import Any

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.core.audit import audited_get_or_create, audited_update_or_create, get_system_user
from apps.geography.models import City, Country, Province
from apps.universities.models import (
    AcademicYear,
    Department,
    DegreeType,
    Program,
    ProgramLanguage,
    ProgramOffering,
    Semester,
    University,
    UniversityMedia,
    UniversityType,
)


LANGUAGE_MAP = {
    "english": {
        "name_en": "English",
        "name_fa": "انگلیسی",
        "name_tr": "İngilizce",
        "name_ar": "الإنجليزية",
    },
    "turkish": {
        "name_en": "Turkish",
        "name_fa": "ترکی",
        "name_tr": "Türkçe",
        "name_ar": "التركية",
    },
    "arabic": {
        "name_en": "Arabic",
        "name_fa": "عربی",
        "name_tr": "Arapça",
        "name_ar": "العربية",
    },
    "german": {
        "name_en": "German",
        "name_fa": "آلمانی",
        "name_tr": "Almanca",
        "name_ar": "الألمانية",
    },
}

DEGREE_MAP = {
    "associate": DegreeType.ASSOCIATE,
    "bachelor": DegreeType.BACHELOR,
    "master": DegreeType.MASTER,
    "master_thesis": DegreeType.MASTER,
    "master_non_thesis": DegreeType.MASTER,
    "phd": DegreeType.PHD,
}

THESIS_MAP = {
    "master_thesis": "thesis",
    "master_non_thesis": "non_thesis",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CommandError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CommandError(f"Invalid JSON in {path}: {exc}") from exc


def as_decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def normalize_slug(value: str | None, fallback: str) -> str:
    candidate = (value or "").strip()
    if candidate:
        return slugify(candidate, allow_unicode=True) or fallback
    return fallback



def load_asset_manifest(source: Path) -> list[dict[str, Any]]:
    path = source / "assets_manifest.json"
    if not path.exists():
        return []

    payload = load_json(path)
    if not isinstance(payload, list):
        raise CommandError("assets_manifest.json must contain a list.")
    return payload


def build_asset_index(
    source: Path,
    manifest: list[dict[str, Any]],
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    index: dict[tuple[str, str], list[dict[str, Any]]] = {}

    for asset in manifest:
        local_path = asset.get("local_path")
        if not local_path:
            continue

        absolute_path = source / str(local_path)
        if not absolute_path.exists():
            continue

        for ref in asset.get("references") or []:
            object_type = str(ref.get("object_type") or "")
            object_id = ref.get("object_id")
            if not object_type or object_id is None:
                continue

            key = (object_type, str(object_id))
            index.setdefault(key, []).append(
                {
                    **asset,
                    "absolute_path": absolute_path,
                    "source_field": str(ref.get("source_field") or ""),
                    "json_path": str(ref.get("json_path") or ""),
                }
            )

    return index


class Command(BaseCommand):
    help = (
        "Import RasaStudy universities/programs from a downloaded data/rasa directory. "
        "The command is idempotent."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            nargs="?",
            default="data/rasa",
            help="Directory containing universities.json and programs.json (default: data/rasa).",
        )
        parser.add_argument(
            "--academic-year",
            default="2026-2027",
            help="Academic year used for imported ProgramOffering rows.",
        )
        parser.add_argument(
            "--semester",
            default="Fall",
            help="Semester used for imported ProgramOffering rows.",
        )
        parser.add_argument(
            "--country",
            default="TR",
            help="ISO2 code used for imported universities (default: TR).",
        )
        parser.add_argument(
            "--skip-offerings",
            action="store_true",
            help="Import universities/programs but do not create ProgramOffering records.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        source = Path(options["source"]).resolve()
        self.system_user = get_system_user()
        universities_payload = load_json(source / "universities.json")
        programs_payload = load_json(source / "programs.json")

        universities = universities_payload.get("universities", universities_payload)
        programs = programs_payload.get("programs", programs_payload)

        if not isinstance(universities, list):
            raise CommandError("universities.json must contain a list or {'universities': [...]}.")

        if not isinstance(programs, list):
            raise CommandError("programs.json must contain a list or {'programs': [...]}.")

        country = self._get_country(options["country"])
        academic_year = self._get_academic_year(options["academic_year"])
        semester = self._get_semester(options["semester"])

        asset_manifest = load_asset_manifest(source)
        asset_index = build_asset_index(source, asset_manifest)

        university_by_rasa_id: dict[Any, University] = {}
        university_by_slug: dict[str, University] = {}

        university_created = university_updated = 0
        program_created = program_updated = 0
        offering_created = offering_updated = 0

        for item in universities:
            university, created = self._upsert_university(item, country, asset_index)
            university_by_rasa_id[item.get("id")] = university
            if item.get("slug"):
                university_by_slug[str(item["slug"])] = university

            if created:
                university_created += 1
            else:
                university_updated += 1

        for item in programs:
            university = self._resolve_program_university(
                item,
                university_by_rasa_id=university_by_rasa_id,
                university_by_slug=university_by_slug,
            )
            if university is None:
                self.stderr.write(
                    self.style.WARNING(
                        f"Skipping program {item.get('id')}: could not resolve university."
                    )
                )
                continue

            program, created = self._upsert_program(item, university)
            if created:
                program_created += 1
            else:
                program_updated += 1

            if options["skip_offerings"]:
                continue

            offering, offering_was_created = self._upsert_offering(
                item,
                program,
                academic_year,
                semester,
            )
            if offering is None:
                continue

            if offering_was_created:
                offering_created += 1
            else:
                offering_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Rasa catalogue import complete. "
                f"Universities created={university_created}, updated={university_updated}; "
                f"Programs created={program_created}, updated={program_updated}; "
                f"Offerings created={offering_created}, updated={offering_updated}."
            )
        )

    def _get_country(self, iso2: str) -> Country:
        try:
            return Country.objects.get(iso2=iso2.upper())
        except Country.DoesNotExist as exc:
            raise CommandError(
                f"Country {iso2!r} does not exist. Run `python manage.py populate_countries` first."
            ) from exc

    def _get_academic_year(self, name: str) -> AcademicYear:
        academic_year, _ = audited_get_or_create(
            AcademicYear.objects,
            lookup={"name_en": name},
            defaults={
                "name_fa": name,
                "name_tr": name,
                "name_ar": name,
                "is_active": True,
            },
            actor=self.system_user,
        )
        return academic_year

    def _get_semester(self, name: str) -> Semester:
        semester, _ = audited_get_or_create(
            Semester.objects,
            lookup={"name_en": name},
            defaults={
                "name_fa": name,
                "name_tr": name,
                "name_ar": name,
                "is_active": True,
            },
            actor=self.system_user,
        )
        return semester

    def _get_city(self, country: Country, city_name: str) -> City:
        province, _ = audited_get_or_create(
            Province.objects,
            lookup={"country": country, "name_en": city_name},
            defaults={
                "name_fa": city_name,
                "name_tr": city_name,
                "name_ar": city_name,
                "slug_en": normalize_slug(city_name, "province"),
                "slug_fa": normalize_slug(city_name, "province"),
                "slug_tr": normalize_slug(city_name, "province"),
                "slug_ar": normalize_slug(city_name, "province"),
                "is_active": True,
            },
            actor=self.system_user,
        )

        city, _ = audited_get_or_create(
            City.objects,
            lookup={"province": province, "name_en": city_name},
            defaults={
                "name_fa": city_name,
                "name_tr": city_name,
                "name_ar": city_name,
                "slug_en": normalize_slug(city_name, "city"),
                "slug_fa": normalize_slug(city_name, "city"),
                "slug_tr": normalize_slug(city_name, "city"),
                "slug_ar": normalize_slug(city_name, "city"),
                "is_active": True,
            },
            actor=self.system_user,
        )
        return city

    def _upsert_university(
        self,
        item: dict[str, Any],
        country: Country,
        asset_index: dict[tuple[str, str], list[dict[str, Any]]],
    ) -> tuple[University, bool]:
        slug = str(item.get("slug") or item.get("name_en") or item.get("id") or "university")
        city_name = str(
            item.get("city_en")
            or item.get("city_tr")
            or item.get("city_fa")
            or "Unknown"
        )
        city = self._get_city(country, city_name)

        university_type = (
            UniversityType.PRIVATE
            if item.get("type") == "private"
            else UniversityType.PUBLIC
        )

        defaults = {
            "name_en": str(item.get("name_en") or slug),
            "name_fa": str(item.get("name_fa") or ""),
            "name_tr": str(item.get("name_tr") or ""),
            "name_ar": str(item.get("name_ar") or ""),
            "slug_fa": normalize_slug(item.get("name_fa") or slug, slug),
            "slug_tr": normalize_slug(item.get("name_tr") or slug, slug),
            "slug_ar": normalize_slug(item.get("name_ar") or slug, slug),
            "description_en": str(item.get("description_en") or ""),
            "description_fa": str(item.get("description_fa") or ""),
            "description_tr": str(item.get("description_tr") or ""),
            "description_ar": str(item.get("description_ar") or ""),
            "website": str(item.get("website") or ""),
            "city": city,
            "university_type": university_type,
            "is_moe_approved": bool(item.get("moe_approved")),
            "is_moh_approved": bool(item.get("moh_approved")),
            "has_erasmus": bool(item.get("erasmus")),
            "has_dormitory": bool(item.get("has_dorm")),
            "listing_priority": int(item.get("boost_score") or 0),
            "is_active": bool(item.get("active", True)),
            "is_featured": bool(item.get("featured", False)),
        }

        ranking = item.get("ranking")
        if isinstance(ranking, int):
            defaults["ranking_urap"] = ranking

        university, created = audited_update_or_create(
            University.objects,
            lookup={
                "slug_en": normalize_slug(slug, f"university-{item.get('id', '')}")
            },
            defaults=defaults,
            actor=self.system_user,
        )

        self._apply_university_assets(
            university=university,
            source_item=item,
            asset_index=asset_index,
        )

        return university, created

    def _apply_university_assets(
        self,
        *,
        university: University,
        source_item: dict[str, Any],
        asset_index: dict[tuple[str, str], list[dict[str, Any]]],
    ) -> None:
        source_id = source_item.get("id")
        if source_id is None:
            return

        assets = asset_index.get(("university", str(source_id)), [])
        if not assets:
            return

        logo_asset = None
        banner_asset = None
        gallery_assets = []

        for asset in assets:
            source_field = str(asset.get("source_field") or "").lower()

            if source_field in {"logo", "logo_url"} and logo_asset is None:
                logo_asset = asset
                continue

            if source_field in {"banner", "banner_url", "cover", "cover_url"} and banner_asset is None:
                banner_asset = asset
                continue

            gallery_assets.append(asset)

        if logo_asset:
            self._save_image_field_if_needed(
                instance=university,
                field_name="logo",
                asset=logo_asset,
                prefix="rasa-logo",
            )

        if banner_asset:
            self._save_image_field_if_needed(
                instance=university,
                field_name="banner",
                asset=banner_asset,
                prefix="rasa-banner",
            )

        existing_markers = set(
            UniversityMedia.objects.filter(university=university).values_list(
                "title",
                flat=True,
            )
        )

        sort_order = UniversityMedia.objects.filter(university=university).count()

        for asset in gallery_assets:
            path = Path(asset["absolute_path"])
            mime_type, _ = guess_type(path.name)

            if not (mime_type or "").startswith("image/"):
                continue

            fingerprint = str(asset.get("sha256") or "")
            if not fingerprint:
                fingerprint = hashlib.sha256(
                    str(asset.get("url") or path).encode("utf-8")
                ).hexdigest()

            marker = f"rasa:{fingerprint}"
            if marker in existing_markers:
                continue

            media = UniversityMedia(
                university=university,
                title=marker,
                sort_order=sort_order,
                is_active=True,
                created_by=self.system_user,
                updated_by=self.system_user,
            )

            with path.open("rb") as handle:
                media.image.save(
                    f"rasa-{source_id}-{path.name}",
                    File(handle),
                    save=False,
                )

            media.save()
            existing_markers.add(marker)
            sort_order += 1

    def _save_image_field_if_needed(
        self,
        *,
        instance: University,
        field_name: str,
        asset: dict[str, Any],
        prefix: str,
    ) -> None:
        path = Path(asset["absolute_path"])
        mime_type, _ = guess_type(path.name)

        if not (mime_type or "").startswith("image/"):
            return

        source_url = str(asset.get("url") or "")
        expected_token = (
            hashlib.sha256(source_url.encode("utf-8")).hexdigest()[:12]
            if source_url
            else ""
        )

        field_file = getattr(instance, field_name)
        current_name = str(getattr(field_file, "name", "") or "")

        if current_name and expected_token and expected_token in current_name:
            return

        filename = (
            f"{prefix}-{expected_token}-{path.name}"
            if expected_token
            else f"{prefix}-{path.name}"
        )

        with path.open("rb") as handle:
            field_file.save(
                filename,
                File(handle),
                save=False,
            )

        instance.save(update_fields=[field_name])

    def _resolve_program_university(
        self,
        item: dict[str, Any],
        *,
        university_by_rasa_id: dict[Any, University],
        university_by_slug: dict[str, University],
    ) -> University | None:
        university_id = item.get("university_id")
        if university_id in university_by_rasa_id:
            return university_by_rasa_id[university_id]

        slug = item.get("university_slug")
        if slug and str(slug) in university_by_slug:
            return university_by_slug[str(slug)]

        name = item.get("uni_name_en") or item.get("university_name_en")
        if name:
            return University.objects.filter(name_en=str(name)).first()

        return None

    def _get_language(self, language_value: str | None) -> ProgramLanguage:
        key = (language_value or "unknown").strip().lower()
        names = LANGUAGE_MAP.get(
            key,
            {
                "name_en": key.title() or "Unknown",
                "name_fa": key,
                "name_tr": key,
                "name_ar": key,
            },
        )

        language, _ = audited_get_or_create(
            ProgramLanguage.objects,
            lookup={"slug_en": normalize_slug(key, "unknown")},
            defaults={
                **names,
                "slug_fa": normalize_slug(names["name_fa"], key),
                "slug_tr": normalize_slug(names["name_tr"], key),
                "slug_ar": normalize_slug(names["name_ar"], key),
                "is_active": True,
            },
            actor=self.system_user,
        )
        return language

    def _get_department(self, item: dict[str, Any], university: University) -> Department | None:
        name_en = str(item.get("department_en") or "").strip()
        name_fa = str(item.get("department_fa") or "").strip()
        name_tr = str(item.get("department_tr") or "").strip()
        name_ar = str(item.get("department_ar") or "").strip()

        if not any((name_en, name_fa, name_tr, name_ar)):
            return None

        canonical = name_en or name_tr or name_fa or name_ar
        slug = normalize_slug(canonical, f"department-{university.id}")

        department, _ = audited_update_or_create(
            Department.objects,
            lookup={"university": university, "slug_en": slug},
            defaults={
                "name_en": canonical,
                "name_fa": name_fa,
                "name_tr": name_tr,
                "name_ar": name_ar,
                "slug_fa": normalize_slug(name_fa or canonical, slug),
                "slug_tr": normalize_slug(name_tr or canonical, slug),
                "slug_ar": normalize_slug(name_ar or canonical, slug),
                "is_active": True,
            },
            actor=self.system_user,
        )
        return department

    def _upsert_program(self, item: dict[str, Any], university: University) -> tuple[Program, bool]:
        raw_degree = str(item.get("degree") or "").strip().lower()
        degree = DEGREE_MAP.get(raw_degree, DegreeType.BACHELOR)
        thesis_type = THESIS_MAP.get(raw_degree)

        language = self._get_language(item.get("language"))
        department = self._get_department(item, university)

        raw_slug = str(item.get("slug") or item.get("name_en") or item.get("id") or "program")
        slug = normalize_slug(raw_slug, f"program-{item.get('id', '')}")

        defaults = {
            "university": university,
            "department": department,
            "name_en": str(item.get("name_en") or raw_slug),
            "name_fa": str(item.get("name_fa") or ""),
            "name_tr": str(item.get("name_tr") or ""),
            "name_ar": str(item.get("name_ar") or ""),
            "slug_fa": normalize_slug(item.get("name_fa") or raw_slug, slug),
            "slug_tr": normalize_slug(item.get("name_tr") or raw_slug, slug),
            "slug_ar": normalize_slug(item.get("name_ar") or raw_slug, slug),
            "description_en": str(item.get("description_en") or ""),
            "description_fa": str(item.get("description_fa") or ""),
            "description_tr": str(item.get("description_tr") or ""),
            "description_ar": str(item.get("description_ar") or ""),
            "degree": degree,
            "thesis_type": thesis_type,
            "program_language": language,
            "duration": int(item["duration_years"]) if item.get("duration_years") else None,
            "listing_priority": int(item.get("boost_score") or 0),
            "is_active": bool(item.get("active", True)),
        }

        return audited_update_or_create(
            Program.objects,
            lookup={"university": university, "slug_en": slug},
            defaults=defaults,
            actor=self.system_user,
        )

    def _upsert_offering(
        self,
        item: dict[str, Any],
        program: Program,
        academic_year: AcademicYear,
        semester: Semester,
    ) -> tuple[ProgramOffering | None, bool]:
        tuition = as_decimal(item.get("tuition_usd"))
        discounted = as_decimal(item.get("tuition_discounted_usd"))
        cash = as_decimal(item.get("tuition_cash_usd"))
        installment = as_decimal(item.get("tuition_annual_installment_usd"))
        discount_pct = as_decimal(item.get("discount_pct"))

        if tuition is None:
            return None, False

        defaults = {
            "fee_basis": "annual",
            "currency": "USD",
            "tuition": tuition,
            "tuition_discount_percentage": discount_pct,
            "tuition_discounted": discounted,
            "tuition_cash": cash,
            "tuition_annual_installment": installment,
            "quota": item.get("quota"),
            "deadline": item.get("deadline") or None,
            "is_active": bool(item.get("active", True)),
        }

        return audited_update_or_create(
            ProgramOffering.objects,
            lookup={
                "program": program,
                "academic_year": academic_year,
                "semester": semester,
            },
            defaults=defaults,
            actor=self.system_user,
        )
