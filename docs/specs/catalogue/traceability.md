# University and program catalogue — traceability

Status: IMPLEMENTED / LOCAL VERIFICATION REQUIRED
Version: 2.0

| Requirement | Design | Tasks | Implementation | Verification |
|---|---|---|---|---|
| `CAT-001` | Program ownership | Baseline | `apps/universities/models.py::Program` | existing catalogue tests |
| `CAT-002` | Department same-University invariant | Baseline | `Program.clean()` | existing model/workflow tests |
| `CAT-003` | ProgramOffering intake boundary | Baseline | `ProgramOffering` | existing offering/filter tests |
| `CAT-004` | University recognition ownership | Baseline | `University` | existing catalogue tests |
| `CAT-005` | Internal listing priority | Baseline | `Program.listing_priority`, `University.listing_priority` | existing public catalogue tests |
| `CAT-006` | Catalogue filters | Baseline | `apps/public/services/program_filters.py` | `tests/test_program_filters.py` |
| `CAT-007` | AcademicUnit model | `CAT-T01` | `AcademicUnit`, `AcademicUnitType`, admin | `CatalogueV2Tests.test_academic_unit_must_belong_to_program_university` |
| `CAT-008` | Program AcademicUnit invariant | `CAT-T01` | `Program.academic_unit`, `Program.clean()` | `CatalogueV2Tests.test_academic_unit_must_belong_to_program_university` |
| `CAT-009` | Multi-language instruction | `CAT-T02` | `ProgramInstructionLanguage`, `Program.instruction_languages` | `CatalogueV2Tests.test_mixed_languages_and_fractional_duration_are_canonical` |
| `CAT-010` | Percentage validation | `CAT-T02` | validators, admin inline formset, importer guard | `CatalogueV2Tests.test_instruction_language_percentage_is_bounded` plus admin/import structural coverage |
| `CAT-011` | Study mode | `CAT-T03` | `Program.study_mode`, filters/admin/importer/public detail | `CatalogueV2Tests.test_language_filter_matches_any_canonical_instruction_language` |
| `CAT-012` | Fraction-safe duration | `CAT-T04` | `duration_months`, `duration_display`, importer conversion/backfill | `CatalogueV2Tests.test_import_helpers_preserve_fractional_duration_and_mixed_languages`; `test_legacy_fields_backfill_without_losing_meaning` |
| `CAT-013` | Pricing semantics | `CAT-T07` | existing structured fields + explicit admin/API/public labels | `CatalogueV2Tests.test_source_and_offering_keep_pricing_semantics_and_provenance` |
| `CAT-014` | Preparatory tuition rename | `CAT-T05` | `preparatory_tuition` mapped to legacy DB column `pre_school_fees` | `CatalogueV2Tests.test_source_and_offering_keep_pricing_semantics_and_provenance` |
| `CAT-015` | Preparation inclusion/notes | `CAT-T07` | `preparation_included`, `notes` | `CatalogueV2Tests.test_source_and_offering_keep_pricing_semantics_and_provenance` |
| `CAT-016` | UniversityCatalogueSource | `CAT-T06` | model + admin/file/recorded-by support | `CatalogueV2Tests.test_source_and_offering_keep_pricing_semantics_and_provenance` |
| `CAT-017` | Offering provenance | `CAT-T06` | protected optional `ProgramOffering.source`, same-University validation | `CatalogueV2Tests.test_offering_rejects_source_from_other_university` |
| `CAT-018` | Offering validity | `CAT-T07` | `valid_from`, `valid_until`, model validation | catalogue v2 model tests |
| `CAT-019` | Offering maintenance | `CAT-T08` | expanded offering inline/admin fieldsets | catalogue v2 structural/admin coverage |
| `CAT-020` | Program maintenance | `CAT-T01`–`CAT-T08` | Program admin + language inline | catalogue v2 structural/admin coverage |
| `CAT-021` | Compatibility migration | `CAT-T02`, `CAT-T04`, `CAT-T05`, `CAT-T11` | legacy language/duration bridges, DB-column-preserving preparatory rename, `backfill_catalogue_v2` | `CatalogueV2Tests.test_legacy_fields_backfill_without_losing_meaning`; updated Rasa tests |
| `CAT-022` | Import mapping/no guessing | `CAT-T03`, `CAT-T04`, `CAT-T09` | Rasa mixed-language/fractional-duration/study-mode mappings and unmapped-note preservation | importer helper tests + `tests/test_rasa_importers.py` |
| `CAT-023` | Canonical public consumers | `CAT-T03`, `CAT-T04`, `CAT-T10` | public filters/detail/cards, Request/Agent templates, API serializers | `tests/test_program_filters.py`, Request structural tests, catalogue v2 tests |
| `CAT-024` | Admission-requirements boundary | `CAT-T13` | no admission-requirement fields added; `DISC-0001` records deferred capability | SDD/document review |

## Verification status

Repository-level SDD validation passes. Full Django/pytest verification must be
run in the normal project environment because the delivery sandbox cannot fetch
the locked Python dependencies from PyPI. The implementation deliberately keeps
legacy `Program.program_language` and `Program.duration` as compatibility
bridges until production data has been backfilled and downstream integrations
have moved to the canonical structures.
