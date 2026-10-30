#!/usr/bin/env python3
"""Version B, step 1: mechanical SEO fixes. Invisible to visitors.

- Titles: strip the doubled "| imoves | imoves"; fix the space before "|"; de-duplicate the known pairs.
- Descriptions: add one where missing (from the page's own first paragraph), trim >160 to a sentence boundary.
- H1: where a page has none, retag its first banner heading (h2/h3 in the page-banner block) as h1, keeping classes.
       Where a page has several, keep the first and retag the rest as h2, keeping classes.
       Empty H1s (image-only) become divs.
- robots.txt and a regenerated sitemap.xml (all indexable pages, lastmod = today).
Writes a change log to tools/versionb-changes.json.
"""
import glob, os, re, json, datetime
from bs4 import BeautifulSoup, NavigableString

ROOT = '/home/claude/imoves-website'
TODAY = datetime.date.today().isoformat()
SITE = 'https://imoves.com'
log = {'titles': {}, 'descriptions': {}, 'h1': {}, 'sitemap': 0}

# Hand-written de-duplications (path -> new title). Content-led, under 60 chars where possible.
TITLE_OVERRIDES = {
    '/active301': 'Active 30 Minutes - Brain Breaks and Shake Ups | imoves',
    '/active30m': 'Active 30 - Movement Breaks for the School Day | imoves',
    '/kristina': 'Kristina - imoves Ambassador | imoves',
    '/back-to-school-with-imoves-active-autumn': 'Back to School with imoves - Active Autumn | imoves',
    '/blog-coronavirus': 'Keeping Children Active at Home - Blog | imoves',
    '/blog-theres-always-one-teacher': "There's Always One Teacher - Blog | imoves",
    '/what-tips-and-activities-can-you-share-for-an-active-class': 'Top Tips and Activities for an Active Class | imoves',
    '/hundred-innovation': 'imoves and the HundrED Global Collection | imoves',
    '/pe-and-sports-funding': 'PE and Sport Premium Funding - How to Spend It | imoves',
    '/world-book-day': 'World Book Day Active Resources | imoves',
    '/thank-you-international-purchase': 'Thank You - International Purchase | imoves',
    '/thanks-for-subscribing': 'Thanks for Subscribing | imoves',
    '/active-learning': 'Active Learning for Primary Schools - Maths, English, Science | imoves',
}

def tidy_title(t):
    t = re.sub(r'\s*\|\s*', ' | ', t.strip())
    t = re.sub(r'(\s*\|\s*imoves)+\s*$', ' | imoves', t)
    if not t.endswith('| imoves'):
        t = t + ' | imoves'
    return t

def first_paragraph_text(soup):
    main = soup.find(attrs={'data-block': 'main-content'}) or soup.body
    for p in main.find_all(['p', 'h2', 'h3']):
        txt = re.sub(r'\s+', ' ', p.get_text(' ', strip=True))
        if len(txt) >= 60 and not txt.lower().startswith(('home >', 'frequently asked')):
            return txt
    txt = re.sub(r'\s+', ' ', main.get_text(' ', strip=True))
    return txt[:300]

def make_description(text, limit=155):
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    m = re.search(r'^(.*[.!?])\s', cut)
    if m and len(m.group(1)) > 80:
        return m.group(1)
    cut = cut.rsplit(' ', 1)[0].rstrip(',;:-')
    return cut + '...'

def retag(el, name):
    el.name = name
    return el

