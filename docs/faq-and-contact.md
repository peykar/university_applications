# FAQ and Contact Models

## Origin

`FAQCategory`, `FAQ`, and `ContactSubmission` were reworked from the previous
`tgate` project and adapted to the current application's UUID/audit/localization
conventions.

## FAQCategory

Represents a public FAQ grouping.

Important fields:
- `key`: stable unique category identifier
- localized names: English, Persian, Turkish, Arabic
- optional frontend `icon` and `color`
- `sort_order`
- `is_active`

The old `tgate` model stored a mutable `count` field. The new model does not
store that duplicate value; `faq_count` is calculated from the related FAQ
records so it cannot become stale.

## FAQ

FAQ content supports English, Persian, Turkish, and Arabic questions/answers.
At least one localized question and one localized answer are required.

Additional fields retained/reworked from `tgate`:
- category
- optional audio URL
- view count
- optional short label
- optional topic
- active flag

`localized_question()` and `localized_answer()` provide language fallback.

## ContactSubmission

Stores messages submitted through a public contact form:
- name
- email
- optional phone number
- subject
- message
- handled status

Phone numbers use the same international validation/E.164 normalization as
other phone fields in the project.

Contact submissions inherit UUID and audit fields from `BaseModel`.
