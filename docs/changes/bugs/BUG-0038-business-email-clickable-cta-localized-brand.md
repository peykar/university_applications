# BUG-0038 — Business email clickable CTA and localized brand

Status: IMPLEMENTED

## Problem
Business email HTML rendered deep links as plain text, and Persian/Arabic business subjects embedded the English `TurkDemy` brand rather than the localized email brand.

## Resolution
Business email content now carries a structured CTA label/URL. Production delivery and previews render that CTA as a clickable HTML action while retaining the URL in plain text. Business copy resolves the brand through the shared localized email-brand helper.
