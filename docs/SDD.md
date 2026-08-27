# Spec-driven development at TurkDemy

## Start a feature

Copy `docs/specs/_template/` to a capability directory or add requirements to an
existing capability.

Example:

```bash
cp -R docs/specs/_template docs/specs/document-requirements
```

Then rename `CAP-*` IDs to the capability prefix allocated in
`docs/specs/README.md`.

## Prompt/workflow contract

A useful agent workflow is:

1. **Spec only** — "Draft/change the spec. Do not implement."
2. Review and resolve `OPEN` decisions.
3. **Design only** — "Spec approved. Create/update technical design."
4. Review architecture and ADR impact.
5. **Tasks only** — "Create implementation tasks mapped to requirement IDs."
6. **Implementation** — "Implement tasks X–Y only."
7. **Verification** — run checks and update traceability/gap report.

## Change an existing feature

Do not start in code. First identify the owning capability and requirement IDs.

If behavior changes:

1. change `spec.md`;
2. approve the behavioral change;
3. update `design.md`;
4. update tasks;
5. implement;
6. update tests/traceability.

If only implementation changes without observable behavior change, the existing
spec can remain unchanged but design/tasks/traceability should reflect the
refactor.

## Resolve a code/spec conflict

Stop implementation. Record the conflict. Decide whether:

- code is wrong → fix code to approved spec;
- spec is wrong/outdated → explicitly revise/approve spec first;
- behavior is undecided → mark OPEN and defer dependent implementation.

Never silently rewrite the spec to justify current code.

## Definition of done

A behavioral change is done when requirements, design, implementation, tests,
traceability and documentation agree and `make check` passes.


## When a bug/change/feature arrives

Start with `docs/changes/README.md`, not with code.

```text
Does approved/baselined spec already define desired behavior?
├── yes, code violates it -> BUG
├── yes, desired behavior is different -> CHANGE
└── no
    ├── behavior is clear -> FEATURE
    └── behavior is unclear -> DISCOVERY
```

Pure visual/copy work can be UI. Behavior-preserving implementation work is a
REFACTOR. If code and spec disagree and the desired behavior is unclear, create
a CONFLICT record and stop dependent implementation.

For substantial work, copy the matching template from
`docs/changes/_templates/`.
