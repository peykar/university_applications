# Program interests and recommendations

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for program interests and recommendations.

## Requirements

PRG-001 — A customer MAY add a Program as an exploratory Lead interest.

PRG-002 — An Agent user in the Lead's active Agent scope MAY recommend an active
Program to an active Lead.

PRG-003 — An Agent recommendation MAY include a customer-understandable reason.

PRG-004 — Agent recommendation MUST use source `agent` and record the suggesting
Agent user.

PRG-005 — Recommending a program already present as a user-created program-level
interest MUST NOT overwrite or duplicate that user interest.

PRG-006 — Creating a recommendation MUST create a customer-visible
PROGRAM_SUGGESTED activity and an Applicant-scoped system message.

PRG-007 — Agent-created, unconverted recommendations MAY be removed while the
Lead is active; user-created interests MUST NOT be removed through this action.

PRG-008 — A Program interest MAY reference a concrete ProgramOffering but MUST
NOT be treated as a formal Application.

PRG-009 — Agent program search for recommendation MUST only return active
Programs whose Universities are active.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
