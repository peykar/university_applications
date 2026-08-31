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

### Localized slugs

English slugs remain ASCII-only. Persian, Turkish, and Arabic localized slugs may
retain valid native-script values from Rasa/import data; they do not need to be
transliterated to English.

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
| `language` | `ProgramLanguage` + one or more `ProgramInstructionLanguage` rows |
| `duration_years` | canonical `Program.duration_months` |
| `boost_score` | `Program.listing_priority` |
| `study_mode` | `Program.study_mode` when explicitly recognized; unknown values are preserved in offering notes |
| `academic_unit` / `faculty` / `school` / `institute` | `AcademicUnit` + `Program.academic_unit` when supplied |
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
| `tuition_discounted_usd` | `OfferingFee(DISCOUNTED_TUITION)` |
| `tuition_cash_usd` | `OfferingFee(CASH_PAYMENT)` |
| `tuition_annual_installment_usd` | `OfferingFee(INSTALLMENT_TOTAL)` |
| `discount_pct` | percentage on discounted-tuition `OfferingFee` |
| `deposit_usd` | `deposit` |
| `preparatory_tuition_usd` | `OfferingFee(PREPARATORY)` |
| `preparation_included` | `preparation_included` |
| `quota` | `quota` |
| `deadline` | `deadline` |
| `valid_from` / `valid_until` | offering commercial validity |
| `offering_notes` / `notes` | `notes` |

Current importer assumptions:

```text
currency      = USD
fee_basis     = annual
academic_year = command argument, default 2026-2027
intake        = command argument, default Fall
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
ProgramOffering   → program + academic_year + intake
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

## Audit mapping

Rasa source records do not control TurkDemy's audit-user foreign keys.
TurkDemy assigns the configured non-human system user during import:

```text
new imported row:
  created_by = system user
  updated_by = system user

existing row updated by re-import:
  created_by = preserved
  updated_by = system user
```

The system identity is configured through `.env`; see `docs/auditing.md`.

## Numeric source normalization

RasaStudy may serialize integer-like values as decimal strings, for example:

```text
duration_years = "5.0"
quota = "40.0"
boost_score = "2.0"
```

The importer accepts integral decimal representations and normalizes them to
integers. Non-integral values such as `"5.5"` are not coerced into integer
fields.

## FAQ category relationship shape

The downloaded Rasa FAQ records use a category **string**, not a category ID:

```json
{
  "id": 81,
  "category": "خوابگاه",
  "question_fa": "..."
}
```

Rasa FAQ categories use that same value as `key`:

```json
{
  "id": 2,
  "key": "خوابگاه",
  "name_fa": "خوابگاه"
}
```

Therefore the canonical relationship mapping is:

```text
FAQ.category (Rasa string)
        ↓
FAQCategory.key
        ↓
FAQ.category (TurkDemy ForeignKey)
```

The importer also supports numeric IDs, explicit category-key fields, and a
nested category object as defensive fallbacks.

### Catalogue v3 storage

Rasa imports write `Intake`, `ProgramInstructionLanguage`, `duration_months`, and
structured `OfferingFee` rows directly. New imports do not create Catalogue v2 compatibility data. Existing databases that still contain v2 columns must use the documented pre-migration cutover before those columns are dropped.

