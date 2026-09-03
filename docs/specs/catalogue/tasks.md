# University and program catalogue — tasks

Status: APPROVED
Version: 3.1

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

- [x] CAT-T19 (`CAT-031`) Add Program `internal_notes`, expose it only in staff
      maintenance/import paths, support it in schema-v1 JSON imports, and add
      regression coverage proving it is absent from public/customer/API surfaces.

- [x] CAT-T20 (`CAT-032`) Add the one-ID `dump_university_data` command, versioned
      catalogue export contract, documentation, and tests covering localized
      programme text, catalogue relationships, default/custom output paths, and
      unknown-University rejection.

- [x] CAT-T21 (`CAT-033`) Enable Unicode validation for Persian/Turkish/Arabic
      localized slugs in the shared catalogue/geography slug contract, preserve
      ASCII validation for `slug_en`, document JSON-import behavior, and add
      model/admin-routing regression coverage.

- [x] CAT-T22 (`CAT-034`) Make shared localized slug fields optional for admin entry,
      auto-generate missing slugs from matching localized names during model
      validation/save, preserve explicit slugs, cover `FAQCategory.key`, and add
      regression coverage across catalogue, geography, and current content slugs.

- [x] CAT-T23 (`CAT-035`, `CAT-036`) Add canonical Intake with university/year/date validation while retaining Semester as a compatibility bridge.
- [x] CAT-T24 (`CAT-037`–`CAT-039`) Add normalized, optionally language-aware OfferingFee and expand fee bases.
- [x] CAT-T25 (`CAT-040`) Make normalized university JSON imports create Intake and structured fee rows while translating legacy fee columns during transition.
- [x] CAT-T26 (`CAT-035`–`CAT-040`) Expose Intake and structured fees in Django Admin and document the v3 transition.
- [x] CAT-T27 (`CAT-041`) Make structured OfferingFee data primary in Django Admin,
      add a structured-fee summary to Program offering inlines, collapse legacy
      fixed pricing/Semester fields into a clearly labelled compatibility section,
      add direct OfferingFee administration, and cover the admin configuration.

- [x] CAT-T28 (`CAT-042`) Order Django Admin structured-fee summaries by stable
      fee semantics, including Tuition → Advance payment → Preparatory/Foundation,
      with regression coverage.

- [x] CAT-T29 (`CAT-043`) Migrate public catalogue filters/detail/cards, customer
      Request/Application displays, agent/student displays, Application admin, and
      ProgramOffering API serialization from legacy Semester/fixed pricing reads to
      canonical Intake/OfferingFee data; add regression coverage preventing v2 UI reads.

- [x] CAT-T30 (`CAT-044`) Remove Semester, legacy Program language/duration fields,
      fixed ProgramOffering pricing/currency/basis fields, compatibility fallback
      code, the old backfill command, and Catalogue-v2 regression tests.
- [x] CAT-T31 (`CAT-045`) Move Application tuition/deposit snapshots to active
      structured OfferingFee data and reject Application creation without tuition.
- [x] CAT-T32 (`CAT-046`, `CAT-047`) Make normalized JSON and Rasa catalogue
      imports v3-native, using Intake + OfferingFee only.
- [x] CAT-T33 (`CAT-048`) Remove legacy Admin/export presentation and update
      catalogue/import/export documentation and regression coverage.
- [x] CAT-T34 (`CAT-049`) Add `prepare_catalogue_v3_cutover` and operator docs so
      existing databases can backfill missing v3 data before locally generated
      destructive migrations remove Catalogue v2 storage.
- [x] CAT-T35 (`CAT-050`) Rebuild localized Program public slugs from structured University, optional Academic Unit/Department, Program name, degree, thesis type, and instruction-language data with the
      localized University prefix, include thesis/non-thesis for graduate variants,
      make them globally unique, preserve existing hierarchy components with an
      English fallback when a localized hierarchy translation is missing, keep
      normalized imports transition-safe/idempotent, add `rebuild_program_slugs --dry-run`,
      make rebuild collisions resolve with deterministic numeric tails and report every resolution,
      make ordinary Program saves/import language synchronization allocate stable numeric tails instead of failing unique constraints,
      document the rollout, and add regression coverage.
- [x] CAT-T36 (`CAT-013`, `CAT-037`, `CAT-038`, `CAT-043`) Preserve structured
      fee semantics in the public offering price presentation: label the promoted
      tuition price, show source/structured percentages exactly once, display fee
      basis alongside every amount-bearing fee, and add rendered-page regression
      coverage for list, scholarship/discounted, advance-payment, and deposit fees.
- [x] CAT-T37 (`CAT-043`) Refine Similar-program card tuition copy to present
      the existing minimum active tuition annotation as customer-facing “Tuition
      from” wording, without changing catalogue pricing/filter semantics, and add
      regression coverage that prevents the internal phrase from returning.
