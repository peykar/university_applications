from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / "docs" / "specs"
REQ_RE = re.compile(r"^([A-Z][A-Z0-9]*-\d{3})\s+[—-]", re.MULTILINE)
TRACE_ROW_RE = re.compile(r"^\|\s*`?([A-Z][A-Z0-9]*-\d{3})`?\s*\|", re.MULTILINE)


def main() -> int:
    errors: list[str] = []
    owners: dict[str, list[Path]] = defaultdict(list)
    active = [p for p in sorted(SPECS.iterdir()) if p.is_dir() and p.name != "_template"]

    for capability in active:
        required_files = ("spec.md", "design.md", "tasks.md", "traceability.md")
        for name in required_files:
            if not (capability / name).is_file():
                errors.append(f"{capability.relative_to(ROOT)}: missing {name}")

        spec = capability / "spec.md"
        trace = capability / "traceability.md"
        if not spec.exists() or not trace.exists():
            continue
        reqs = REQ_RE.findall(spec.read_text(encoding="utf-8"))
        if not reqs:
            errors.append(f"{spec.relative_to(ROOT)}: no stable requirement IDs found")
            continue
        for req in reqs:
            owners[req].append(spec)

        traced = set(TRACE_ROW_RE.findall(trace.read_text(encoding="utf-8")))
        for req in reqs:
            if req not in traced:
                errors.append(f"{trace.relative_to(ROOT)}: missing requirement-level row for {req}")
        for req in sorted(traced - set(reqs)):
            errors.append(f"{trace.relative_to(ROOT)}: traces unknown requirement {req}")

    for req, files in sorted(owners.items()):
        if len(files) > 1:
            paths = ", ".join(str(p.relative_to(ROOT)) for p in files)
            errors.append(f"duplicate requirement ID {req}: {paths}")

    if errors:
        print("SDD validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    total = len(owners)
    print(
        f"SDD validation passed: {len(active)} capabilities, "
        f"{total} unique requirements fully traced."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
