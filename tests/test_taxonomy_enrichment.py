from pathlib import Path

from apps.geography.models import City
from apps.universities.management.commands import enrich_taxonomy


def test_city_has_localized_editorial_and_seo_fields():
    field_names = {field.name for field in City._meta.fields}
    for locale in ("en", "fa", "tr", "ar"):
        assert f"description_{locale}" in field_names
        assert f"seo_title_{locale}" in field_names
        assert f"seo_description_{locale}" in field_names


def test_taxonomy_snapshot_is_explicit_and_leaves_only_known_bad_record_unmapped():
    assert len(enrich_taxonomy.GENERAL_FIELDS) == 24
    assert len(enrich_taxonomy.PROGRAM_FIELD_MAP) == 5508
    assert enrich_taxonomy.CITY_ENRICHMENT["slug_en"] == "istanbul"
    assert enrich_taxonomy.SKIPPED_PROGRAMS == {
        "b16d8718-7e8a-46d8-bb68-50913baad85e": (
            "Malformed catalogue record whose English name is only 'biruni'; "
            "manual review required."
        )
    }
    valid_slugs = {field["slug_en"] for field in enrich_taxonomy.GENERAL_FIELDS}
    assert valid_slugs
    assert all(set(slugs) <= valid_slugs for slugs in enrich_taxonomy.PROGRAM_FIELD_MAP.values())


def test_normal_program_importer_does_not_reference_enrichment_command():
    importer = Path(
        "apps/universities/management/commands/import_programs_for_university.py"
    ).read_text(encoding="utf-8")
    assert "PROGRAM_FIELD_MAP" not in importer
    assert "enrich_taxonomy" not in importer
