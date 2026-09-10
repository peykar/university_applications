# Email and notification templates — technical design

Status: ACTIVE

## Design mapping

- `apps/core/email_previews.py` is the canonical outgoing-type registry and preview surface.
- `apps/core/services/emailing.py` rejects unregistered outgoing email types.
- `apps/core/services/business_email.py` owns business-recipient selection, direct links, and
  post-commit dispatch.
- `apps/core/services/business_email_content.py` is the shared production/preview copy builder for
  every business email type. The preview gallery supplies representative primitive context to this
  builder instead of maintaining separate placeholder content.
- Existing domain services/views call the business-email service only after the relevant domain
  state has been persisted.
- Authentication rendering remains owned by the account adapter; business previews use the same
  business content builder as delivery and the shared branded HTML renderer.
- `templates/emails/base.html` localizes reusable branded/footer chrome in the active email language.
- Base-domain configuration remains environment-driven through `SITE_URL`.
- Supported language behavior follows project i18n settings/active translation context.

## Recipient policy

- Customer: Request confirmations, human Agent messages, recommendations, document actions,
  finalization milestones, Application creation and status changes.
- Agent users: new Requests and customer messages.
- Individual Agent assignee: TODO assignment when another user assigns it.
- University contacts and global administrators: no automatic business email in this version.

## Delivery policy

Business email is registered via `transaction.on_commit`. Email contains a concise event summary
and direct link, but messaging notifications intentionally do not copy message body content.

## Cross-cutting constraints

Follow `docs/product/business-rules.md`, permissions architecture, auditability requirements, and
service-layer workflow ownership. Email is a side effect of a successful workflow, not the workflow
transaction itself.
