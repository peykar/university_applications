# University and program catalogue — traceability

Status: IMPLEMENTED / LOCAL VERIFICATION REQUIRED
Version: 2.4

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
| `CAT-025` | Normalized per-University JSON import | `CAT-T16` | `apps/universities/management/commands/import_programs_for_university.py` | `UniversityProgramJsonImportTests.test_source_must_belong_to_university_before_any_import_writes` |
| `CAT-026` | Versioned JSON contract | `CAT-T16` | command schema validation; `docs/university-program-json-import.md`; `docs/examples/university-programs-v1.json` | university-program JSON importer tests |
| `CAT-027` | Deterministic idempotent upserts | `CAT-T17` | Program/AcademicUnit/Department slug keys; Offering Program+year+semester+source key | `UniversityProgramJsonImportTests.test_reimport_updates_program_and_offering_without_duplicates` |
| `CAT-028` | Authoritative languages/source provenance | `CAT-T17` | `_sync_languages`; `_upsert_offering` source binding | `UniversityProgramJsonImportTests.test_import_creates_program_academic_unit_languages_and_source_bound_offering` |
| `CAT-029` | Atomic validation/no deletion | `CAT-T16`, `CAT-T17` | `transaction.atomic`; schema/reference validation; duplicate-match guards | source mismatch + invalid percentage rollback tests |
| `CAT-030` | Docs/example/tests | `CAT-T18` | importer docs/example + `tests/test_university_program_json_import.py` | named importer tests |
| `CAT-031` | Program internal notes | `CAT-T19` | `Program.internal_notes`; Program admin; normalized JSON importer | `UniversityProgramJsonImportTests`; `ProgramInternalNotesVisibilityTests` |
| `CAT-032` | University catalogue JSON dump | `CAT-T20` | `apps/universities/management/commands/dump_university_data.py` | `UniversityDataDumpTests` |
| `CAT-033` | Native Unicode localized slugs | `CAT-T21` | `apps/core/mixins.py`; existing `<str:slug>` catalogue routes; normalized importer model validation | `UnicodeLocalizedCatalogueSlugValidationTests`; `UnicodeCatalogueSlugRoutingTests` |

## Verification status

The user verified the Catalogue v2 baseline with local `make check` after applying
the required migrations/backfill. The normalized JSON-import extension has
repository-level verification in the delivery sandbox; its Django/pytest tests
must be re-run with local `make check` because the delivery sandbox does not have
the locked project dependencies installed. Legacy `Program.program_language` and
`Program.duration` remain compatibility bridges while canonical fields are used
by the importer and readers.
