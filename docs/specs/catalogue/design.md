# University and program catalogue — technical design

Status: APPROVED
Version: 3.2

## Domain shape

```text
University
 ├── AcademicUnit*
 ├── Department*
 ├── UniversityCatalogueSource*
 └── Program*
      ├── AcademicUnit? / Department?
      ├── study_mode / duration_months / internal_notes
      ├── ProgramInstructionLanguage* → ProgramLanguage
      └── ProgramOffering*
           ├── AcademicYear
           ├── Intake
           ├── OfferingFee*
           ├── preparation_included
           ├── quota / deadline / validity
           ├── notes
           └── source? → UniversityCatalogueSource
```

Catalogue v3 is the sole active persistence representation.

## Model design

### AcademicUnit

Add `AcademicUnit` under `apps.universities` with University ownership,
localized name fields consistent with existing catalogue entities, unit type,
active state, and normal audit/base-model fields where applicable. Enforce same
University when attached to Program.

### Instruction languages

Replace Program's single-language domain contract with a through model
`ProgramInstructionLanguage`. Keep `ProgramLanguage` as the canonical language
vocabulary. The through model stores `percentage` (nullable) and `is_primary`.
Use a database/service uniqueness invariant for `(program, language)`.

Percentage-total validation belongs in model/service/form validation because a
row cannot validate the aggregate alone. Null means "source did not state the
share", not zero.

The earlier single-language compatibility field has been removed. All language
readers and writers use `ProgramInstructionLanguage`.

### Program internal notes

Add an optional `Program.internal_notes` text field for provenance, normalization,
and staff/import commentary that does not belong in customer-facing programme
descriptions. The Django admin may expose it to staff, but public/customer
templates and the public Program API serializer must not expose it. The
normalized JSON importer accepts optional `internal_notes` and treats it as an
updatable Program attribute under the existing Program upsert key. This is
distinct from `ProgramOffering.notes`, which remains source/commercial context
for an Offering and may have its own presentation semantics.

### Study mode

Add a Program choice field with stable values `on_campus`, `distance`, `online`,
`hybrid`. Default existing rows to `on_campus`; importers may override only from
source evidence.

### Duration

Use `duration_months` as the sole stored duration. It is unambiguous and supports
fractional-year programmes such as 18 months without loss.

### UniversityCatalogueSource

Add a University-owned source record containing title, optional uploaded file,
received date, optional AcademicYear, optional valid-from/until, source notes,
and recorded-by User. Source records are provenance and must not be cascade-
deleted merely because an Offering changes. Prefer protective/null-safe
relations according to existing file-retention conventions.

### ProgramOffering

`ProgramOffering` is the intake/availability/provenance boundary. It stores the
canonical `Intake`, academic year, preparation-inclusion flag, quota/deadline,
validity, notes, and source. Monetary values are not columns on ProgramOffering.
Each price/percentage is an `OfferingFee` with explicit fee type, currency, basis,
optional language, label, and notes.

## Admin/agent maintenance

Program editing must group stable academic identity separately from offering
commercial data. Offering maintenance exposes all CAT-019 fields. Source is
selectable only from the same University as the Program/Offering.

AcademicUnit, Department, language composition, study mode and duration are
Program-level inputs. Agent-facing validation must explain invalid mixed
language percentages and cross-University selections.

## Import and transition strategy

The compatibility transition is complete. New code must not create or read the
removed Semester, single-language Program field, whole-year duration field, or
fixed ProgramOffering price columns. Source ambiguity is preserved in notes rather
than guessed.

### Normalized per-University JSON import

`import_programs_for_university` accepts University UUID,
UniversityCatalogueSource UUID, and a schema-v2 JSON path. Programs use `slug_en`
as their deterministic key. Offerings use Program + AcademicYear + Intake + source.
Instruction-language rows are authoritative for imported Programs, and each
Offering carries a structured `fees` array. The whole import is atomic.

### Rasa import

Rasa source columns are normalized directly into `duration_months`,
`ProgramInstructionLanguage`, university/year-specific `Intake`, and `OfferingFee`
rows. The `--semester` command-line spelling is accepted only as an alias for
`--intake`; it does not create a Semester model or compatibility data.

## Public catalogue

Language filters match any canonical instruction-language association. Mixed
language display renders known percentages where available. Study mode and
AcademicUnit become available presentation/filter dimensions where UX chooses
to expose them. Tuition filters continue to constrain a coherent Offering row.

