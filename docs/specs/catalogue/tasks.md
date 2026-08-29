# University and program catalogue — tasks

Status: APPROVED
Version: 2.1

- [x] CAT-T01 (`CAT-007`, `CAT-008`, `CAT-020`) Add AcademicUnit model,
      validation, admin maintenance, and Program association.
- [x] CAT-T02 (`CAT-009`, `CAT-010`, `CAT-021`) Add
      ProgramInstructionLanguage through model and data-preserving legacy
      language migration.
- [x] CAT-T03 (`CAT-011`, `CAT-020`, `CAT-022`, `CAT-023`) Add study mode,
      importer mapping, admin display, public presentation/filter support.
- [x] CAT-T04 (`CAT-012`, `CAT-021`, `CAT-022`, `CAT-023`) Introduce canonical
      fraction-safe duration, migrate existing values, update displays/imports.
- [x] CAT-T05 (`CAT-014`, `CAT-021`) Rename/migrate `pre_school_fees` to
      `preparatory_tuition` without data loss.
- [x] CAT-T06 (`CAT-016`, `CAT-017`) Add UniversityCatalogueSource, source file
      handling, same-University validation, and admin maintenance.
- [x] CAT-T07 (`CAT-013`, `CAT-015`, `CAT-018`) Extend ProgramOffering with
      preparation inclusion, notes, validity, and formal pricing semantics.
- [x] CAT-T08 (`CAT-019`, `CAT-020`) Redesign catalogue admin/agent forms so all
      approved Program and Offering fields are maintainable and validated.
- [x] CAT-T09 (`CAT-022`) Update Rasa/import mapping and fixtures; preserve
      ambiguous unsupported source values rather than guessing.
- [x] CAT-T10 (`CAT-023`) Update public program detail/list/filter consumers and
      any Request/Application program displays to canonical fields.
- [x] CAT-T11 (`CAT-021`) Add migration/regression tests proving existing
      Program, Offering, Application and LeadProgramInterest references/data are
      preserved.
- [x] CAT-T12 (`CAT-007`–`CAT-023`) Add named model, form/admin, importer and
      public catalogue tests and update traceability to concrete paths.
- [x] CAT-T13 (`CAT-024`) Create a separate discovery/spec before implementing
      Admission Requirements or credit-transfer structure.
- [x] CAT-T14 Update `docs/models.md`, `docs/rasa-mapping.md`,
      `docs/program-detail.md`, `docs/program-filters.md`, and relevant admin
      documentation after implementation.
- [x] CAT-T15 Run `make format` and `make check`; user verified the Catalogue v2 baseline passes locally.
- [x] CAT-T16 (`CAT-025`, `CAT-026`, `CAT-029`) Define schema-v1 normalized university-programme JSON and implement the three-argument atomic management command.
- [x] CAT-T17 (`CAT-027`, `CAT-028`) Implement deterministic upsert keys, exact Program instruction-language synchronization, and source-bound Offering updates.
- [x] CAT-T18 (`CAT-030`) Add command tests, contract documentation, a complete example JSON file, and change documentation.
