# imoves.com website - Version B specification

**Status: current.** Version B is the live development line on branch `main` of github.com/dmlaycock/imoves-website, published at dmlaycock.github.io/imoves-website/. At the time of this specification it stands at release v0.9 (commit 749227d, 30 October 2026).

Version B starts from Version A (the locked exact copy, see SPEC-version-a.md) and changes only what search engines, AI answer engines, screen readers and browsers see behind the page. A visitor looking at Version B sees Version A.

Date of this specification: 30 October 2026. Author: Claude, for David Laycock, on behalf of imoves active education ltd.

---

## 1. Purpose

Version A proved that imoves.com can be copied exactly and run on static hosting. It also inherited every fault of the live site. Version B fixes the faults that can be fixed without touching what visitors see, so that when the copy takes over imoves.com it is better found, better understood by AI answer engines, more accessible, and faster, while remaining the same site to the eye.

Version B does **not** change content, wording, design, layout, navigation, behaviour or any link visible on the page. The single visible change was made in Version A (the Pricing menu item pointing to the in-site pricing page) and is unchanged here.

## 2. Governing rule and how it is enforced

Every Version B change must leave every page rendering identically to Version A. This is enforced by `tools/compare-ab.js` and `tools/pixdiff.py`: every page is loaded from the frozen `/version-a/` copy and from the current build in headless Chromium at 1366 px and 390 px, with the site's JavaScript running, and the screenshots are compared pixel by pixel. The script fails if any page does not load (added in v0.9 after a silent failure, see issue 12). The rendered text and the sequence of heading tags are compared as well.

Acceptance for a Version B release: no text difference on any page; no layout or height difference on any page; pixel difference confined to lossy image compression at under 0.1 % of a page, with no visible change on inspection.

## 3. Release history

| Release | Date | Change |
|---|---|---|
| v0.8 | 30 Oct 2026 | Titles, descriptions, headings, alt text, structured data, robots.txt, llms.txt, sitemap |
| v0.9 | 30 Oct 2026 | Stylesheet purged, large images to WebP; v0.8 heading retags reverted in favour of ARIA levels |

## 4. Changes in detail, with reasons

### 4.1 Page titles (v0.8)

**Fault.** 56 of 161 pages ended "| imoves | imoves", a template bug in the Bespoke CMS that appended the site name to titles that already had it. 9 titles were duplicated across pages (for example three pages titled "Thank you everyone", two titled "Blog").

**Why it matters.** The title is the blue link in a search result and the tab label in the browser. A doubled suffix looks broken and wastes the space Google shows (about 60 characters). Duplicate titles make Google treat pages as near-copies and pick one to show.

**Change.** The doubled suffix is removed on all 56 pages. 13 titles were rewritten by hand to be unique and descriptive, for example "Active blasts, brain breaks and shake up activities" on two pages became "Active 30 Minutes - Brain Breaks and Shake Ups" and "Active 30 - Movement Breaks for the School Day". `og:title` and `twitter:title` follow the new titles.

**Not changed.** 61 titles remain over 60 characters. Shortening them means choosing which words to drop, which is an editorial decision for imoves (issue 10).

### 4.2 Meta descriptions (v0.8)

**Fault.** 31 pages had no description (16 of them indexable), 85 were over 160 characters, 8 were duplicated across pages.

**Why it matters.** The description is the grey text under a search result. Without one Google writes its own, often badly. Over-length ones are cut mid-sentence. Duplicates tell Google the pages are interchangeable. AI engines also read it as the page's one-line summary.

**Change.** Every indexable page now has a description of 120 to 155 characters, unique to it. Over-length ones were trimmed to a sentence boundary. Missing ones were drafted from the page's own opening copy, then 16 were rewritten by hand where the automatic draft read as a fragment. 10 duplicates were rewritten by hand. `og:description` and `twitter:description` follow.

### 4.3 Heading outline (v0.8, corrected in v0.9)

**Fault.** 22 pages had no H1, 19 had two or more, and the homepage uses H2 and H3 out of order.

**Why it matters.** The H1 tells search engines and screen readers what the page is about; several H1s dilute that, none leaves it to guesswork. AI summarisers lean on the heading outline to understand structure.

**First attempt (v0.8, reverted).** The script changed the tag of the first banner heading to `h1` where none existed, and extra `h1`s to `h2`. This changed appearance on 19 pages, because the site's stylesheet styles headings by tag inside `.text-content` (for example `.text-content h3 { font-size: 1.5rem }`), so an `h3` promoted to `h1` lost its rule and fell back to the browser default. The defect was not caught at the time because the verification server had stopped and the comparison passed two blank pages as identical (issue 12).

