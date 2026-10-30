# imoves.com website - Version A specification

**Status: LOCKED.** Version A is the exact static copy of the public imoves.com site as it stood on 29 October 2026. It is frozen at git commit `f664269` (release v0.7) on branch `version-a` of github.com/dmlaycock/imoves-website, and a viewable frozen copy is served at dmlaycock.github.io/imoves-website/version-a/. Nothing in Version A changes from this point. All further work happens in Version B and later.

Date of this specification: 30 October 2026. Author: Claude, for David Laycock, on behalf of imoves active education ltd.

---

## 1. Purpose

Version A exists to:

1. Capture the whole public marketing site before Bespoke Digital Agency's CMS and hosting are switched off (Phase 3 of the imoves re-engineering).
2. Give imoves a copy that runs on any static host, with no server-side code, so the site can move to imoves.com by a DNS change.
3. Provide a fixed, verified baseline that Version B and later can be measured against: any difference between a later version and Version A is a deliberate change, not drift.

Version A deliberately does **not** improve the site. Where the live site has a fault, Version A has the same fault, with four exceptions listed in section 8.

## 2. Scope

### 2.1 In scope

- Every page enabled in the Bespoke CMS (imoves.com/adm, Pages list, 233 entries of which 165 enabled) that is reachable on the public site: 160 pages, plus the 404 page.
- Every asset those pages reference on the imoves.com origin: images, PDFs, the stylesheet, the script, fonts, favicons, the web manifest and the XML sitemap.
- Redirect stubs for the 29 legacy URLs that the live site forwards (for example `/dances` to `/dance`, `/peplus` to `/primary-pe`) and two platform redirects (`/signup`, `/subscriptions`).
- One new page, `/pricing`, built inside the site header and footer as a static snapshot of the platform's subscription options page (see 8.3).

### 2.2 Out of scope

- The 68 CMS pages marked Disabled (old offers, Covid-era pages, drafts, test pages). They are not on the public site and were not copied. They remain retrievable from the CMS until Bespoke is switched off.
- The teacher platform at platform.imoves.com (login, sign-up, checkout, the resources themselves). Links to it are kept as they are.
- The after-school club site at aac.imoves.com and the Active 30 site at active.imoves.com. Links kept.
- Server-side behaviour: the one CMS form (see 7.3), the Bespoke admin, the video-feed refresh.
- Third-party services: Wistia, LeadConnector, Google Tag Manager, Google Fonts. They are loaded from their own hosts exactly as the live site loads them.

## 3. Page inventory

160 content pages plus `404.html`, grouped as in `tools/page-schedule-v0.2.md` (which lists every path, title, video count, form and widget):

| Group | Pages |
|---|---|
| Core (homepage) | 1 |
| Product and offer pages (Active School, Active Learning, Active Blasts, Primary PE, Dance, Gymnastics, Pilates, Wellbeing, MATs, CPD, SEND, Enrichment, Active 30 variants) | 17 |
| Company pages (About, Team, Contact, Terms, Privacy, Sitemap, We Love imoves, Ambassadors, Help, Chat) | 10 |
| Teacher Knowledge Hub (index and 10 articles) | 11 |
| Resource Hub (index, 3 category pages, 6 articles) | 10 |
| Partner and profile pages (Advertise, Davies Sports, Fundraise, SGO, ITT, HundrED, EdTech 50, accreditation) | 11 |
| Blogs, guides and articles | 74 |
| Offers and seasonal campaigns (Black Friday, Spring, March, Active Advent, Active Autumn, lockdown, free access) | 12 |
| Utility and thank-you pages (thank-you x7, message-sent, unsubscribe, log-in, reports, page-builder, jointheimovement, the-imovement) | 14 |
| Pricing (new in Version A) | 1 |

Redirect stubs: 29 legacy paths plus `/signup` and `/subscriptions` (31 stub files). Each is a one-line HTML page with a `meta refresh` and a canonical link to the destination.

## 4. Structure and build

### 4.1 File layout

Each page lives at `<path>/index.html`, so clean URLs work on any static host (`/active-school` serves `active-school/index.html`). The homepage is `index.html` at the root. Assets keep their original paths under `/images/`, `/files/` and `/default/dist/`.

