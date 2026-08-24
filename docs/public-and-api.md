# Public Workflows and API

## Django public pages

Server-rendered routes include:

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

The contact page writes `ContactSubmission`.

The profile page creates/updates the authenticated user's `Student` profile.

The dashboard lists that student's applications.

## REST API

Initial read-only endpoints:

```text
/api/v1/universities/
/api/v1/universities/<slug>/
/api/v1/programs/
/api/v1/programs/<slug>/
/api/v1/offerings/
/api/v1/faq-categories/
/api/v1/faqs/
```

Django REST Framework is installed as the API foundation.

## CORS

Allowed browser origins are configured through:

```dotenv
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

This supports a separately hosted React/Vite frontend.
