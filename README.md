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
- v0.6 - 29 Oct 2026 - audit fixes: og:image and twitter:image restored to absolute imoves.com URLs (social previews need them); three UTM-tagged internal links restored; mirror.py corrected for both. Full audit: 160 pages at 1366px and 390px, text identical on all, fonts identical on all, 248 of 320 renders pixel-identical, the other 70 differ only by the reviews block removed in v0.3. Audit tools added (compare-all.js, pixdiff.py, dom-audit.py).
- v0.7 - 29 Oct 2026 - new link-preview images (og-share.png, twitter-share.png) at 1200x630 using the current im brand mark on purple, replacing the retired wordmark the live site still serves; og:image and twitter:image point at the copy's own address until cutover

## Version A - locked 30 Oct 2026

Version A is the exact copy at v0.7 (commit f664269). It is locked on branch `version-a` and served frozen at `/version-a/`. Its specification is `tools/SPEC-version-a.md`. Do not change Version A; all further work is Version B onwards on `main`.

## Version B - search and AI discovery (in progress from 30 Oct 2026)

Version B starts from Version A and changes nothing a visitor sees. Every change is in the page head, in attributes, or in new files at the root. Verified against the frozen Version A copy: 322 of 322 renders pixel-identical, no text change.

- v0.8 - 30 Oct 2026 - titles: doubled "| imoves | imoves" removed on 56 pages, 13 duplicates rewritten; descriptions: 16 written where missing, 85 over-length trimmed to a sentence, 10 duplicates rewritten; H1: 15 pages given one by retagging their banner heading, 19 pages with several reduced to one (extras become h2, classes kept), image-only h1s became divs; alt text on all 416 images that lacked it (114 marked decorative, 59 video thumbnails named from the page, 62 hand-written, rest from filenames); JSON-LD added: WebSite, BreadcrumbList on 131 pages, Article on 73 guides and blogs, FAQPage on 5 product pages (50 questions), Product and Offer for the 8 products on /pricing; robots.txt with AI crawlers allowed; llms.txt; sitemap.xml regenerated with 132 indexable URLs and lastmod. Scripts: tools/versionb-seo.py, versionb-schema.py, versionb-alt.py; change logs tools/versionb-changes.json, versionb-alt.json, versionb-schema.json.
- v0.9 - 30 Oct 2026 - performance. Stylesheet purged against every page (810 KB to 27 KB; all element selectors and runtime menu/modal classes safelisted; tools/purgecss.config.cjs). 161 images over 150 KB converted to WebP (63 MB saved) and served through <picture> or CSS image-set with the original as fallback. Also corrects a v0.8 defect: retagging headings to h1/h2 changed their size because the stylesheet styles headings by tag inside .text-content; all heading tags are restored to Version A's and the outline is now expressed with role="heading" aria-level="N" instead, which is invisible. Verified against Version A: 256 of 322 renders pixel-identical, the rest differ by under 0.07% from WebP compression with no visible change; no text or layout change on any page. Typical page weight down 65-84%.

## Version B - locked 30 Oct 2026

Version B is locked at v0.9 (commit 9c2326a) on branch `version-b` and served frozen at `/version-b/`. Specification: `tools/SPEC-version-b.md`.

## Version C - leaving Wistia (in progress from 30 Oct 2026)

- v0.10 - 30 Oct 2026 - all 114 Wistia popover embeds on 47 pages replaced with a Cloudflare Stream player. The 74 marketing videos were imported to Stream by the `website` mode of the imoves repo's video-migration workflow (27 were already there from the content migration, 47 imported now; map in tools/video-stream-map.json). Each video's designed thumbnail was fetched from Wistia at 1280x720 and stored in video/thumbs (jpg + webp); the Active Advent video has no public Wistia thumbnail and uses Stream's generated one. The player (video/cf-player.css, video/cf-player.js, 3.4 KB total, no third-party script) reproduces the Wistia look: 16:9 rounded thumbnail, purple play button, click opens a lightbox with the Stream iframe autoplaying, closed by X, overlay click or Escape. Wistia scripts removed from every page. Vimeo and YouTube modals are unchanged. Script: tools/versionc-stream.py.
