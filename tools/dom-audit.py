#!/usr/bin/env python3
"""Static DOM audit: live HTML vs copy HTML for every page.
Compares, after normalisation: link targets, image sources, text content, meta tags,
script/style references. Ignores the JustReview/Paddle removals made deliberately in v0.3."""
import os, re, json, sys, requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Comment
ROOT = '/home/claude/imoves-website'; SITE = 'https://imoves.com'
pages = [l.strip() for l in open('pages.txt') if l.strip()]
S = requests.Session(); S.headers['User-Agent'] = 'Mozilla/5.0'
def norm_url(u, base_path):
    if not u or u.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:', 'sms:')): return u
    if u.startswith('//'): u = 'https:' + u
    absu = urljoin(SITE + base_path + ('/' if base_path != '/' else ''), u)
    p = urlparse(absu)
    host = p.netloc.replace('www.', '')
    if host == 'imoves.com':
        path = re.sub(r'\?\d{6,}$', '', p.path)  # cache-buster on assets
        path = path.rstrip('/') or '/'
        return path + (('?' + p.query) if p.query and not p.query.isdigit() else '') + (('#' + p.fragment) if p.fragment else '')
    return absu
def clean(soup):
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)): c.extract()
    # deliberate removals in v0.3
    for el in soup.find_all(['link', 'script']):
        src = (el.get('href') or el.get('src') or '')
        if 'justreview' in src or 'paddle.com' in src: el.decompose()
    for sc in soup.find_all('script'):
        t = sc.string or ''
        if 'JustReview.initTestimonials' in t or 'Paddle.Setup' in t: sc.decompose()
    h = soup.find(id='justreview-testimonials')
    if h is not None:
        row = h.find_parent(attrs={'data-block': 'main-content'})
        (row if row is not None and len(row.get_text(strip=True)) <= len(h.get_text(strip=True)) + 2 else h).decompose()
    for m in soup.find_all('meta', attrs={'name': 'csrf-token'}): m.decompose()
    return soup
def digest(soup, base_path):
    links = [norm_url(a.get('href'), base_path) for a in soup.find_all('a')]
    # the Pricing menu link was deliberately repointed in v0.4
    links = ['/pricing' if l == 'https://platform.imoves.com/subscribe/options' else l for l in links]
    imgs = [norm_url(i.get('src') or i.get('data-src'), base_path) for i in soup.find_all('img')]
    srcset = [re.sub(r'https?://(www\.)?imoves\.com', '', i.get('srcset')) for i in soup.find_all(srcset=True)]
    css = [norm_url(l.get('href'), base_path) for l in soup.find_all('link', rel=lambda r: r and 'stylesheet' in r)]
    js = [norm_url(s.get('src'), base_path) for s in soup.find_all('script', src=True)]
    inline_js = [re.sub(r'\s+', ' ', (s.string or '')).strip()[:200] for s in soup.find_all('script', src=False)]
    inline_js = [re.sub(r'https?://(www\.)?imoves\.com', '', x) for x in inline_js]
    metas = sorted(f"{m.get('name') or m.get('property')}={re.sub(r'https?://(www.)?imoves.com','',str(m.get('content')))}" for m in soup.find_all('meta') if m.get('name') or m.get('property'))
    for t in soup(['script', 'style', 'noscript']): t.decompose()
    text = re.sub(r'\s+', ' ', soup.get_text(' ')).strip()
    styles = [re.sub(r'https?://(www\.)?imoves\.com', '', e.get('style')) for e in soup.find_all(style=True)]
    classes = [' '.join(e.get('class')) for e in soup.find_all(class_=True)]
    return dict(links=links, imgs=imgs, srcset=srcset, css=css, js=js, inline_js=inline_js, metas=metas, text=text, styles=styles, classes=classes, title=soup.title.string if soup.title else '')
def relativise_copy(soup, page_path):
    # resolve the copy's relative URLs against the page path so they compare to live's
    return soup
report = {}
for p in pages:
    f = os.path.join(ROOT, p.strip('/'), 'index.html') if p != '/' else os.path.join(ROOT, 'index.html')
    copy = BeautifulSoup(open(f, encoding='utf-8').read(), 'html.parser')
    try:
        r = S.get(SITE + p, timeout=40); live = BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        report[p] = {'error': str(e)}; continue
    dl = digest(clean(live), p)
    # for the copy, hrefs like ../x resolve relative to /p/ -> handled by norm_url with base_path
    dc = digest(clean(copy), p)
    diffs = {}
    for k in dl:
        if dl[k] != dc[k]:
            if isinstance(dl[k], list):
                a, b = dl[k], dc[k]
                only_live = [x for x in a if x not in b][:5]; only_copy = [x for x in b if x not in a][:5]
                diffs[k] = {'live_n': len(a), 'copy_n': len(b), 'only_live': only_live, 'only_copy': only_copy}
            else:
                a, b = dl[k], dc[k]; i = 0
                while i < len(a) and i < len(b) and a[i] == b[i]: i += 1
                diffs[k] = {'live': a[max(0, i - 60):i + 120], 'copy': b[max(0, i - 60):i + 120]}
    report[p] = diffs
    print(p, 'OK' if not diffs else 'DIFF ' + ','.join(diffs), flush=True)
json.dump(report, open('dom-audit.json', 'w'), indent=1)
print('pages with differences:', sum(1 for v in report.values() if v))
