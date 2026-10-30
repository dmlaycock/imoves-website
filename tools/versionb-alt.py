#!/usr/bin/env python3
"""Version B, step 3: alt text for images that have none. Invisible to sighted visitors.

Rules, in order:
1. Wistia swatch placeholders and other purely decorative images -> alt="" (explicitly decorative).
2. Video thumbnails (vimeo-thumbnails) -> "Video: <nearest title above>" or "Video" if none.
3. Image inside a link with a title attribute -> that title.
4. Known logo/badge filenames -> brand or award name.
5. Otherwise -> cleaned filename ("active-30-small.png" -> "Active 30"), with the page's H1 as context
   when the filename is numeric or meaningless ("1.png", "adobestock162376827.jpg").
Writes tools/versionb-alt.json with every alt set, for review.
"""
import glob, os, re, json
from bs4 import BeautifulSoup

ROOT = '/home/claude/imoves-website'
log = {}
LOGOS = {
    'imoves-im-logo-white-on-purple-1': 'imoves logo',
    'imovement-powered-by-imoves-2': 'The imovement, powered by imoves',
    'hundred-winner': 'HundrED Global Collection winner badge',
    'hundred-logo': 'HundrED logo',
    'edtech-imapct-evidencebadge-1': 'EdTech Impact evidence badge',
    'bett': 'Bett Awards logo', 'bett-winner': 'Bett Awards winner', 'bett-2020-highly-commended': 'Bett Awards 2020 highly commended',
    'bett-awards-2022-finalist': 'Bett Awards 2022 finalist', 'bett-awards-finalist-2022': 'Bett Awards 2022 finalist',
    'era-2020-finalist': 'Education Resources Awards 2020 finalist', 'era2021-finalist-logo-cmyk': 'Education Resources Awards 2021 finalist',
    'era2022-finalist-logo-cmyk': 'Education Resources Awards 2022 finalist', 'uk-active': 'ukactive logo', 'uk-activelab': 'ukactive ActiveLab logo',
    '10-october-white-logo': 'imoves',
}
MEANINGLESS = re.compile(r'^(\d+|adobestock\d+|untitled.*|screenshot.*|chatgpt-image.*|bespoke-pages.*|website-templates.*|landing-page-images.*|image\d*|img\d*|\d+x\d+.*)$', re.I)

def clean_name(name):
    base = re.sub(r'\.[a-z0-9]{2,5}$', '', name, flags=re.I)
    base = re.sub(r'-\d{3,}x\d{3,}(-px)?', '', base)
    base = re.sub(r'(-\d+)+$', '', base)
    words = re.sub(r'[-_]+', ' ', base).strip()
    words = re.sub(r'\s+', ' ', words)
    if not words: return ''
    out = words[0].upper() + words[1:]
    out = re.sub(r'\bpe\b', 'PE', out, flags=re.I).replace('Afpe', 'AfPE').replace('afpe', 'AfPE').replace('Ks1', 'KS1').replace('Ks2', 'KS2').replace('Eyfs', 'EYFS').replace('Cpd', 'CPD').replace('Sats', 'SATs').replace('Imoves', 'imoves')
    return out

def nearest_title(img):
    # climb a few levels, look for a preceding sibling or child element with short bold/heading text
    node = img
    for _ in range(5):
        node = node.parent
        if node is None: break
        for cand in node.find_all(['h1', 'h2', 'h3', 'h4', 'div', 'p'], recursive=True):
            if cand.find('img'): continue
            t = re.sub(r'\s+', ' ', cand.get_text(' ', strip=True))
            cls = ' '.join(cand.get('class') or [])
            if 3 <= len(t) <= 70 and ('font-bold' in cls or cand.name in ('h1', 'h2', 'h3', 'h4')):
                return t
    return None

for f in sorted(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)):
    if '/version-a/' in f: continue
    html = open(f, encoding='utf-8').read()
    if 'http-equiv="refresh"' in html: continue
    rel = os.path.relpath(os.path.dirname(f), ROOT); path = '/' if rel == '.' else '/' + rel
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.find('h1'); page_ctx = re.sub(r'\s+', ' ', h1.get_text(' ', strip=True)) if h1 else ''
    changed = False
    for img in soup.find_all('img'):
        if (img.get('alt') or '').strip(): continue
        src = img.get('src') or img.get('data-src') or ''
        name = src.split('/')[-1]; base = re.sub(r'\.[a-z0-9]{2,5}$', '', name, flags=re.I)
        alt = None
        if 'wistia.com' in src or name == 'swatch' or 'swatch' in src:
            alt = ''  # decorative placeholder behind the video player
        elif 'vimeo-thumbnail' in src:
            t = nearest_title(img); alt = f'Video: {t}' if t else 'Video'
        else:
            a = img.find_parent('a')
            if a is not None and (a.get('title') or '').strip() and a['title'].strip().lower() != 'play video':
                alt = a['title'].strip()
            elif base in LOGOS:
                alt = LOGOS[base]
            elif MEANINGLESS.match(base) or len(clean_name(name)) < 4:
                alt = page_ctx if page_ctx else 'imoves'
            else:
                alt = clean_name(name)
        img['alt'] = alt
        log.setdefault(path, []).append([name, alt]); changed = True
    if changed:
        open(f, 'w', encoding='utf-8').write(str(soup))

json.dump(log, open(os.path.join(ROOT, 'tools', 'versionb-alt.json'), 'w'), indent=1, ensure_ascii=False)
n = sum(len(v) for v in log.values()); dec = sum(1 for v in log.values() for a in v if a[1] == '')
print('alt set on', n, 'images across', len(log), 'pages;', dec, 'marked decorative')
