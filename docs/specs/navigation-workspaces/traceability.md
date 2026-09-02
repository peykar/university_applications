# Navigation and workspace information architecture — traceability

Status: BASELINED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `NAV-001` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `NAV-002` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `NAV-003` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `NAV-004` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `NAV-005` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `NAV-006` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `NAV-007` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `NAV-008` | `design.md` | Baseline verification: existing project tests; replace with named tests when this requirement changes. | Baseline |
| `NAV-009` | `templates/base.html`, `docs/navigation.md` | `NavigationArchitectureTests.test_footer_uses_current_customer_workspace_terminology` | Named test |

| `NAV-010` | `templates/customer/base.html`, `static/css/turkdemy.css`, `docs/navigation.md` | `NavigationArchitectureTests.test_customer_workspace_mobile_actions_do_not_clip` | Named style/structural test |
| `NAV-011` | `templates/agents/base.html`, `static/css/turkdemy.css`, `docs/navigation.md` | `NavigationArchitectureTests.test_agent_workspace_uses_shared_workspace_visual_system`; `AgentProgramRecommendationStructureTests.test_agent_workspace_uses_shared_shell_and_compact_overview` | Named structural/style tests |

## Notes

This baseline intentionally starts at capability level. When a requirement is
changed or newly implemented, replace the family row with requirement-level
code paths and named tests. Do not claim exact traceability that has not been
verified.
| `NAV-012` | `apps/leads/views.py`, `templates/leads/lead_section.html`, `static/css/turkdemy.css` | `CustomerRequestWorkspaceTests.test_empty_request_context_releases_secondary_column` | Named structural/runtime test |
