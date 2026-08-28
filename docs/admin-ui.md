# Django admin UX conventions

The Django admin is an operational/support interface, not the Agent/customer product UI.

## List pages

For business models, prefer:

- `list_display` with the primary human identifier, ownership/status and useful timestamps;
- `search_fields` using names, email, titles and business identifiers rather than UUID-only lookup;
- `list_filter` for lifecycle/status, organization/owner and dates;
- `date_hierarchy` where one date is operationally important;
- `list_select_related` for foreign keys displayed on large lists;
- `autocomplete_fields` for foreign-key selection where the related admin supports search;
- 50-row pagination for operational/high-volume models.

## Inlines

Use an inline when the child is naturally understood in the context of one parent and loading the collection is expected to remain bounded. Use `show_change_link` when the child also has a useful standalone admin page.

Immutable history models may be inline, but must be read-only and non-deletable.

Do not inline very high-cardinality reverse collections merely because Django technically can. Examples include all Programs below a large University or all Cities below a Country. Those are more usable as searchable/filterable standalone lists.

Generic-subject operations (TODOs and Communication Logs) remain standalone/global admin records in V1; the product workspace supplies their contextual subject UI.