- [x] CAT-T38 (`CAT-051`) Add a read-only persisted Catalogue v3 audit command with
      human/JSON/CSV reports, optional error exit status, operator documentation,
      and regression coverage for Application readiness, clean structured tuition,
      and public provenance leakage.

- [x] CAT-T39 (`CAT-043`) Remove the stale Catalogue v2 homepage tuition lookup and
  source Popular-program pricing exclusively from active structured `OfferingFee`
  rows through the canonical Catalogue v3 tuition annotation helper.

- [x] CAT-T40 (`CAT-052`, `I18N-001`) Keep public field-filter query identities on
      canonical `slug_en`, deduplicate repeated Department slugs for presentation,
      localize only their labels, exclude fields backed only by inactive Universities,
      align homepage study-field links/counts with the active catalogue, and add
      regression coverage for canonical-vs-localized slug behavior.


- [x] CAT-T41 (`CAT-053`, `CAT-054`) Add global multilingual/SEO-ready
      `GeneralField` and optional many-to-many `Program.general_fields` without changing
      AcademicUnit/Department semantics.
- [x] CAT-T42 (`CAT-056`) Add GeneralField Django Admin management and expose
      manual Program multi-field mapping with list/filter/search/autocomplete support.
- [x] CAT-T43 (`CAT-055`) Move public field choices, field filtering and homepage
      field discovery from repeated Department slugs to GeneralField.
- [x] CAT-T44 (`CAT-057`) Keep `import_programs_for_university` GeneralField-neutral:
      reject import-supplied mapping, leave new Programs unmapped and preserve existing
      manual assignments on re-import.
- [x] CAT-T45 (`CAT-053`–`CAT-058`) Update catalogue/business/domain/import docs and
      record the field-landing-page boundary for the later SEO phase.
- [x] CAT-T46 (`CAT-055`, `CAT-057`) Add regression coverage for canonical field
      filtering, localized labels, inactive catalogue exclusion, no Department
      fallback, new-import empty mapping, re-import preservation and import rejection.
- [x] CAT-T47 (`CAT-059`) Add localized editorial/SEO metadata to City and expose it in Django Admin.
- [x] CAT-T48 (`CAT-060`) Add the one-time `enrich_taxonomy` command with transactional dry-run, 24 curated GeneralFields, Istanbul enrichment, and UUID-pinned mappings for the exported active catalogue.


## CHG-0019 — GeneralField landing pages

- [x] CAT-T49 (`CAT-061`) Add `/programs/fields/<slug_en>/` before the generic Program detail route.
- [x] CAT-T50 (`CAT-062`) Render localized GeneralField editorial content, mapped Programs, University coverage and pagination.
- [x] CAT-T51 (`CAT-063`) Link homepage fields to the landing route and add canonical/hreflang, schema and sitemap behavior.
- [x] CAT-T52 (`CAT-061`–`CAT-063`) Add public metadata/SEO regression tests and synchronized documentation.
- [ ] Run `make format` and `make check` locally.

## CHG-0020 — City landing pages

- [x] CAT-T53 (`CAT-064`) Add `/universities/cities/<slug_en>/` before the generic University detail route.
- [x] CAT-T54 (`CAT-065`) Render localized City editorial content, paginated active Universities and representative Programs with a canonical city-filter discovery link.
- [x] CAT-T55 (`CAT-066`) Add City canonical/hreflang, structured data, sitemap inclusion and crawlable University-detail internal linking.
- [x] CAT-T56 (`CAT-064`–`CAT-066`) Add public metadata/SEO regression tests and synchronized documentation.
- [x] User verified CHG-0020.

## CHG-0021 — City banner media

- [x] CAT-T57 (`CAT-067`) Add optional City banner storage, localized alt text and localized fallback behavior.
- [x] CAT-T58 (`CAT-067`) Add City Admin upload/preview and localized alt editing.
- [x] CAT-T59 (`CAT-067`, `SEO-017`) Render the responsive City banner and reuse it for social/structured-data image metadata.
- [x] CAT-T60 (`CAT-067`, `SEO-017`) Add regression tests, SEO review and synchronized documentation.
- [ ] Run `make format` and `make check` locally.


## CHG-0022 — Homepage City discovery integration

- [x] CAT-T61 (`CAT-068`) Add a top-five active City destination query with distinct active University and Program counts.
- [x] CAT-T62 (`CAT-068`) Render localized City destination cards between Featured Universities and GeneralField discovery, linking to canonical City landing pages and reusing curated banners.
- [x] CAT-T63 (`CAT-068`, `SEO-018`) Add responsive/mobile presentation, translations, public-page regression coverage, and synchronized SEO/documentation updates.
- [ ] Run `make format` and `make check` in the project environment.

## CHG-0023 — Discovery-to-Request conversion and internal linking

- [x] CAT-T64 (`CAT-069`, `SEO-019`) Link Program City and active GeneralFields to their canonical public landing pages.
- [x] CAT-T65 (`CAT-069`) Prefetch Program GeneralFields for the detail surface and preserve existing University/related-program discovery.
