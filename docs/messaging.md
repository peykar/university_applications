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

## Fresh installation

Legacy Lead messaging has been removed. Generate fresh migrations with `uv run python manage.py makemigrations` and apply them with `uv run python manage.py migrate`.
## Requests without an Agent yet

A customer Request can exist before an Agent organization is assigned. Such a Request remains fully viewable, but no generic Conversation is created because Conversation requires both an Agent and customer. The Request Messages tab explains that messaging becomes available after advisor assignment and does not show a compose form. Direct send attempts are redirected safely. Once an Agent is assigned, normal subject-scoped messaging becomes available.


## Customer Request Messages presentation

The Request Messages tab is the focused customer conversation workspace. It uses one
**Messages** title. Customer messages render as **You** at logical end; Agent messages use
the Agent user's full name or **Your advisor** at logical start; system events render as
centered **TurkDemy** notices. Every message shows both date and time on all responsive
layouts.

Desktop retains the Request context sidebar. At customer mobile widths the sidebar is
hidden so the thread and composer use the available width. The composer preserves the
existing `MessageForm`/send service while presenting an accessible **Attach file**
affordance and selected-file feedback instead of the browser file-input chrome.

## Locale-aware system messages

New workflow-generated system messages use `Message.event_type` plus JSON-safe
`Message.event_data` as their canonical event representation. `Message.body` is
retained as an English fallback snapshot. Product templates and inbox/detail
previews render `Message.localized_body`, which translates the event sentence in
the active locale and resolves localized structured values (for example Program
and University names) at display time.

Human-authored customer/Agent messages are never automatically translated.
Historical system messages without structured event metadata continue to display
their stored body unchanged.
