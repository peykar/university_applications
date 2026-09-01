# Application-wide localization traceability

| Requirement | Design/tasks | Implementation | Tests | Status |
|---|---|---|---|---|
| `I18N-001` | `design.md`; `I18N-T01`–`I18N-T13` | `apps/core/localization.py`; `apps/core/mixins.py`; `apps/core/forms.py`; `apps/core/templatetags/localization.py`; localized model properties/`__str__`; translation-enabled templates/views/forms; `static/js/searchable_multiselect.js`; `apps/core/views.py::switch_language`; `locale/{fa,tr,ar}/LC_MESSAGES/django.{po,mo}` | `tests/test_application_localization_integrity.py`; `tests/test_searchable_multiselect.py`; `tests/test_homepage_localization_regression.py`; `tests/test_program_filters.py`; `tests/test_language_switching.py`; existing auth/RTL/page regressions | Implemented |
