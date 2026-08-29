# University and program catalogue — traceability

Status: APPROVED / NOT YET IMPLEMENTED
Version: 2.0

| Requirement | Design | Tasks | Verification |
|---|---|---|---|
| `CAT-001` | Existing Program ownership | `Existing baseline` | Existing baseline tests |
| `CAT-002` | Department same-University invariant | `Existing baseline` | Existing baseline tests |
| `CAT-003` | ProgramOffering intake boundary | `Existing baseline` | Existing baseline tests |
| `CAT-004` | University recognition ownership | `Existing baseline` | Existing baseline tests |
| `CAT-005` | Internal listing priority | `Existing baseline` | Existing baseline tests |
| `CAT-006` | Catalogue filters | `Existing baseline` | Existing baseline tests |
| `CAT-007` | AcademicUnit model | `CAT-T01, CAT-T12` | Pending named tests |
| `CAT-008` | Program AcademicUnit invariant | `CAT-T01, CAT-T12` | Pending named tests |
| `CAT-009` | ProgramInstructionLanguage | `CAT-T02, CAT-T12` | Pending named tests |
| `CAT-010` | Language percentage validation | `CAT-T02, CAT-T12` | Pending named tests |
| `CAT-011` | Program study mode | `CAT-T03, CAT-T12` | Pending named tests |
| `CAT-012` | Fraction-safe duration | `CAT-T04, CAT-T11, CAT-T12` | Pending migration/display tests |
| `CAT-013` | Offering pricing semantics | `CAT-T07, CAT-T12` | Pending pricing tests |
| `CAT-014` | Preparatory tuition rename | `CAT-T05, CAT-T11` | Pending migration tests |
| `CAT-015` | Preparation inclusion and notes | `CAT-T07, CAT-T12` | Pending model/admin tests |
| `CAT-016` | UniversityCatalogueSource | `CAT-T06, CAT-T12` | Pending provenance tests |
| `CAT-017` | Offering source provenance | `CAT-T06, CAT-T12` | Pending provenance tests |
| `CAT-018` | Offering validity | `CAT-T07, CAT-T12` | Pending validity tests |
| `CAT-019` | Offering maintenance UI | `CAT-T08, CAT-T12` | Pending form/admin tests |
| `CAT-020` | Program maintenance UI | `CAT-T01, CAT-T02, CAT-T03, CAT-T04, CAT-T08` | Pending form/admin tests |
| `CAT-021` | Compatibility migration strategy | `CAT-T02, CAT-T04, CAT-T05, CAT-T11` | Pending migration tests |
| `CAT-022` | Importer mapping/no-guess rule | `CAT-T03, CAT-T04, CAT-T09` | Pending importer tests |
| `CAT-023` | Canonical public consumers | `CAT-T03, CAT-T04, CAT-T10` | Pending catalogue/request UI tests |
| `CAT-024` | Admission-requirements boundary | `CAT-T13` | Separate spec/discovery required before code |

## Verification status

This change is specification/design only. No v2 implementation is claimed.
Existing v1 behavior remains the executable baseline until the tasks above are
implemented and verified. Requirement-level implementation paths will replace
`Pending` entries as each task lands.
