# Activity and audit — technical design

Status: BASELINED

## Design mapping

- Model: `LeadActivity` with type, description, metadata and visibility flag.
- Shared recorder lives under Lead services/activity.
- Agent Activity page is separate from compact Applicant Overview.
- Predefined Activity description presentation is centralized in
  `apps/leads/services/activity_presentation.py` and exposed through
  `LeadActivity.localized_description`.
- New predefined event producers persist semantic metadata for dynamic values.
  Program references use stable Program IDs so the current localized Program
  name can be resolved at display time; document metadata prefers stable type and
  review-status codes plus free-form document names where applicable.
- The renderer includes backward-compatible parsing for recognized historical
  English description shapes. It never mutates historical rows and falls back to
  the stored description for unknown/free-form audit text.
- Agent templates render `localized_description` rather than raw
  `description`; structured profile-change field labels render through
  `localized_changes`, while old/new snapshot values remain immutable audit data.
  Activity-type choice labels continue to use Django i18n.


- The dedicated Agent Activity timeline keeps title, actor and localized timestamp
  in one compact metadata stack so wide desktop layouts do not visually detach
  metadata from its event. The stack uses logical `start` alignment and therefore
  follows LTR/RTL page direction without physical left/right overrides.
- Activity descriptions and structured old/new audit values use `dir="auto"` plus
  plaintext bidi isolation at presentation time. This protects English emails,
  filenames, Program names and other LTR values embedded in Persian/Arabic pages
  while preserving the exact stored/display value.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
