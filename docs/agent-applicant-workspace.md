# Agent applicant workspace

## Overview

The Applicant Overview is intentionally a summary page. It keeps the applicant
identity, assignment and lifecycle controls visible, then links to the focused
entity areas:

- Profile
- Programs
- Documents
- Applications
- Messages
- Activity

The previous full Conversation, Documents, Internal notes and Programs panels
remain implemented in their focused destinations instead of being duplicated
visually on Overview.

## Program recommendations

Agent users can recommend programs from the Applicant **Programs** tab.

1. Open Applicant → Programs.
2. Select **Recommend a program**.
3. Search by program or university name.
4. Optionally enter a short reason that the applicant can understand.
5. Select **Recommend**.

A recommendation creates a `LeadProgramInterest` with `source="agent"` and
`suggested_by` set to the current Agent user. It also creates a
`PROGRAM_SUGGESTED` activity and sends an applicant-scoped system message.

If the applicant already added the same program, the system does not overwrite
their user-added interest. Agent recommendations can be removed until the Lead
is finalized or closed. Converted/formalized interests are not removable.

## Layout

Agent Applicant pages use the shared TurkDemy workspace shell rather than an
Agent-only wide canvas. The standard site container, sidebar geometry, heading
hierarchy, entity navigation, responsive behavior, and RTL treatment match My
TurkDemy. Applicant-specific panels and tables may remain denser inside the shared
content column when the workflow requires it.
