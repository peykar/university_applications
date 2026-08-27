# Generic Agent ↔ Customer messaging

Messaging is modeled as communication between one Agent organization and one
customer, optionally scoped to a business subject. The current subjects are
Lead, Student, and Application; future UUID-based domain objects can use the
same `Conversation` model through Django ContentTypes.

## Models

- `Conversation`: Agent + customer + generic subject + closed state.
- `Message`: sender user, sender role (`customer`, `agent`, `system`), body.
- `MessageAttachment`: reusable chat attachment metadata/file.
- `ConversationParticipantState`: per conversation + user + party-role read
  cursor (`last_read_message`, `last_read_at`).

Read state is deliberately per **user and party role**. This matters when an
account is both a customer and an agent user, and when several users belong to
the same Agent. Reading a customer message as Agent user A does not mark it read
for Agent user B.

Unread badges are available in both customer and Agent navigation. Agent unread
messages count customer-originated messages. Customer unread messages count
Agent and System messages. A user's own sent messages are never incoming/unread.

## Permissions

Agent-side access is granted by membership in `conversation.agent.users`
(superusers are allowed globally). Customer-side access requires
`conversation.customer == request.user`. `get_or_create_conversation()` also
validates that Lead/Student/Application Agent and customer ownership matches the
Conversation, preventing cross-Agent subject mismatches.

## Existing Lead messages

Migration `messaging.0002_migrate_lead_messages` copies existing Lead
conversation/message/attachment history into the generic tables using the old
UUIDs where possible and collapses old per-message read receipts into the
participant last-read cursor. The old Lead-specific messaging models are kept
temporarily for migration/backward compatibility, but runtime Lead, Student,
and Application messaging uses `apps.messaging`.


## Customer conversation page

The customer Messages inbox opens a generic conversation page for Student,
Application, general, and future subjects. Lead conversations remain visible on
the Applicant page as well. Opening a conversation advances only that customer's
read cursor; Agent-user read cursors are independent.


## Explicit legacy-message migration command

Although the generic messaging schema includes a data migration, legacy Lead
messages can also be migrated explicitly and safely with the management
command:

```bash
uv run python manage.py migrate_legacy_messages --dry-run
uv run python manage.py migrate_legacy_messages
```

or:

```bash
make messages-migrate-dry-run
make messages-migrate
```

The command is idempotent: conversations, messages and attachments already
present in the generic tables are reused instead of duplicated. Existing
`LeadMessageRead` rows are collapsed to the latest read cursor for each
conversation/user and stored in `ConversationParticipantState`.

`--dry-run` performs all validation and prints counts, then rolls back the
transaction.

The command reports created/existing/skipped counts for conversations,
messages, attachments and participant read states. A legacy conversation is
skipped (and its id reported) if its Lead has no Agent or no customer User.

The command does not delete legacy Lead messaging rows. Removal of the old
models/tables should be done only after migration output and the new UI have
been verified.
