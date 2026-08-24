# Dependency Audit

Third-party imports discovered in the Python code:

- `babel`
- `dj_database_url`
- `django`
- `httpx`
- `phonenumbers`
- `pycountry`
- `rest_framework`

Runtime dependencies declared:

- `Babel>=2.17,<3`
- `dj-database-url>=2.3,<3`
- `Django>=5.2,<6`
- `djangorestframework>=3.16,<4`
- `gunicorn>=23,<24`
- `phonenumbers>=9,<10`
- `pycountry>=24.6,<25`

Unmapped third-party imports:

- `httpx`

## Explicit runtime-only dependencies

- `httpx>=0.28,<1`
- `Pillow>=11,<12`
- `django-cors-headers>=4.7,<5`
- `psycopg[binary]>=3.2,<4`

These are required by runtime behavior even when not all appear as direct first-party imports.