Program-detail similarity cards may use the annotated minimum active tuition as
their numeric source, but public copy presents that value as **“Tuition from”**
rather than exposing internal/query terminology such as “minimum active tuition”.
This refinement changes presentation only; the tuition annotation/filter semantics
remain unchanged.

## Cross-cutting constraints

- Follow `docs/product/business-rules.md` and terminology.
- Preserve existing LeadProgramInterest/Application relationships to Program and
  ProgramOffering.
- Existing Applications must retain valid Offering references through migrations.
- Admission workflow semantics remain unchanged except that Application pricing snapshots now read canonical structured OfferingFee data.
- Preserve i18n/RTL behavior and existing localized catalogue naming patterns.

## Architecture decision

See `docs/architecture/decisions/ADR-006-university-catalogue-v2.md`.

## University catalogue JSON dump

`dump_university_data <university-id>` produces a schema-v2 UTF-8 JSON snapshot
for offline catalogue comparison and text enrichment. The command accepts one
required positional argument; `--output` is an optional destination override.
The default filename is `university_<uuid>_catalogue.json`.

The export is deliberately catalogue-scoped rather than a database backup. It
contains localized University/geography data, media metadata, AcademicUnits,
Departments, catalogue sources, Programs (including internal notes), canonical
instruction languages, and ProgramOfferings. It does not traverse Leads,
Students, Applications, conversations, users, or other customer operational
records. File/image fields are represented by their stored names rather than
embedding binary content. Decimal values are emitted as strings to preserve
precision and dates use ISO-8601 strings.
## Localized Unicode slugs

The shared `LocalizedSlugMixin` keeps `slug_en` as Django's default ASCII-only
`SlugField` and enables `allow_unicode=True` only for `slug_fa`, `slug_tr`, and
`slug_ar`. Because University, AcademicUnit, Department, ProgramLanguage, Program,
and Country/Province/City share this mixin, model/admin/import validation now
uses the same native-script policy everywhere. This is a validation/state change;
it does not rewrite existing stored slugs.

Public, application, and API detail routes already use the single-segment
`<str:slug>` converter so persisted Unicode slugs can be reversed and resolved.
The normalized university-program JSON importer continues to use `slug_en` as its
deterministic upsert key, while localized slug fields may carry native Persian,
Turkish, or Arabic slugs. No transliteration or fallback to English is required.



## Automatic localized slug generation

Supported slug fields are optional input in admin forms. `BaseModel` inspects
`SlugField`s and fills only missing values where the related name mapping is known.
Localized `slug_<locale>` fields map to `name_<locale>`; conventional `slug` maps
to `name`; and the existing `FAQCategory.key` maps to `name_en`. English uses
Django `slugify(..., allow_unicode=False)` while Persian, Turkish, and Arabic
localized fields use their field-level Unicode setting.

Generation is fill-only for the shared default slug behavior. `Program` is an
intentional CAT-050 exception: its localized public slugs are canonical derived
values and are rebuilt from University slug, localized Program name, degree,
thesis type when applicable, and structured instruction languages. A Program
name or variant change can therefore change its public slug. In normalized
schema-v2 programme imports, input `slug_en` remains the stable source identity
used to re-match the existing row; the persisted Program `slug_en` is the
structured public slug rather than the source key.

## Catalogue v3 transition completion

Catalogue v3 is now the sole active persistence model. `Program` stores canonical
`duration_months` and instruction-language through rows only. `ProgramOffering`
stores its `Intake`, availability/provenance metadata, and preparation-inclusion
flag; all monetary values, currencies, percentages and fee bases live in
`OfferingFee`.

Application creation is an explicit v3 consumer. It selects the same canonical
payable tuition used for presentation (discounted tuition first, then list
tuition), rejects offerings without an amount-bearing active tuition fee, and
snapshots an active structured deposit when one exists.

Normalized JSON import schema version 2 requires `intake` and a structured
`fees` array. Rasa source columns are translated directly into OfferingFee rows.
No importer writes a compatibility copy. Export and Admin likewise expose only
the canonical model.

## Globally unique Program public slugs (CAT-050)

