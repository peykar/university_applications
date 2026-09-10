# Email and notification templates — traceability

Status: ACTIVE

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `MAIL-001` | `apps/core/services/business_email.py`, email branding/site settings | `tests/test_business_email_notifications.py` | Exact |
| `MAIL-002` | `apps/core/email_previews.py` | `tests/test_email_preview_gallery.py` | Exact |
| `MAIL-003` | `apps/core/email_previews.py` | `tests/test_email_preview_gallery.py` | Exact |
| `MAIL-004` | preview renderer/gallery | `tests/test_email_preview_gallery.py` | Exact |
| `MAIL-005` | account adapter/auth templates | existing branded/auth email tests | Baseline |
| `MAIL-006` | lead post-save + business email service | `tests/test_business_email_notifications.py` | Exact |
| `MAIL-007` | messaging service + business email service | `tests/test_business_email_notifications.py` | Exact |
| `MAIL-008` | recommendation service + business email service | service wiring + preview registry tests | Partial |
| `MAIL-009` | Agent document review + business email service | service wiring + preview registry tests | Partial |
| `MAIL-010` | lead finalization service + business email service | service wiring + preview registry tests | Partial |
| `MAIL-011` | Application creation service + business email service | service wiring + preview registry tests | Partial |
| `MAIL-012` | Agent Application status workflow + business email service | service wiring + preview registry tests | Partial |
| `MAIL-013` | operations TODO service + business email service | `tests/test_business_email_notifications.py` | Exact |
| `MAIL-014` | `apps/core/services/business_email.py` | `tests/test_business_email_notifications.py` | Exact |
| `MAIL-015` | post-commit side-effect boundary | design + service tests | Partial |
| `MAIL-016` | business email copy/routes | `tests/test_business_email_notifications.py` | Exact |
| `MAIL-017` | `apps/core/services/business_email_content.py`, `apps/core/email_previews.py` | `tests/test_email_preview_gallery.py`, `tests/test_business_email_notifications.py` | Exact |
| `MAIL-018` | `templates/emails/base.html`, locale catalogs | `tests/test_email_preview_gallery.py`, localization integrity tests | Exact |

