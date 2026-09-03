from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_homepage_dynamic_hero_copy_uses_trimmed_blocktrans():
    template = (ROOT / "templates/public/home.html").read_text(encoding="utf-8")

    hero_blocktrans = (
        "{% blocktrans trimmed with program_count=program_count "
        "university_count=university_count %}"
    )
    assert hero_blocktrans in template


def test_homepage_study_field_query_carries_localized_names():
    source = (ROOT / "apps/public/views.py").read_text(encoding="utf-8")
    template = (ROOT / "templates/public/home.html").read_text(encoding="utf-8")

    assert "GeneralField.objects.filter(" in source
    assert "programs__is_active=True" in source
    assert "programs__university__is_active=True" in source
    assert '{{ field|localized:"name" }}' in template
    assert "field.localized_name" not in template


def test_homepage_tuition_amount_is_bidi_isolated():
    template = (ROOT / "templates/public/home.html").read_text(encoding="utf-8")

    tuition_markup = (
        '<bdi dir="ltr">{{ program.min_active_tuition|currency_amount:'
        "program.min_active_currency }}</bdi>"
    )
    assert tuition_markup in template
