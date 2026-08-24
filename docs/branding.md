# TurkDemy Branding

Assets are in `static/branding/`.

- `turkdemy-logo.svg`: primary native vector logo.
- `turkdemy-logo-horizontal.svg`: header logo.
- `turkdemy-mark.svg`: emblem-only native vector mark.
- `turkdemy-mark-monochrome.svg`: monochrome mark.
- `turkdemy-logo-generated.png`: original generated concept.
- `favicon.ico`, 16/32/48 PNG favicons.
- `apple-touch-icon.png`: 180×180.
- `android-chrome-192x192.png` and `android-chrome-512x512.png`.
- `site.webmanifest`.

Brand colors: Navy `#0B3A67`, Red `#E3062C`, White `#FFFFFF`.

The SVG files contain vector shapes/text and do not embed raster images.
`templates/base.html` uses the horizontal SVG and declares the favicon/app icons.

## Troubleshooting

If the header logo is missing during development, verify:

```text
http://127.0.0.1:8000/static/branding/turkdemy-logo-horizontal.svg
```

The browser should display the SVG directly. The base template references this
asset through Django's `{% static %}` tag.
