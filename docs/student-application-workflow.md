# Student → Application workflow

A Lead program interest is exploratory. A formal Application is created only
after the Lead has been finalized into a Student and an agent deliberately
starts an application for a concrete `ProgramOffering`.

## Relationships

`Student -> Application -> ProgramOffering -> Program -> University`

The originating Lead remains historical. Its `LeadProgramInterest` records are
shown on the Student workspace under **Programs discussed during applicant
stage**.

## Starting from a discussed program

If the Lead interest already contains a concrete offering/intake, **Start
application** creates a Draft Application for that offering.

If the Lead interest is program-level only, the agent must first choose one of
that Program's active offerings. The created Application is linked back through
`LeadProgramInterest.converted_application`.

## Creating a new application

Agents can use **New application** on the Student workspace for a program that
was never discussed during the Lead stage. The agent selects a concrete active
ProgramOffering and the Application starts as Draft.

## Creation rules

`create_student_application()` is the canonical service. It:

- requires a Student and concrete ProgramOffering;
- validates that a source Lead interest belongs to the Student and Program;
- prevents a second active Application for the same Student + ProgramOffering;
- copies tuition and deposit from the offering;
- sets the Student's Agent;
- creates the Application as Draft;
- links a source LeadProgramInterest when applicable.

Rejected, Withdrawn, and Cancelled Applications are considered inactive for the
duplicate check.

StudentDocuments remain reusable master documents. ApplicationDocument can
reference the StudentDocuments selected for a specific university application.


## Document workflow

Agents can upload reusable master documents directly from the Student workspace.
This creates `StudentDocument`.

On an Application, **Add document** can either:

1. reuse an existing StudentDocument that is not already linked to that
   Application, creating `ApplicationDocument`; or
2. upload a new file, which first creates a reusable StudentDocument and then
   links it to the current Application.

Agent-side uploads and selections are marked verified. The displayed document
type links directly to the stored file; the underlying filename is available
as the link tooltip.
