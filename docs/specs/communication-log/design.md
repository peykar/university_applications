# Communication Log — Design

`apps.operations.CommunicationLog` is Agent-owned with an optional generic
canonical subject. `performed_by` identifies the Agent user who actually made
the communication; `occurred_at` is independent from audit `created_at`.

`CommunicationLogRevision` stores immutable snapshots of editable fields before
each edit. Updates go through a service that checks creator ownership and writes
the revision before updating the entry.

Messages remain in `apps.messaging`; Communication Log remains in
`apps.operations`.

The same generic subject/parent aggregation service used by TODOs powers
contextual Communication Log tabs.

"Create TODO" copies the Communication Log's Agent and canonical subject and can
prefill the TODO title/description.
