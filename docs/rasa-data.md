# RasaStudy Data Download

TurkDemy includes:

```text
scripts/download_rasastudy.py
```

It downloads the public RasaStudy catalogue into `data/rasa/`.

## Data downloaded

- universities
- programs
- FAQ categories
- FAQs
- same-site files referenced by those records, including images, documents,
  audio and video assets

## Run

```bash
uv run python scripts/download_rasastudy.py --output data/rasa
```

or:

```bash
make rasa-download
```

## Output

```text
data/rasa/
├── universities.json
├── programs.json
├── faq_categories.json
├── faqs.json
├── universities/
├── programs/
├── faq_categories/
├── faqs/
├── assets/
├── raw/
├── assets_discovered.json
├── assets_manifest.json
└── summary.json
```

## FAQ endpoint detection

RasaStudy has used different FAQ endpoint spellings across versions. The
downloader tries several public candidates and validates the JSON shape.

Expected category payloads use one of:

```text
cats
categories
faq_categories
```

Expected FAQ payloads use one of:

```text
faqs
faq
```

If automatic discovery stops working, supply the endpoint explicitly:

```bash
uv run python scripts/download_rasastudy.py   --faq-url https://rasastudy.com/api/v1/...   --faq-categories-url https://rasastudy.com/api/v1/...
```

The old Rasa/TGate dump format used `cats` for categories and `faqs` for FAQ
records. FAQ fields may include `audio_url`; the downloader therefore includes
audio files in asset discovery.

## Import into TurkDemy

After downloading:

```bash
uv run python manage.py populate_countries
uv run python manage.py import_rasa_data data/rasa
```

See `docs/rasa-import.md`.