**Change (v0.9).** Every heading tag is restored to exactly what Version A has. The outline is instead declared with `role="heading" aria-level="1"` on the first heading of pages that have no `h1` (34 pages) and `aria-level="2"` on the surplus `h1`s of pages that have several (2 pages). Search engines and assistive technology read the ARIA level; the stylesheet ignores it, so nothing moves. Two image-led pages (`/gymnastics-for-primary-schools`, `/walk-to-school-week-is-back-join-the-5-day-challenge`) have no text heading at all and are left as they are.

### 4.4 Image alt text (v0.8)

**Fault.** 416 of 740 images had no `alt` attribute.

**Why it matters.** Alt text is what a screen reader says for an image and what image search indexes. Its absence is a WCAG 1.1.1 failure, which matters for a supplier to schools.

**Change.** Every image now has an `alt`. 114 Wistia video placeholders are marked decorative (`alt=""`), which is the correct treatment for an image that conveys nothing. 187 video thumbnails read "Video: <title above them>" (for example "Video: Alexi Jo"), or "Video: <page heading>" where no title sits above. 62 product, team and marketing images have hand-written text (for example "imoves Active School on laptop, tablet and phone", "Imogen Buxton-Pickles, imoves founder"). The rest are derived from their filenames ("Active autumn pink kid"), which is imperfect but honest and better than nothing; they are listed for review in `tools/versionb-alt.json`.

### 4.5 Structured data (v0.8)

**Fault.** Every page carried one generic Organization block and nothing else.

**Why it matters.** Structured data (JSON-LD) is how Google builds rich results (breadcrumbs, FAQ drop-downs, product prices) and how AI engines extract facts without guessing. Without it, "how much does imoves cost" or "what is a primary PE scheme of work" have nothing machine-readable to draw on.

**Change.** Added, in the page head, marked `data-vb="schema"` so they can be regenerated:
- `WebSite` on the homepage.
- `BreadcrumbList` on all 131 indexable pages, built from the URL path and page titles.
- `Article` on 73 guide and blog pages (Teacher Knowledge Hub, Resource Hub articles, blog and how-to pages), with headline, description, image, publisher and modified date.
- `FAQPage` on the 5 product pages whose "Frequently Asked Questions" section is written as numbered question-and-answer paragraphs: Active School (11 questions), Active Blasts (9), Active Learning (10), Primary PE (12), Wellbeing (8). The gymnastics page's FAQ uses an emoji-bullet layout the extractor does not read; the dance and CPD pages have an FAQ heading with no Q&A beneath.
- `Product` with three `Offer`s (infant, junior, primary prices in GBP, in stock, linking to the platform checkout) for each of the eight products on `/pricing`.

All blocks validate as JSON. The original Organization block is kept.

### 4.6 robots.txt, llms.txt and sitemap (v0.8)

**Fault.** The copy had no robots.txt (the live site's is two lines). No llms.txt existed anywhere. The sitemap listed 131 of 161 pages with no dates.

**Why it matters.** robots.txt is where crawlers check what they may read; AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended and others) increasingly look for an explicit welcome. llms.txt is the emerging convention for telling AI engines, in plain text, what a site is and which pages matter. The sitemap is how search engines find pages and learn what changed.

**Change.** `robots.txt` allows all crawlers, names the main AI crawlers explicitly, blocks `/adm` and `/version-a/`, and points to the sitemap. `llms.txt` describes imoves in a paragraph, lists the 16 main pages and every Knowledge Hub and Resource Hub article. `sitemap.xml` is regenerated from the page list: 132 indexable URLs (noindex pages excluded), each with a last-modified date and a priority.

### 4.7 Stylesheet (v0.9)

**Fault.** `default/dist/css/app.css` was 810 KB on every page: a Tailwind build that was never purged, so it carried every utility class in every responsive and state variant whether used or not.

**Why it matters.** The stylesheet blocks rendering until it has downloaded and parsed. 810 KB on a school's connection is a visible delay before anything appears, and page speed is a ranking factor.

**Change.** PurgeCSS was run against all 161 pages and the site's script. The safelist keeps every bare element selector (the CSS reset depends on them), every class the JavaScript adds at runtime (the slide-out menu, the video modal, hover and open states) and the `.text-content` family. Result: 27 KB. A check confirmed that every class used anywhere in the HTML and defined in the original stylesheet is still defined. The configuration is in `tools/purgecss.config.cjs` and the pre-purge original is in the Version A branch.

### 4.8 Images (v0.9)

**Fault.** 95 images were over 300 KB, the largest 2.4 MB; none were in a modern format.

**Why it matters.** Images are most of a page's weight. WebP is a quarter to a half the size of PNG or JPEG at the same quality and every current browser supports it.

