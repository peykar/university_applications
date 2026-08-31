# Django Admin

TurkDemy's Django Admin is intended to be a practical internal operations
interface rather than only a raw model editor.

## Shared audit behavior

Most business models inherit `BaseModel`.

`AuditAdminMixin`:
- makes `created_at`, `updated_at`, `created_by`, and `updated_by` read-only
- automatically sets `created_by` on creation
- automatically updates `updated_by` on every staff save

This avoids manual manipulation of audit identity fields.

## Accounts

User Admin supports searching by:
- username
- email
- mobile/cell
- Telegram username
- Telegram ID
- first/last name

The phone verification timestamp is read-only.

## Agents

Agent Admin includes:
- company/contact columns
- active filtering
- user count
- parent autocomplete
- horizontal user membership selector
- logo preview
- inline `AgentDocument` management
- active/inactive bulk actions

## Geography

Country, Province, and City have:
- multilingual search
- active filters
- autocomplete relationships
- slug prepopulation

## Universities

University Admin includes:
- university type
- YÖK/MOE/MOH flags
- Erasmus and dormitory flags
- listing priority
- featured/active state
- country filtering
- multilingual search
- city autocomplete
- logo/banner previews
- inline university gallery/media management
- feature/unfeature and active/inactive actions

## Programs

Program Admin separates stable academic identity from intake/commercial data.
It includes University, AcademicUnit, optional Department, degree, thesis type,
study mode, canonical duration in months, listing priority, active state, and an
inline instruction-language composition editor with optional percentages.

The `ProgramOffering` inline/admin exposes academic year, intake, fee basis,
currency, standard/list tuition, offered/discounted tuition, cash/advance-payment
tuition, installment tuition, deposit, preparatory tuition, preparation-included
state, quota, deadline, commercial validity, source, notes, and active state.

`UniversityCatalogueSource` has its own admin for uploaded university sheets and
provenance metadata. Offering/source same-University validation prevents linking
a price row to another university's source.

## Students

Student Admin groups:
- identity
- contact/residence
- education
- family
- passport
- internal notes/audit

`StudentDocument` records are editable inline.

## Applications

Application Admin is workflow-oriented and shows:
- student
- university
- program
- academic year
- intake
- agent
- status
- tuition/deposit snapshots

Application documents are editable inline.

Bulk actions support:
- under review
- accepted
- rejected

`ApplicationDocument` also supports verify/unverify actions.

## FAQ and contact submissions

FAQ categories manage FAQ rows inline.

FAQ Admin supports multilingual question/answer search and category filtering.

Contact submissions support:
- handled/unhandled filtering
- search across identity/message fields
- bulk mark handled/unhandled actions

When marked handled through the action, `handled_at` is populated.

## Branding

The Django Admin header is:

```text
TurkDemy Administration
```


## Automatic slug generation

For supported models, admins may leave slug fields empty. On validation/save
TurkDemy fills each missing slug from its related name. Localized fields map
`name_en/fa/tr/ar` to `slug_en/fa/tr/ar`; `FAQCategory.key` maps from `name_en`.
English slugs are ASCII; Persian, Turkish, and Arabic localized slugs preserve
valid Unicode. Existing/non-empty slugs are never automatically replaced when a
name changes, so established URLs remain stable. If the source name is empty,
its slug remains empty.
