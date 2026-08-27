# <Capability name> — technical design

Status: DRAFT

## Requirement mapping

| Requirement | Design component |
|---|---|
| CAP-001 | ... |

## Domain model impact

State explicitly whether schema changes are required.

## Services

```text
service_name(...)
```

Define inputs, outputs, invariants and transaction boundary.

## Authorization

Describe how each object is resolved/scoped. Do not rely on UI hiding.

## Routes/API

| Method | Route | Purpose |
|---|---|---|
| ... | ... | ... |

## UI / navigation

Describe entry points, entity scope, empty/loading/error states and mobile
behavior.

## Side effects

- Activity/audit:
- Message/notification:
- Email:
- File mutation:

## Transactions and concurrency

What must succeed/fail atomically? What duplicate/race conditions are possible?

## Migration/data compatibility

- Schema migration:
- Backfill:
- Existing data behavior:

## Test strategy

- Unit:
- Integration:
- Authorization:
- Regression:

## ADR impact

State `No ADR required` or link the new/changed ADR.
