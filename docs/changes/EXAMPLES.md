# Change-record examples

These are examples only; they are not active TurkDemy work items.

## Bug example

```text
BUG-0001-cross-agent-applicant-access

Requirement: PERM-003
Expected: Agent B context cannot access Agent A Applicant.
Actual: Applicant remains accessible after organization switch.
Process: regression test -> fix scoped queryset -> make check.
Spec change: none.
```

## Change example

```text
CHG-0001-finalization-permission

Current: ASN-006 allows only responsible Agent user to finalize.
Requested: any authorized Agent user may finalize.
Process: revise/approve ASN-006 -> design -> tasks -> implementation.
```

## Feature example

```text
FEAT-0001-application-requirements

Problem: structured university/Application requirement tracking does not yet
exist.
Process: discovery questions -> new/expanded APP/DOC spec -> approval -> design
-> tasks -> implementation.
```
