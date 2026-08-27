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

Agent workspace pages use a wider desktop shell than public catalogue pages.
The workspace expands up to 1500px while retaining responsive breakpoints for
tablet and mobile. This gives Applicant and Application entity pages enough room
for their sidebar, data panels and forms without leaving excessive unused
horizontal space.
