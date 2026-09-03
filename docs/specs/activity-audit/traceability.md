# Activity and audit — traceability

Status: BASELINED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `AUD-001` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `AUD-002` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `AUD-003` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `AUD-004` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `AUD-005` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `AUD-006` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `AUD-007` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `AUD-008` | `apps/leads/services/activity_presentation.py`; `apps/leads/models.py`; predefined Lead Activity producers; `templates/agents/applicant_activity.html`; FA/TR/AR gettext catalogs | `tests/test_activity_localization.py`; `tests/test_application_localization_integrity.py` | Automated |
| `AUD-009` | `apps/leads/services/activity_presentation.py`; preserved `LeadActivity.description` fallback | `tests/test_activity_localization.py` | Automated |
| `AUD-010` | `templates/agents/applicant_activity.html`; `static/css/turkdemy.css` | `tests/test_agent_activity_page.py` | Automated |

## Notes

This baseline intentionally starts at capability level. When a requirement is
changed or newly implemented, replace the family row with requirement-level
code paths and named tests. Do not claim exact traceability that has not been
verified.
