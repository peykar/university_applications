# TODO Management — Design

`apps.operations.Todo` is Agent-owned and uses an optional generic canonical
subject (`subject_content_type`, `subject_object_id`, `GenericForeignKey`).
Generic subjects are deliberately not restricted to Lead/Application.

`TodoComment` is append-only in V1. Model validation prevents mutation after
creation.

Global queries are always scoped by the active Agent organization. Assignees
must be users of the owning Agent.

Parent aggregation is implemented in the operations service layer. For a Lead,
the scope contains the Lead plus Applications belonging to its converted
Student. For an Application, the scope contains that Application.

Lifecycle transitions are service operations so completion metadata is
consistent and reopening clears completion metadata.

No reminder scheduler and no attachments are part of V1.
