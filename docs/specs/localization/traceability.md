# Application-wide localization traceability

| Requirement | Design/tasks | Implementation | Tests | Status |
|---|---|---|---|---|
| `I18N-001` | `design.md`; `I18N-T01`–`I18N-T13` | `apps/core/localization.py`; `apps/core/mixins.py`; `apps/core/forms.py`; `apps/core/templatetags/localization.py`; localized model properties/`__str__`; translation-enabled templates/views/forms; `static/js/searchable_multiselect.js`; `apps/core/views.py::switch_language`; `locale/{fa,tr,ar}/LC_MESSAGES/django.{po,mo}` | `tests/test_application_localization_integrity.py`; `tests/test_searchable_multiselect.py`; `tests/test_homepage_localization_regression.py`; `tests/test_program_filters.py`; `tests/test_language_switching.py`; existing auth/RTL/page regressions | Implemented |

| `I18N-002` | `design.md`; `I18N-T14`, `I18N-T16` | `apps/core/localization.py::localized_date`; `apps/core/templatetags/localization.py`; translation-enabled templates | `tests/test_locale_datetime_presentation.py` | Implemented |
| `I18N-003` | `design.md`; `I18N-T14`, `I18N-T16` | `apps/core/localization.py::localized_datetime`; `apps/core/templatetags/localization.py`; timeline/message/workspace templates | `tests/test_locale_datetime_presentation.py` | Implemented |
| `I18N-004` | `design.md`; `I18N-T15` | `apps/core/localization.py::_gregorian_to_jalali`; Persian presentation branch | `tests/test_locale_datetime_presentation.py` | Implemented |
| `I18N-005` | `design.md`; `I18N-T15` | `apps/core/localization.py` month/digit presentation | `tests/test_locale_datetime_presentation.py` | Implemented |
| `I18N-006` | `design.md`; `I18N-T14` | Gregorian EN/TR/AR presentation branches in `apps/core/localization.py` | `tests/test_locale_datetime_presentation.py` | Implemented |
| `I18N-007` | `design.md`; `I18N-T14` | `apps/core/localization.py::_presentation_datetime` | `tests/test_locale_datetime_presentation.py` | Implemented |
| `I18N-008` | `design.md`; `I18N-T14`, `I18N-T16` | `apps/core/localization.py::localized_date`; date-only template surfaces | `tests/test_locale_datetime_presentation.py` | Implemented |
| `I18N-009` | `design.md`; `I18N-T16`, `I18N-T17` | presentation-only helpers/filters; preserved ISO/control template values | `tests/test_locale_datetime_presentation.py`; existing localization/workflow regressions | Implemented |
