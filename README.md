# imoves.com website copy

Static copy of the public imoves.com marketing site, taken 29 October 2026 from the live Bespoke-hosted site. Every enabled CMS page, its images, PDFs, stylesheet, script and fonts, with links rewritten to root-relative paths so the site runs on any static host.

- Pages: 160, plus 29 redirect stubs for old URLs the live site forwards
- Assets: 405 (images, PDFs, CSS, JS, fonts)
- 404 page: `404.html`
- Served by GitHub Pages from the `main` branch root (`.nojekyll` keeps every folder as-is)

## Tools

- `tools/mirror.py` - the crawler that produced this copy (`python3 tools/mirror.py` re-mirrors from the sitemap and follows internal links; `--only /path ...` fetches named pages)
- `tools/relativise.py` - converts root-relative URLs to page-relative ones after a re-mirror (`python3 tools/relativise.py .`)
- `tools/compare.js` - Playwright script that screenshots live vs copy and compares text and pixels
- `tools/page-schedule-v0.1.md` - schedule of every page with its group, videos, forms and widgets
- `tools/redirects.json` - the redirect map

## Versions

- v0.1 - 29 Oct 2026 - first complete copy, pixel-identical on ten key pages at 1366px
- v0.2 - 29 Oct 2026 - all internal links and asset paths made relative (tools/relativise.py) so the site works at dmlaycock.github.io/imoves-website/ and at imoves.com/ unchanged
