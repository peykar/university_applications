# Public SEO — traceability

Status: BASELINED

| Requirement | Primary implementation area | Verification | Coverage |
|---|---|---|---|
| `SEO-001` | `AGENTS.md`; `docs/product/business-rules.md` | `tests/test_public_seo.py` | Automated |
| `SEO-002` | `apps/public/context_processors.py`; `templates/base.html` | `tests/test_public_seo.py` | Automated |
| `SEO-003` | `apps/public/context_processors.py`; `templates/base.html` | `tests/test_public_seo.py` | Automated |
| `SEO-004` | `apps/public/context_processors.py` | `tests/test_public_seo.py` | Automated |
| `SEO-005` | `apps/public/context_processors.py`; `templates/base.html` | `tests/test_public_seo.py` | Automated |
| `SEO-006` | `apps/public/seo_views.py`; `turkdemy/urls.py` | `tests/test_public_seo.py` | Automated |
| `SEO-007` | `apps/public/seo_views.py`; catalogue models | `tests/test_public_seo.py` | Automated |
| `SEO-008` | `templates/base.html` | `tests/test_public_seo.py` | Automated |
| `SEO-009` | repository SDD/SEO contract | `tests/test_public_seo.py` | Automated |
| `SEO-010` | public templates; locale catalogues | `tests/test_public_page_metadata.py` | Automated |
| `SEO-011` | `templates/base.html`; public templates/views | `tests/test_public_page_metadata.py` | Automated |
| `SEO-012` | `apps/public/seo.py`; `apps/public/views.py` | `tests/test_public_page_metadata.py` | Automated |
| `SEO-013` | `apps/public/views.py` | `tests/test_public_page_metadata.py` | Automated |
| `SEO-014` | `apps/public/templatetags/seo.py`; `apps/public/seo.py` | `tests/test_public_page_metadata.py` | Automated |

| `SEO-015` | `apps/public/context_processors.py`; `apps/public/seo_views.py`; `apps/public/views.py::program_field_detail`; `templates/public/program_field_detail.html`; `templates/public/home.html` | `tests/test_public_seo.py`; `tests/test_public_page_metadata.py` | Automated |
| `SEO-016` | `apps/public/context_processors.py`; `apps/public/seo_views.py`; `apps/public/views.py::university_city_detail`; `templates/public/university_city_detail.html`; `templates/public/university_detail.html` | `tests/test_public_seo.py`; `tests/test_public_page_metadata.py` | Automated |
| `SEO-017` | `apps/geography/models.py::City`; `apps/public/views.py::university_city_detail`; `templates/public/university_city_detail.html`; `templates/base.html` | `tests/test_public_page_metadata.py`; `tests/test_taxonomy_enrichment.py` | Automated |

