# DISC-0001 — Admission requirements capability

Status: OPEN / DEFERRED
Classification: DISCOVERY
Date: 2026-08-29

## Context

University catalogues may also carry academic/admission conditions such as
minimum GPA/percentage, IELTS/TOEFL, SAT/TR-YÖS, GRE/GMAT, portfolio/interview,
language-preparation, and credit-transfer rules.

## Decision for Catalogue v2

Do not encode these rules as ad-hoc Program or ProgramOffering pricing fields.
They require a separate capability/spec because scope may be university-wide,
degree-level, program-level, intake-specific, conditional, or document-based.

## Open design questions

- Which requirement scopes are required: University, Program, ProgramOffering,
  Degree, or combinations?
- Which requirements need typed numeric values versus free-text conditions?
- How should market/citizenship-specific requirements be represented?
- Which requirements are customer-visible versus agent-only?
- How are requirement versions/provenance linked to university source files?

No admission-requirement code is authorized by this discovery record.
