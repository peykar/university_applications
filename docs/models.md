# TurkDemy Models

## accounts
- User

## agents
- Agent
- AgentDocument

## geography
- Country
- Province
- City

## universities
- University
- UniversityMedia
- Department
- ProgramLanguage
- AcademicYear
- Semester
- Program
- ProgramOffering

## students
- Student
- StudentDocument

## applications
- Application
- ApplicationDocument

## content
- FAQCategory
- FAQ
- ContactSubmission

## Key relationships

```text
Country → Province → City → University
University → Department
University → Program → ProgramOffering → Application
Agent → Student → Application
Student → StudentDocument → ApplicationDocument → Application
```
