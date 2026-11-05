#!/usr/bin/env python3
"""v0.23: carry across imoves' 5 November 2026 edit of the Active Advent page on the old (Bespoke) site.

tools/live-drift.py found /active-advent was the only page changed since the copy (158 of 160 the same; the
other difference is the CMS's own /sitemap page, which only lists the renamed page and is already removed).
The edit is wording and two images, in the same blocks and layout. This script copies the new wording into
our page and keeps what the new site adds: the Cloudflare Stream videos, WebP images (image-set), the
shortened meta descriptions and the breadcrumb structured data.

Two obvious typos on the live page are corrected (David to tell imoves): the meta description starts "oin"
(for "Join"), and the prize line says "Davis Sports" (the partner is Davies Sports).
Usage: python3 tools/v023-advent.py <saved copy of https://imoves.com/active-advent> <folder with the two new jpgs>
"""
import os, re, sys, json, shutil
from bs4 import BeautifulSoup
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE, NEWIMG = sys.argv[1], sys.argv[2]
PAGE = os.path.join(ROOT, 'active-advent', 'index.html')
IMGDIR = os.path.join(ROOT, 'images/800x450/0x0-0x0/active-advent')

live = BeautifulSoup(open(LIVE, encoding='utf-8'), 'html.parser')
soup = BeautifulSoup(open(PAGE, encoding='utf-8'), 'html.parser')
lb, cb = live.select('[data-block]'), soup.select('[data-block]')
assert [b['data-block'] for b in lb] == [b['data-block'] for b in cb] == \
    ['home-banner', 'image-and-usp', 'cta-bar', 'image-and-usp', 'videos-block', 'cta-bar', 'images-block', 'main-content']

# 1. the two new images (and WebP versions, as for every other content image)
for n in (1, 2):
    name = f'copy-of-landing-page-images-active-advent-{n}'
    shutil.copy(os.path.join(NEWIMG, f'advent-new-{n}.jpg'), os.path.join(IMGDIR, name + '.jpg'))
    Image.open(os.path.join(IMGDIR, name + '.jpg')).save(os.path.join(IMGDIR, name + '.webp'), 'WEBP', quality=82, method=6)

def relative(block):
    """Live blocks use absolute https://imoves.com/... addresses; the copy uses relative ones."""
    s = str(block).replace('https://imoves.com/images/', '../images/')
    return BeautifulSoup(s, 'html.parser').find(attrs={'data-block': True})

def image_set(block):
    """Same treatment as the rest of the site: WebP first, original as the fallback."""
    for d in block.find_all(style=re.compile(r"background-image:\s*url\('\.\./images/")):
        src = re.search(r"url\('([^']+)'\)", d['style']).group(1)
        base, ext = os.path.splitext(src)
        mime = 'image/jpeg' if ext.lower() in ('.jpg', '.jpeg') else 'image/png'
        assert os.path.exists(os.path.join(ROOT, 'active-advent', base + '.webp')), base
        d['style'] = (f"background-image:url('{src}');background-image:image-set(url({base}.webp) type('image/webp'),"
                      f"url({src}) type('{mime}'))")
    return block

# 2. banner, the two text-and-image blocks and both call-to-action bars: the live wording
for i in (0, 1, 2, 3, 5):
    new = image_set(relative(lb[i]))
    cb[i].replace_with(new)
cb = soup.select('[data-block]')

# typo in the live prize line
for st in soup.find_all('strong', string=re.compile('Davis Sports')):
    st.string = st.string.replace('Davis Sports', 'Davies Sports')

# 3. videos: new heading and the new closing paragraph; our Cloudflare Stream players stay
vh_live, vh = lb[4].find('h3'), cb[4].find('h3')
vh.string = vh_live.get_text()
extra = lb[4].find_all('div', class_='text-content', recursive=True)[-1]
assert 'little taste of the fun' in extra.get_text()
if 'little taste of the fun' not in cb[4].get_text():
    cb[4].find('div', class_='row').append(BeautifulSoup(str(extra), 'html.parser'))

# 4. head: title, descriptions, social titles, breadcrumb
TITLE = live.title.get_text(strip=True)                                  # "... | imoves"
SHORT = TITLE.rsplit(' | ', 1)[0]
DESC = live.find('meta', attrs={'name': 'description'})['content']
DESC = re.sub(r'^oin ', 'Join ', DESC)
soup.title.string = TITLE
for attrs in ({'name': 'description'}, {'property': 'og:description'}, {'name': 'twitter:description'}):
    soup.find('meta', attrs=attrs)['content'] = DESC
for attrs in ({'property': 'og:title'}, {'name': 'twitter:title'}):
    soup.find('meta', attrs=attrs)['content'] = SHORT
for sc in soup.find_all('script', attrs={'type': 'application/ld+json'}):
    d = json.loads(sc.string)
    if d.get('@type') == 'BreadcrumbList':
        d['itemListElement'][-1]['name'] = SHORT
        sc.string = json.dumps(d, ensure_ascii=False, separators=(',', ':'))

open(PAGE, 'w', encoding='utf-8').write(str(soup))
print('active-advent updated:', TITLE)
