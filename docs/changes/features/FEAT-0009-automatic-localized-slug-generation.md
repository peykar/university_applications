# FEAT-0009 — Automatic localized slug generation

## Summary

Admins no longer need to type supported slugs manually. Blank localized
catalogue/geography slugs are generated from matching localized names, and the
content `FAQCategory.key` is generated from `name_en`, before persistence.

## Rules

- `slug_en` is generated with ASCII slug semantics.
- `slug_fa`, `slug_tr`, and `slug_ar` use Unicode-aware slugification.
- Explicit slugs are preserved and are not regenerated after name edits.
- Missing localized names leave their corresponding slugs blank.
- All shared localized slug fields are optional in model/admin forms.
- Normalized programme JSON imports still use explicit `slug_en` as their
  deterministic upsert key; this feature does not weaken that import contract.

## Implementation

`BaseModel` performs fill-only slug preparation during `clean()` and `save()` by
inspecting supported `SlugField`/name mappings. `LocalizedSlugMixin` marks all
localized slug fields `blank=True`, and `FAQCategory.key` is also optional, while
preserving Unicode validation rules from CAT-033.

## Verification

Regression tests cover University, Program, Country, Province and City generation,
Unicode preservation, form optionality, full-clean behavior, and preservation of
explicit slugs.
