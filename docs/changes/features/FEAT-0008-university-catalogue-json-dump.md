# FEAT-0008 — University catalogue JSON dump

## Summary

Added `dump_university_data`, a one-required-input management command that exports
all catalogue-domain data for a University as versioned UTF-8 JSON for offline
matching/enrichment, especially Rasa-to-official catalogue text enrichment.

## Behavior

- Required input: University UUID only.
- Optional `--output` selects the destination.
- Default output: `university_<uuid>_catalogue.json`.
- Includes localized University/geography, media, units, departments, sources,
  Programs, internal notes, instruction languages, and offerings.
- Excludes applicant/student/application/message/customer operational data.
- Preserves UUID references, decimal precision, and source/offering structure.

## SDD

Catalogue v2.3 adds CAT-032 and CAT-T20.