### 4.2 Links

Every internal link and asset reference is **page-relative** (`./pricing`, `../default/dist/css/app.css`, `../../images/...`). This lets the identical files run at `dmlaycock.github.io/imoves-website/` today and at `imoves.com/` after cutover with no edit. `tools/relativise.py` performs the conversion after a re-mirror.

Three internal links carry UTM query strings as on the live site, so that Analytics attribution is unchanged.

External links (platform.imoves.com, aac.imoves.com, LeadConnector, social profiles, partner sites) are left absolute.

### 4.3 Head metadata

Each page keeps the live site's `<title>`, meta description, robots directive, canonical link, Open Graph and Twitter Card tags, favicons and theme colour. Two deliberate changes: `og:image` and `twitter:image` point at the copy's own share image (see 8.4), and the `csrf-token` meta is carried over unused.

`canonical` and `og:url` still name `https://imoves.com/...`. This is correct for the final home and is flagged for the preview period in issue #4.

### 4.4 Hosting

GitHub Pages, served from the root of the `main` branch. A `.nojekyll` file stops GitHub's Jekyll processing so every folder is served as-is. `404.html` at the root is picked up by GitHub Pages as the not-found page. Total size 385 MB (370 MB of it images and PDFs; the largest single file is the 40 MB brochure PDF).

## 5. Design and presentation

The copy uses the live site's own compiled stylesheet (`default/dist/css/app.css`, 812 KB, Tailwind-based) and script (`default/dist/js/app.js`, 76 KB) without modification.

- **Typefaces**: Baloo (self-hosted, four TTF weights under `default/dist/ui/fonts/`) for headings and body; Montserrat from Google Fonts for some legacy content blocks.
- **Palette**: purple `#702f8a` header, footer and bands; lilac `#dcccea` page background; white content cards; accent colours per product (red, orange, pink, blue, green).
- **Header**: fixed purple bar with the seasonal logo (currently the Halloween "10 October" variant), five top-level menu items with hover dropdowns at desktop width, Login and Get FREE Access buttons. Below 1024 px a hamburger opens a right-hand slide-out menu (the "pushy" component) with expanding sections.
- **Footer**: social icons, company details, 24/7 phone number, Terms and Privacy links, brush-stroke SVG edge.
- **Responsive**: Tailwind breakpoints as on live; verified at 1366 px and 390 px.

## 6. Behaviours

| Behaviour | Mechanism | Verified |
|---|---|---|
| Desktop dropdown menus | CSS hover on `li.has-dropdown` | Identical to live |
| Mobile slide-out menu and expanding sections | `app.js` + pushy classes, jQuery 3.4.1 from ajax.googleapis.com | Identical to live |
| Equal-height cards | jquery.matchHeight 0.7.2 from cdnjs | Loads and runs |
| Video | Wistia E-v1.js embeds, 74 distinct media IDs across the site | Players initialise with thumbnails; showreel plays |
| Book a demo | Links to api.leadconnectorhq.com booking widgets (two different calendars) | Links intact |
| Teacher login / Get FREE Access | Links to platform.imoves.com/login and /sign-up | Links intact |
| Pricing menu item | Points to the new `/pricing` page | Works (deliberate change, 8.3) |
| Analytics | Google Tag Manager GTM-W5KKLGQ loads on every page | Container loads (ownership to confirm at cutover) |
| Link prefetch | instant.page 2.0.0 | Loads |
| 404 | `404.html` copied from the live site's not-found page | Served by GitHub Pages |

## 7. Verification

### 7.1 Method

`tools/compare-all.js` loaded every page from imoves.com and from the copy in headless Chromium at 1366 px and 390 px, with the site's JavaScript running and the same third-party hosts blocked on both sides. It recorded the rendered text, computed font families, link targets, page height and a full-page screenshot. `tools/pixdiff.py` compared the screenshot pairs pixel by pixel. `tools/dom-audit.py` separately compared the raw HTML: links, images, srcset, stylesheets, scripts, inline scripts, meta tags, inline styles, class lists, text and titles.