pages = []
for f in sorted(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)):
    if '/version-a/' in f or f.startswith(os.path.join(ROOT, 'version-a')):
        continue
    html = open(f, encoding='utf-8').read()
    if 'http-equiv="refresh"' in html:
        continue
    rel = os.path.relpath(os.path.dirname(f), ROOT)
    path = '/' if rel == '.' else '/' + rel
    soup = BeautifulSoup(html, 'html.parser')
    changed = False

    # --- title
    t = soup.title
    if t and t.string:
        old = t.string.strip()
        new = TITLE_OVERRIDES.get(path, tidy_title(old))
        if new != old:
            t.string.replace_with(new); log['titles'][path] = [old, new]; changed = True
            for m in soup.find_all('meta', attrs={'property': 'og:title'}) + soup.find_all('meta', attrs={'name': 'twitter:title'}):
                if m.get('content', '').strip() in (old, old.replace(' | imoves', ''), re.sub(r'(\s*\|\s*imoves)+$', '', old)):
                    m['content'] = new.replace(' | imoves', '')

    # --- description
    robots = soup.find('meta', attrs={'name': 'robots'})
    noindex = robots is not None and 'noindex' in (robots.get('content') or '')
    d = soup.find('meta', attrs={'name': 'description'})
    cur = (d.get('content') or '').strip() if d else ''
    newd = None
    if not cur and not noindex:
        newd = make_description(first_paragraph_text(soup))
    elif len(cur) > 160:
        newd = make_description(cur)
    if newd and newd != cur:
        if d is None:
            d = soup.new_tag('meta'); d['name'] = 'description'
            soup.head.insert(2, d)
        d['content'] = newd
        for m in soup.find_all('meta', attrs={'property': 'og:description'}) + soup.find_all('meta', attrs={'name': 'twitter:description'}):
            if (m.get('content') or '').strip() in (cur, ''):
                m['content'] = newd
        log['descriptions'][path] = [cur, newd]; changed = True

    # --- H1
    h1s = soup.find_all('h1')
    # drop empty h1s (image-only banners) to divs
    for h in list(h1s):
        if not h.get_text(strip=True):
            retag(h, 'div'); h1s.remove(h); changed = True
            log['h1'].setdefault(path, []).append('empty h1 -> div')
    if not h1s and not noindex:
        banner = soup.find(attrs={'data-block': 'page-banner'})
        cand = None
        if banner is not None:
            cand = banner.find(['h2', 'h3'])
        if cand is None:
            main = soup.find(attrs={'data-block': 'main-content'})
            if main is not None:
                cand = main.find(['h2', 'h3'])
        if cand is not None and cand.get_text(strip=True):
            log['h1'].setdefault(path, []).append(f'{cand.name} -> h1: {cand.get_text(" ", strip=True)[:60]}')
            retag(cand, 'h1'); changed = True
    elif len(h1s) > 1:
        for h in h1s[1:]:
            log['h1'].setdefault(path, []).append(f'h1 -> h2: {h.get_text(" ", strip=True)[:60]}')
            retag(h, 'h2'); changed = True

    if changed:
        open(f, 'w', encoding='utf-8').write(str(soup))
    pages.append((path, noindex))

# --- robots.txt
robots_txt = f"""User-agent: *
Allow: /
Disallow: /adm
Disallow: /version-a/

# AI and answer-engine crawlers are welcome
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: anthropic-ai
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: Bytespider
Allow: /
User-agent: CCBot
Allow: /

Sitemap: {SITE}/sitemap.xml
"""
open(os.path.join(ROOT, 'robots.txt'), 'w').write(robots_txt)

# --- sitemap.xml: indexable pages only
urls = []
for path, noindex in pages:
    if noindex or path == '/404':
        continue
    pri = '1.0' if path == '/' else ('0.9' if path in ('/pricing', '/active-school', '/active-learning', '/active-blasts', '/primary-pe', '/dance', '/mats', '/about-us', '/contact-us') else '0.7')
    urls.append(f'  <url>\n    <loc>{SITE}{path}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{pri}</priority>\n  </url>')
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n'
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm)
log['sitemap'] = len(urls)

json.dump(log, open(os.path.join(ROOT, 'tools', 'versionb-changes.json'), 'w'), indent=1)
print('titles changed', len(log['titles']), '| descriptions changed', len(log['descriptions']), '| h1 changes on', len(log['h1']), 'pages | sitemap urls', log['sitemap'])