**Change.** The 161 images over 150 KB were converted to WebP at quality 82 (63 MB saved across the site; a conversion that saved under 15 % was discarded). In the HTML, each `<img>` for a converted image is wrapped in `<picture>` with a WebP `<source>` and the original as fallback; each inline `background-image` gets a CSS `image-set()` with the WebP first and the original second. Browsers that cannot show WebP get exactly what Version A served. The originals stay in place.

**Not changed.** Scripts already load at the end of the body, so they do not block first paint; they were left alone. The 40 MB brochure PDF and the Wistia player script are the largest remaining loads and leave with later phases.

## 5. Verification results for v0.9

Against the frozen Version A copy, 161 pages at 1366 px and 390 px (322 renders), site JavaScript running, video, analytics and widget hosts blocked identically on both sides:

- Rendered text: identical on every page.
- Heading tag sequence: identical to Version A on every page.
- Layout and height: identical on every page (a 3-pixel height variance on four pages with video embeds disappeared on re-run; it was player load timing).
- Pixels: 256 of 322 renders identical. 66 renders differ by between 0.002 % and 0.061 % of the page, all inside photographs, from WebP recompression. The worst case was inspected side by side at full size and shows no visible difference.
- Structured data: 379 JSON-LD blocks, all parse.
- Behaviours (desktop dropdowns, mobile slide-out menu, video play, contact page) were confirmed on the published site in a real browser at v0.6 and v0.9's stylesheet keeps every runtime class those depend on; a scripted re-check of the open menus against Version A is part of the next release's verification.

## 6. Measured outcome

| Page | Version A | Version B v0.9 | Saving |
|---|---|---|---|
| Homepage | 2.06 MB | 0.71 MB | 65 % |
| Active School | 3.33 MB | 0.69 MB | 79 % |
| Primary PE | 1.95 MB | 0.63 MB | 68 % |
| Dance | 1.95 MB | 0.55 MB | 72 % |
| Pricing | 1.01 MB | 0.22 MB | 79 % |
| Knowledge Hub article | 1.01 MB | 0.21 MB | 79 % |
| Active Advent | 1.86 MB | 0.30 MB | 84 % |

| Measure | Version A | Version B v0.9 |
|---|---|---|
| Titles ending "\| imoves \| imoves" | 56 | 0 |
| Duplicate titles | 9 | 0 |
| Indexable pages with no description | 16 | 0 |
| Descriptions over 160 characters | 85 | 0 |
| Duplicate descriptions | 8 | 0 |
| Indexable pages with no H1 (tag or ARIA) | 16 | 2 |
| Pages with several top-level headings | 19 | 0 |
| Images with no alt attribute | 416 | 0 |
| Structured data types | 1 | 6 |
| Sitemap URLs | 131, undated | 132, dated |
| robots.txt / llms.txt | none | both |
| Stylesheet | 810 KB | 27 KB |

## 7. Open items carried by Version B

From `tools/issues-log.md`:

| # | Item | Owner / when |
|---|---|---|
| 10 | 61 titles over 60 characters; two image-led pages with no text heading; gymnastics FAQ not in schema | Review with imoves |
| 1 | Pricing page is a static snapshot of Quickbase prices | Phase 3 subscriptions or Phase 4 |
| 2, 3 | Bespoke-hosted form on `/jointheimovement`; dead Paddle buttons on `/march-half-price-offer` | Phase 3 (likely drop both pages) |
| 4, 5 | canonical and og:url name imoves.com; share-image URLs name github.io | One find-and-replace at cutover |
| 6 | GTM container ownership; Wistia and LeadConnector dependencies | Phase 2 (Wistia) and cutover |
| 7 | Login, sign-up and checkout on platform.imoves.com | Phases 1 and 3 |
| 8 | 68 disabled CMS pages not copied | Decide before Bespoke is switched off |

## 8. Tooling added in Version B (in `tools/`)

| File | Purpose |
|---|---|
| versionb-seo.py | Titles, descriptions, robots.txt, sitemap (v0.8). Its heading retagging is superseded; see 4.3 |
| versionb-schema.py | JSON-LD and llms.txt; idempotent, rerun after any content change |
| versionb-alt.py | Alt text generation |
| purgecss.config.cjs | Stylesheet purge configuration and safelist |
| compare-ab.js | Version B against frozen Version A, fails on any page that does not load |
| versionb-changes.json, versionb-alt.json, versionb-schema.json, versionb-webp.json | Every title, description, heading, alt and image change, for review |

## 9. How to make further Version B changes

1. Change the files on `main`. Never touch `/version-a/` or the `version-a` branch.
2. If content changed, rerun `tools/versionb-schema.py` so breadcrumbs, articles and FAQs follow.
3. Serve the repo locally and run `compare-ab.js` over `pages-b.txt`, then `pixdiff.py`. Any layout or text difference must be explained as deliberate and recorded in the README and the issues log, or fixed.
4. Give the release a new version number in the README. Never rebuild and overwrite a released version.
