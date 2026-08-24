# Public Frontend

TurkDemy uses Django's server-rendered frontend as the primary website.

## Architecture

```text
Browser
  ↓
Django URL routing
  ↓
Django views/forms
  ↓
Django templates
  ↓
Models/services
```

There is no separate React/Vite application.

Django REST Framework remains available for external integrations, future
mobile clients, and API-specific use cases.

## Public routes

The public website is language-prefixed:

```text
/<lang>/
/<lang>/universities/
/<lang>/universities/<slug>/
/<lang>/programs/
/<lang>/programs/<slug>/
/<lang>/faq/
/<lang>/contact/
/<lang>/about/
/<lang>/dashboard/
/<lang>/profile/
/<lang>/accounts/login/
```

## Static files

Templates use Django's `{% static %}` template tag.

Project-wide static assets are located under:

```text
static/
└── css/
    └── turkdemy.css
```

`STATICFILES_DIRS` includes the repository-level `static/` directory.

## Internationalization

`LocaleMiddleware` and `i18n_patterns` provide EN/FA/TR/AR URL prefixes.
The base template includes a language selector and RTL page direction for
Persian and Arabic.
