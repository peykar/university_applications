# BUG-0015 — University data dump test duplicated canonical language row

## Problem

`UniversityDataDumpTests.setUp()` created a `Program` with the legacy `program_language`
compatibility field and then explicitly created the same canonical
`ProgramInstructionLanguage` row. `Program.save()` already backfills that canonical row
when `program_language` is set, so the explicit create violated the unique constraint on
`(program, language)`.

## Fix

The dump fixture now creates the program without the legacy `program_language` bridge and
then explicitly creates its canonical `ProgramInstructionLanguage` row. This keeps the
fixture focused on the canonical catalogue-v2 representation that the dump command is
intended to serialize.

## Regression

The three `UniversityDataDumpTests` can now reach the dump-command assertions instead of
failing during fixture setup.
