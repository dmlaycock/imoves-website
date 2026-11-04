#!/usr/bin/env python3
"""v0.18: apply Ian and Imogen's sign-off responses (review document v4, returned 4 November 2026).

1. 26 hidden pages they marked Remove become forwards to the homepage (the Black Friday Wellbeing
   page, also marked Remove, keeps its existing forward to Mental Wellbeing, as David agreed).
   build-dist.py turns every forward into a 301 in Cloudflare's _redirects.
2. Gymnastics page: subscription wording removed, "included in" line added, trial buttons start
   the PE trial (nid=133), and the two duplicate "Book a demo" buttons added in v0.11 removed.
3. Mental Wellbeing page: both "See Prices" buttons removed, the standalone price dropped, the
   "Does the whole school get access?" answer removed, "included in" line added, trial buttons
   start the Active School trial (nid=138).
"""
import os, re
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOVE = """ambassadors kristina free-online-clinics-for-sgos blackfridaydeals-priority march-half-price-offer
march-offers spring-offer spring-saver-offer lockdown lockdown-free-access free-access-june blog-coronavirus reports
pe-and-sports-funding world-book-day laughing-yoga the-imovement jointheimovement we-love-imoves log-in active-30minutes
active301 active30m activeblasts2 page-builder sitemap""".split()
assert len(REMOVE) == 26, len(REMOVE)

def stub(path):
    depth = path.count('/') + 1
    up = '../' * depth
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>Redirecting</title>'
            f'<meta http-equiv="refresh" content="0; url={up}"><link rel="canonical" href="https://imoves.com/">'
            f'</head><body><a href="{up}">Continue</a></body></html>')

for p in REMOVE:
    f = os.path.join(ROOT, p, 'index.html')
    assert os.path.exists(f), p
    open(f, 'w').write(stub(p))
# /subscriptions (a legacy address) forwarded to the platform's old eight-product price page; send it to /pricing
open(os.path.join(ROOT, 'subscriptions', 'index.html'), 'w').write(
    '<!doctype html><html><head><meta charset="utf-8"><title>Redirecting</title><meta http-equiv="refresh" content="0; url=../pricing/">'
    '<link rel="canonical" href="https://imoves.com/pricing"></head><body><a href="../pricing/">Continue</a></body></html>')
# the old Login page is still linked from Thanks for subscribing, so it forwards to the platform login instead
LOGIN = 'https://platform.imoves.com/login'
open(os.path.join(ROOT, 'log-in', 'index.html'), 'w').write(
    f'<!doctype html><html><head><meta charset="utf-8"><title>Redirecting</title><meta http-equiv="refresh" content="0; url={LOGIN}">'
    f'<link rel="canonical" href="{LOGIN}"></head><body><a href="{LOGIN}">Continue</a></body></html>')

# keep sitemap.xml and llms.txt free of removed pages
for fn in ('sitemap.xml', 'llms.txt'):
    fp = os.path.join(ROOT, fn); s = open(fp).read(); n = 0
    for p in REMOVE:
        pat = re.compile(r'\s*<url>\s*<loc>https://imoves\.com/' + re.escape(p) + r'/?</loc>.*?</url>', re.S) if fn == 'sitemap.xml' \
            else re.compile(r'^.*https://imoves\.com/' + re.escape(p) + r'/?\)?\s.*\n?', re.M)
        s, k = pat.subn('', s); n += k
    open(fp, 'w').write(s); print(fn, 'entries removed:', n)

def page(p):
    f = os.path.join(ROOT, p, 'index.html')
    return f, BeautifulSoup(open(f, encoding='utf-8'), 'html.parser')

def included_line(soup, text):
    """Add one centred line to the page banner, under the existing banner heading and subheading."""
    banner = soup.select_one('[data-block=page-banner] .row')
    assert banner is not None
    new = soup.new_tag('p', attrs={'class': ['text-lg', 'font-semibold', 'px-20', 'mb-30', 'mx-auto', 'text-center']})
    new.string = text
    banner.append(new)

def retarget_trials(soup, old_nid, new_nid):
    n = 0
    for a in soup.find_all('a', href=True):
        if f'sign-up?nid={old_nid}' in a['href']:
            a['href'] = a['href'].replace(f'nid={old_nid}', f'nid={new_nid}'); n += 1
    return n

# ---- Gymnastics
f, s = page('imoves-gymnastics')
# v0.11 turned each "Buy Now" in the two package-cta rows into a second "Book a demo" beside the original
# "Book a Demo". Remove the v0.11 button (lower-case "Book a demo") and its column wrapper from those rows.
removed = 0
for row in s.select('[data-block=package-ctas]'):
    for a in row.find_all('a', href=re.compile('leadconnectorhq.com/widget/bookings')):
        if a.get_text(strip=True) == 'Book a demo':
            a.parent.decompose(); removed += 1
assert removed == 2, removed
# FAQ: remove "Do all teachers get access?" and its subscription answer
h = s.find('h4', string=re.compile(r'Do all teachers get access\?'))
ans = h.find_next_sibling('p'); assert 'One subscription' in ans.get_text()
h.decompose(); ans.decompose()
assert retarget_trials(s, 134, 133) == 5
included_line(s, 'Gymnastics is included in the PE and Active School packages.')
open(f, 'w', encoding='utf-8').write(str(s))
print('gymnastics: 2 duplicate demo buttons and 1 FAQ removed, 5 trial links to PE (133), line added')

# ---- Mental Wellbeing
f, s = page('imoves-mental-wellbeing')
sp = [a for a in s.find_all('a', href=True) if a.get_text(strip=True) == 'See Prices']
assert len(sp) == 2
for a in sp:
    wrap = a.parent
    if wrap.name == 'div' and len(wrap.find_all('a')) == 1: wrap.decompose()
    else: a.decompose()
strong = s.find('strong', string=re.compile(r'From just £247 a year,'))
para = strong.parent
strong.decompose()
first = para.find(string=re.compile(r'\S'))
first.replace_with(re.sub(r'^\s*help', 'Help', str(first)))
q = s.find('strong', string=re.compile(r'Does the whole school get access\?')).find_parent('p')
q.decompose()
for p in s.find_all('p'):
    st = p.find('strong')
    if st and re.match(r'\s*8\.\s*Can we try it', st.get_text()):
        st.string = st.get_text().replace('8.', '7.', 1)
# FAQ structured data: drop the same question
import json
for sc in s.find_all('script', attrs={'type': 'application/ld+json'}):
    d = json.loads(sc.string)
    if d.get('@type') == 'FAQPage':
        d['mainEntity'] = [q for q in d['mainEntity'] if q['name'] != 'Does the whole school get access?']
        sc.string = json.dumps(d, ensure_ascii=False)
assert retarget_trials(s, 137, 138) == 4
included_line(s, 'Mental Wellbeing is included in the Active School package.')
open(f, 'w', encoding='utf-8').write(str(s))
print('wellbeing: 2 See Prices removed, price removed, 1 FAQ removed and renumbered, 4 trial links to Active School (138), line added')
