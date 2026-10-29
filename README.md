# imoves.com website copy

Static copy of the public imoves.com marketing site, taken 29 October 2026 from the live Bespoke-hosted site. Every enabled CMS page, its images, PDFs, stylesheet, script and fonts, with links rewritten to root-relative paths so the site runs on any static host.

- Pages: 160, plus 29 redirect stubs for old URLs the live site forwards
- Assets: 405 (images, PDFs, CSS, JS, fonts)
- 404 page: `404.html`
- Served by GitHub Pages from the `main` branch root (`.nojekyll` keeps every folder as-is)

## Tools

- `tools/mirror.py` - the crawler that produced this copy (`python3 tools/mirror.py` re-mirrors from the sitemap and follows internal links; `--only /path ...` fetches named pages)
- `tools/relativise.py` - converts root-relative URLs to page-relative ones after a re-mirror (`python3 tools/relativise.py .`)
- `tools/strip-dead-widgets.py` - removes the JustReview and Paddle integrations (run after a re-mirror)
- `tools/compare.js` - Playwright script that screenshots live vs copy and compares text and pixels
- `tools/page-schedule-v0.1.md` - schedule of every page with its group, videos, forms and widgets
- `tools/redirects.json` - the redirect map
- `tools/issues-log.md` - stop-gaps in the copy and the proper fix each needs later (also in the project docs as website/issues-log.md)

## Versions

- v0.1 - 29 Oct 2026 - first complete copy, pixel-identical on ten key pages at 1366px
- v0.2 - 29 Oct 2026 - all internal links and asset paths made relative (tools/relativise.py) so the site works at dmlaycock.github.io/imoves-website/ and at imoves.com/ unchanged
- v0.3 - 29 Oct 2026 - removed dead integrations: JustReview stylesheet, script, init and the 'Our latest reviews' block on 35 pages (the live widget shows an expired-subscription notice); Paddle script and setup on all pages. The 2020/21 march-half-price-offer page keeps its old Paddle buy buttons, which now do nothing.
- v0.4 - 29 Oct 2026 - added /pricing inside the site shell (static snapshot of the platform's eight products and prices, checkout links still to the platform) and pointed every Pricing menu link at it; started the issues log (pricing snapshot is issue #1)
- v0.5 - 29 Oct 2026 - pricing page laid out as on the platform: single column of full-width cards, bold titles, prices and buttons, no separate page banner
