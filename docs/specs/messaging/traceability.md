# Generic messaging — traceability

Status: BASELINED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `MSG-001` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `MSG-002` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `MSG-003` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `MSG-004` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `MSG-005` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `MSG-006` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `MSG-007` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `MSG-008` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `MSG-009` | `apps/leads/views.py`, `templates/leads/lead_section.html`, generic Conversation invariant | `UnassignedCustomerRequestTests` | Named runtime tests |
| `MSG-010` | `design.md`; `MSG-T10`–`MSG-T11`; `apps/messaging/models.py`; `apps/messaging/services.py`; structured event producers and message presentation templates | `LocalizedSystemMessageTests`; existing messaging/workspace regressions | Named runtime tests |

## Notes

This baseline intentionally starts at capability level. When a requirement is
changed or newly implemented, replace the family row with requirement-level
code paths and named tests. Do not claim exact traceability that has not been
verified.
