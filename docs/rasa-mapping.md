# RasaStudy → TurkDemy Mapping

This is the canonical mapping reference for the RasaStudy download/import flow.

## Source files

```text
data/rasa/
├── universities.json
├── programs.json
├── faq_categories.json
├── faqs.json
├── assets_manifest.json
└── assets/
```

## University

| Rasa | TurkDemy |
|---|---|
| `id` | import lookup only; TurkDemy keeps UUID PKs |
| `slug` | `University.slug_en` |
| `name_en/fa/tr/ar` | corresponding `University.name_*` |
| `description_en/fa/tr/ar` | corresponding `University.description_*` |
| `website` | `University.website` |
| `type` | `University.university_type` |
| city fields | `City` through geography fallback |
| `moe_approved` | `University.is_moe_approved` |
| `moh_approved` | `University.is_moh_approved` |
| `erasmus` | `University.has_erasmus` |
| `has_dorm` | `University.has_dormitory` |
| `boost_score` | `University.listing_priority` |
| `featured` | `University.is_featured` |
| `active` | `University.is_active` |
| `ranking` | currently `University.ranking_urap` as a temporary generic fallback |

## University images

The downloader records downloaded files in `assets_manifest.json`.

References with:

```text
object_type = university
source_field = logo or logo_url
```

map to `University.logo`.

References with:

```text
source_field = banner, banner_url, cover, or cover_url
```

map to `University.banner`.

Other university image assets become `UniversityMedia`.

The importer uses Django's file/storage API. Raw source paths under
`data/rasa/assets/` are never assigned directly to `ImageField`.

Re-import behavior:
- logo/banner filenames include a hash derived from the source URL
- already imported logo/banner assets are not intentionally duplicated
- gallery media uses a source fingerprint marker to avoid duplicate
  `UniversityMedia` rows

## Program

| Rasa | TurkDemy |
|---|---|
| `university_id` | `Program.university` |
| `slug` | `Program.slug_en` |
| `name_en/fa/tr/ar` | corresponding `Program.name_*` |
| `description_en/fa/tr/ar` | corresponding `Program.description_*` |
| `department_*` | `Department` + `Program.department` |
| `degree` | `Program.degree` |
| `language` | `ProgramLanguage` + `Program.program_language` |
| `duration_years` | `Program.duration` |
| `boost_score` | `Program.listing_priority` |
| `active` | `Program.is_active` |

### Degree mapping

```text
associate          → associate
bachelor           → bachelor
master             → master
master_thesis      → master + thesis
master_non_thesis  → master + non_thesis
phd                → phd
```

## ProgramOffering

Rasa stores pricing/intake properties directly on a program row. TurkDemy
normalizes them into `ProgramOffering`.

| Rasa | TurkDemy |
|---|---|
| `tuition_usd` | `ProgramOffering.tuition` |
| `tuition_discounted_usd` | `tuition_discounted` |
| `tuition_cash_usd` | `tuition_cash` |
| `tuition_annual_installment_usd` | `tuition_annual_installment` |
| `discount_pct` | `tuition_discount_percentage` |
| `quota` | `quota` |
| `deadline` | `deadline` |

Current importer assumptions:

```text
currency      = USD
fee_basis     = annual
academic_year = command argument, default 2026-2027
semester      = command argument, default Fall
```

## FAQCategory

Accepted source containers:

```text
cats
categories
faq_categories
```

| Rasa | TurkDemy |
|---|---|
| `id` | import lookup only |
| `key` / `slug` | `FAQCategory.key` |
| `name_en/fa/tr/ar` | corresponding name fields |
| `icon` | `FAQCategory.icon` |
| `color` | `FAQCategory.color` |
| `sort_order` / `order` | `FAQCategory.sort_order` |
| `active` / `is_active` | `FAQCategory.is_active` |

Rasa category counts are not imported; TurkDemy calculates `faq_count`
dynamically.

## FAQ

Accepted source containers:

```text
faqs
faq
```

| Rasa | TurkDemy |
|---|---|
| `category_id` / `cat_id` | `FAQ.category` |
| `question_en/fa/tr/ar` | corresponding question fields |
| `answer_en/fa/tr/ar` | corresponding answer fields |
| `sort_order` / `order` | `FAQ.sort_order` |
| `active` / `is_active` | `FAQ.is_active` |

FAQ `audio_url` assets are downloaded but are not currently attached to the
FAQ model because TurkDemy does not yet have an FAQ audio field.

## Idempotency

Stable import keys are:

```text
University        → slug_en
Program           → university + slug_en
ProgramOffering   → program + academic_year + semester
FAQCategory       → key
FAQ               → category + question_en
UniversityMedia   → source fingerprint marker
```

## Geography fallback

Rasa provides city text but no normalized province hierarchy.

The importer currently creates:

```text
Country(TR)
└── Province(<Rasa city name>)
    └── City(<Rasa city name>)
```

This is explicitly a fallback until TurkDemy has a canonical Türkiye
administrative geography dataset.