`Program` specializes shared slug behavior because its slug is a single-segment
public/API route identifier. It does not treat an imported or manually edited
Program slug as canonical input. Instead, each localized slug is reconstructed
from structured catalogue data: localized University slug, localized Academic Unit
when present, localized Department when present, localized Program name,
deterministic localized degree token, `thesis`/`non-thesis` when applicable, and
the structured instruction-language variant. Missing Academic Unit/Department
relations are omitted rather than inferred. When an existing Academic Unit or
Department lacks the requested locale, slug generation preserves that hierarchy
component by falling back to its English slug, then English name. This prevents
localized slug collisions caused only by incomplete hierarchy translations.
Instruction languages are ordered primary-first and then deterministically, and
every language in a multilingual variant is represented.

`ProgramInstructionLanguage.save()` refreshes the parent Program so Admin/import
inline changes also refresh public slugs. Repeated generation from the same
structured state is idempotent. Program localized slugs retain conditional database
uniqueness constraints (blank localized values are excluded).

`rebuild_program_slugs` is the existing-database operator path. It derives every
target slug from current structured Program data and computes the complete target set
before writes. When two or more Programs would receive the same localized canonical
slug, the command reports the conflicting locale, base slug, Program identifiers, and
resolved slugs. The first Program in deterministic Program-ID order keeps the base slug;
later Programs receive the smallest available numeric tail (`-2`, `-3`, ...), avoiding
other canonical and already assigned targets. The command rebuilds all locales rather than partially
rewriting its other localized slugs. The command supports `--dry-run` and updates audit
metadata for Programs it actually writes. This means legacy rows such as
`altinbas-dentistry` normalize to a structured identity such as
`altinbas-faculty-of-dentistry-dentistry-bachelor-english` when its Academic Unit,
Program, and instruction-language data establish those values.

## Source-faithful public fee presentation (CAT-013, CAT-037, CAT-038, CAT-043)

The public Program detail page may continue to promote `display_tuition_fee` as
its headline payable tuition (discounted tuition first, then list tuition), but
promotion must not erase the selected `OfferingFee` semantic label. The headline
therefore renders the fee's source label (or canonical fee-type label), amount,
and basis together.

`OfferingFee.display_label` is the presentation boundary for fee labels. It
preserves a non-empty source label verbatim and falls back to the canonical
fee-type display name. When a structured percentage exists and the chosen label
does not already contain a percent sign, the percentage is appended once in
parentheses. This prevents source labels such as `Scholarship fee (10%)` or
`Advance payment (15%)` from producing duplicate percentage text while ensuring
percentage-only semantics are not hidden when a source label omits the number.

All remaining amount-bearing structured fees render their label, amount, and
basis as one fact. The template does not recompute discounts or infer relations
between fee rows; it only presents the source-faithful normalized data.

## Persisted catalogue audit

`audit_catalogue` is an operator-facing, read-only verification surface run after
bulk catalogue imports. It audits the database state rather than source packages,
so it catches cross-import collisions and stale/incomplete persisted records.
Findings use ERROR, WARNING and INFO severities. ERROR means a broken invariant or
an active offering that cannot safely create an Application; WARNING means data
that deserves review but can be legitimate when the source is incomplete; INFO is
used for expected-but-notable state such as numeric public-slug collision tails.
The command never repairs data. Human output is the default; JSON and CSV are
available for review/automation. `--fail-on-errors` is opt-in so an exploratory
audit remains non-disruptive.

## Locale-independent public filter identity (CAT-052, superseded in part by CAT-055)

Slug-backed public catalogue filters use `slug_en` as their stable URL identity in
all supported locales. Locale selection affects presentation labels only. CHG-0017
keeps that URL invariant but moves the `field` dimension from repeated University-owned
Department slugs to the global TurkDemy `GeneralField.slug_en`. Public controls expose
only active GeneralFields connected to active Programs at active Universities. The
homepage applies the same active-catalogue boundary. Department remains source/catalogue
structure and is no longer the public field-filter identity.


## GeneralField classification layer (CHG-0017)

`GeneralField` is a TurkDemy-owned taxonomy layer that sits beside, not inside, the
University hierarchy. The existing `AcademicUnit` and `Department` models remain
unchanged and continue to represent source/university structure.

```text
University
 ├── AcademicUnit / Department
 └── Program
      └── general_fields* ──> GeneralField (global TurkDemy taxonomy)
```