### 7.2 Results

- Rendered text: identical on all 160 pages at both widths.
- Font families: identical on all 160 pages.
- Links, images, stylesheets, scripts, classes, styles, titles: identical, after two corrections made in v0.6 (absolute share-image URLs; three UTM strings).
- Pixels: 248 of 320 renders identical. The remaining 70 renders are the 35 pages carrying the removed JustReview block (8.1); the difference is confined to the region below that block, which sits higher by its removed height. No other pixel difference on any page.
- Behaviours: as in section 6, checked in the Claude browser pane on the published copy against the live site.

## 8. Deliberate differences from the live site

Version A differs from imoves.com in exactly four ways. Each is recorded in `tools/issues-log.md`.

### 8.1 JustReview removed (v0.3)
The live site loads a JustReview stylesheet and script on every page and renders an "Our latest reviews..." block on 35 pages. imoves no longer subscribes, and the widget displays "Your subscription has expired" on the live site. Version A removes the stylesheet, script, init code and the 35 empty blocks.

### 8.2 Paddle removed (v0.3)
The live site loads paddle.js and calls `Paddle.Setup` on every page. Paddle is legacy only. Version A removes both. The 2020/21 `/march-half-price-offer` page keeps its old Paddle buttons, which now do nothing (issue #3).

### 8.3 Pricing page added (v0.4, v0.5)
The live Pricing menu item sends visitors to platform.imoves.com/subscribe/options, a page with the platform's own header and footer. Version A adds `/pricing` inside the site's header and footer, laid out as the platform page is (single column of eight product cards, three price tiers each, coloured "Get..." buttons linking to the platform checkout), and points the Pricing menu item on every page to it. Prices are a snapshot as at 29 Oct 2026 (issue #1).

### 8.4 Share image replaced (v0.7)
The live site's `og-share.png` and `twitter-share.png` carry a wordmark retired about five years ago. Version A replaces both with the current "im" brand mark on purple at 1200 x 630 and points the meta tags at the copy's own files (issue #9).

## 9. Known issues

Section 9.1 lists issues inherent in a static copy; section 9.2 lists search and AI discovery faults inherited from the live site. Each has its impact and its planned fix. Items marked **B** are addressed in Version B; the rest are tied to later phases.

### 9.1 Structural issues (from tools/issues-log.md)

| # | Issue | Impact | Fix | When |
|---|---|---|---|---|
| 1 | Pricing page is a static snapshot of Quickbase-driven prices | A price change in Quickbase is not reflected until someone edits the file | Read prices from the Phase 3 subscription store, or regenerate on a schedule | Phase 3 or 4 |
| 2 | `/jointheimovement` form posts to Bespoke's server | Form submits nowhere once Bespoke is off | Repoint to a Genie (GHL) form or drop the page | Phase 3 |
| 3 | Paddle buttons on `/march-half-price-offer` | Dead buttons on an unlinked 2020 page | Drop the page | Phase 3 |
| 4 | canonical and og:url name imoves.com; share images name github.io | Correct at cutover; until then search engines treat the live site as canonical | One find-and-replace at cutover | Phase 3 |
| 5 | sitemap.xml copied verbatim, 131 URLs, no lastmod | 30 pages and `/pricing` absent from the sitemap | Regenerate from the page list | **B** |
| 6 | Third-party scripts kept (GTM, LeadConnector, instant.page, jQuery CDN, Wistia, Google Fonts) | Dependencies to review; GTM container ownership unknown | Review at cutover; Wistia leaves with Phase 2 | Phase 2 and 3 |
| 7 | Login, sign-up and checkout live on platform.imoves.com | Fine until the platform is replaced | Replaced by Phase 1 front end and Phase 3 subscriptions | Phase 1 and 3 |
| 8 | 68 disabled CMS pages not copied | Lost when Bespoke is switched off unless fetched first | Decide before switch-off | Phase 3 |
| 9 | Share image was the retired logo | Fixed in v0.7 | Swap in the full wordmark if imoves supply one | Done |

### 9.2 Search and AI discovery faults inherited from the live site

Audited across the 161 pages on 30 Oct 2026 (`tools/seo-pages.json`).

| Area | Finding | Impact | Fix | When |
|---|---|---|---|---|
| Titles | 56 pages end "\| imoves \| imoves" (template bug); 79 exceed 60 characters; 9 duplicates | Truncated and repetitive results in Google; weaker click-through | Strip the doubled suffix; shorten where meaning allows; de-duplicate | **B** |
| Descriptions | 31 pages have none; 85 exceed 160 characters; 8 duplicated across pages | Google writes its own snippet; duplicates dilute | Write one per page from its own opening copy, 120-155 characters | **B** |
| Headings | 22 pages have no H1; 19 have two or more; homepage mixes H2 and H3 out of order | Weaker topical signal for search and for AI summarisers | Promote the page title to H1 where absent; demote extras to H2 | **B** |
| Image alt text | 416 of 740 images have no alt attribute | Accessibility failure (WCAG 1.1.1); invisible to image search | Generate alt text from filename and surrounding heading; mark decorative images with empty alt | **B** |
| Structured data | Only a generic Organization block on every page | Search engines and AI engines get no product, price, article or FAQ facts | Add BreadcrumbList site-wide; Article on the ~85 guides and blogs; Product and Offer on `/pricing`; FAQPage where pages already contain Q&A | **B** |
| Sitemap | 131 of 161 pages; no lastmod | Slower discovery of new and changed pages | Regenerate with all indexable pages and dates | **B** |
| robots.txt | Live site: `Allow: /`, `Disallow: /adm`. Copy: none | AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) rely on defaults | Add robots.txt with explicit allows and the sitemap location | **B** |
| llms.txt | None | AI engines have no curated summary of what imoves is and which pages matter | Add `/llms.txt` with a description, key pages and contact | **B** |
| Performance | `app.css` 812 KB unpurged; 77 images over 500 KB; no WebP; render-blocking scripts | Poor Core Web Vitals, a ranking factor and a mobile experience issue | Purge Tailwind, convert large images to WebP with fallbacks, defer scripts | Phase 3 |
| Thin pages | 6 thank-you pages under 150 words (all already noindex) | None | None | - |

## 10. Tooling (in `tools/`)

| File | Purpose |
|---|---|
| mirror.py | Crawl imoves.com from the sitemap and internal links; save pages and same-origin assets; rewrite links |
| relativise.py | Convert root-relative URLs to page-relative so the site runs at any mount point |
| strip-dead-widgets.py | Remove JustReview and Paddle |
| compare.js, compare-all.js, pixdiff.py, dom-audit.py | Verification against the live site (section 7) |
| redirects.json | Legacy URL to destination map |
| page-schedule-v0.2.md | Every page with group, videos, forms, widgets and a Keep column |
| issues-log.md | Running log of stop-gaps and their proper fixes |
| seo-pages.json | Per-page SEO audit data (titles, descriptions, H1 counts, alt counts) |

## 11. Release history to lock

| Version | Date | Change |
|---|---|---|
| v0.1 | 29 Oct 2026 | First complete copy: 160 pages, 405 assets, redirects, 404 |
| v0.2 | 29 Oct 2026 | All links made page-relative |
| v0.3 | 29 Oct 2026 | JustReview and Paddle removed |
| v0.4 | 29 Oct 2026 | `/pricing` added in the site shell; issues log started |
| v0.5 | 29 Oct 2026 | Pricing page laid out as the platform page |
| v0.6 | 29 Oct 2026 | Audit fixes: absolute share-image URLs, UTM links restored; audit tools |
| v0.7 | 29 Oct 2026 | Current brand mark for share images |
| **Version A** | **30 Oct 2026** | **Lock at v0.7, commit f664269, branch `version-a`, frozen copy at `/version-a/`** |

## 12. Lock statement

Version A is complete and locked. Its content is the live imoves.com site of 29 October 2026 with the four deliberate differences in section 8, verified as set out in section 7. The faults in section 9 are recorded, not fixed. Version B starts from this baseline and must demonstrate, by the same comparison tools, that every visible change it makes is intentional.
