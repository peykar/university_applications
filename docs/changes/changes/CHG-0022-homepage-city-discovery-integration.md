# CHG-0022 — Homepage City discovery integration

Status: VERIFIED
Requested: 2026-09-03

## Request

Integrate the canonical City landing pages into homepage discovery in the same way that
GeneralField landing pages are discoverable from the homepage.

## Classification

CHANGE

## Affected requirements

- `CAT-068` — top-five homepage City destination discovery.
- `SEO-018` — crawlable direct homepage links to canonical City landing pages.
- `BR-SEO-007` — homepage City-discovery canonical-link policy.

## Desired behavior

- Add Study destinations between Featured Universities and the GeneralField section.
- Show up to five active Cities that have active Universities.
- Order by active University count, then active Program count, then stable English name.
- Link the whole City card directly to `/universities/cities/<slug_en>/`.
- Show localized City name and active University/Program counts.
- Reuse the curated City banner and localized alt text when available; render a clean visual
  placeholder when no banner exists.
- Keep mobile compact with horizontally swipeable destination cards.

## SEO review

- Homepage title/meta/canonical/hreflang/robots: unchanged.
- Sitemap: unchanged; City landing pages already participate independently under `SEO-016`.
- Internal links: strengthened through direct crawlable homepage City links.
- Query filters: not promoted; destination cards use clean City landing routes only.
- Social/structured metadata: homepage metadata unchanged.
- Images: reused City banners keep locale-aware meaningful alt text.
- Semantic structure: section has a localized eyebrow/H2 and cards use City H3 headings.

## Verification

- [ ] `make format`
- [ ] `make check`
- [ ] Verify EN homepage City card links to the canonical City landing page.
- [ ] Verify FA/AR RTL homepage destination cards and localized banner alt text.
- [ ] Verify mobile destination row is horizontally swipeable and does not expand page height excessively.