Each Program may have zero or more GeneralFields. The optional many-to-many relation makes curation state explicit: an empty relation means the Program has not yet been mapped or intentionally remains unclassified, while interdisciplinary Programs may be mapped to multiple GeneralFields. No mapping is inferred from Department names/slugs during import.

Public `?field=` filtering resolves exclusively against `GeneralField.slug_en`; labels
are localized at presentation time. This keeps one stable filter identity across EN,
FA, TR and AR while separating it from University-specific Department data. Homepage
field discovery uses the same GeneralField many-to-many relation and active-catalogue constraints.

Django Admin is the first curation surface. GeneralField has localized editorial and
SEO fields so a later SEO change can create canonical field landing pages without
changing the taxonomy model. Program admin exposes the mapping through autocomplete
and list/filter/search support.

`import_programs_for_university` deliberately excludes GeneralField memberships from update
defaults. New Programs therefore remain unmapped and all existing assignments survive re-import. The schema validator rejects supplied `general_field` and `general_fields` keys so accidental automatic classification cannot become an undocumented import convention.

## City public landing pages (CAT-064–CAT-066)

City landing routes live inside the University catalogue namespace at
`/universities/cities/<slug_en>/`. The route resolves an active City only when it
has at least one active University. `slug_en` is the stable route identity across
locale prefixes.

The view renders City editorial/SEO fields from the City model, paginates active
Universities 24 at a time, and shows up to 12 representative active Programs from
active Universities in the City using the canonical structured-fee tuition
annotation. A Program-catalogue link carries `?city=<slug_en>` for advanced
discovery; that query surface remains non-canonical/noindex.

City pages use CollectionPage + BreadcrumbList structured data. Sitemap emission is
restricted to active Cities with active Universities. University detail pages provide
crawlable internal links to their City's canonical landing route.

## City banner media (CAT-067)

`City.banner` stores one optional shared visual under `cities/banners/`. Localized
`banner_alt_*` fields provide meaningful accessibility/SEO text. The model exposes
`localized_banner_alt`, which follows the shared localization fallback and ultimately
falls back to the localized City name. City Admin provides the upload field, localized
alt fields, and a read-only preview.

The City landing template renders the banner directly below the hero when present and
omits the entire media block when absent. The view promotes the same banner to the page's
Open Graph/Twitter image and CollectionPage `image` property using an absolute media URL.
No image is synthesized when a City has no curated banner.


## Homepage City discovery (CAT-068)

The homepage queries active `City` rows that have active Universities, annotates distinct
active-University and active-Program counts, and exposes the top five ordered by University
count, Program count, then English name. Cards link directly to
`university-city-detail` using the canonical `slug_en`; they never use a query-string filter
as the destination identity.

Cards reuse `City.banner` and `City.localized_banner_alt` when curated. Missing banners use
a non-semantic visual placeholder while preserving the localized City name as visible text.
The desktop layout is a compact responsive card grid; mobile uses a horizontally swipeable
row so destination discovery does not create excessive page height.

## Program contextual discovery (CAT-069)

Program detail is a junction between specific programme intent and broader catalogue
discovery. The University remains a first-class link; the University's active City links to
`/universities/cities/<slug_en>/`, and active mapped GeneralFields link to
`/programs/fields/<slug_en>/`. Canonical English slugs remain route identity across locales.
Query-string filters remain advanced-navigation surfaces and are not substituted for these
curated landing links.

## Program Detail conversion layout (CAT-070)

The Program page remains a decision surface rather than a raw record view. Desktop keeps the main
catalogue information at inline-start and the Request conversion card in an adjacent sticky column;
CSS Grid follows the document direction so RTL naturally mirrors the visual placement. A lone
Offering spans the main column to avoid artificial whitespace. The University showcase and media
retain the same information with tighter vertical density.

At widths below 1000px the grid collapses and the Request sidebar receives negative flex/grid order
so it appears before the long main content without duplicating the conversion action in the DOM.
Mobile uses the approved conversion-first composition: the hero gets generous safe spacing; hero fact
pills are suppressed so degree/language/duration/study-mode appear only once in a compact four-cell
summary row. The hero already names and links the University and City, so mobile deliberately omits a
separate University bridge card and moves directly from hero context to the fact row. The Request card
keeps one dominant CTA with two compact secondary actions. The later University section uses a three-column by
two-row fact grid, shortened expandable copy and a wide media treatment. Similar Programs use compact
horizontal snap cards so several alternatives are visible without creating a long repeated stack.
