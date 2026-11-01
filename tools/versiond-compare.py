#!/usr/bin/env python3
"""Version D v0.12: one package comparison component, used on the homepage and the pricing page.

Replaces (a) the homepage "Find the right support for your school" PNG (six products, old names,
one price typo, no alt text to speak of) and (b) the five flat cards on /pricing with the same
HTML component on both pages, built from the PRODUCTS data below. Two families, as in the PNG:
PE subscriptions (Dance, PE) and Active School subscriptions (Active Blasts, Active Learning,
Active School). Each product is a card with the feature list (ticks and crosses, labels as in the
PNG), the three price tiers, and the Get button to the platform checkout. Cards in a family share
rows via CSS subgrid so the ticks line up across cards; on a phone they stack.
Names follow Ian's list (Active Learning, not Active 30; PE, Dance without "Primary").
Run after any price or feature change; it rewrites both pages and default/dist/css/compare.css.
"""
import os, re, json
from bs4 import BeautifulSoup

ROOT = '/home/claude/imoves-website'
PLATFORM = 'https://platform.imoves.com/subscribe/'

PRODUCTS = {
    'dance': dict(name='Dance', pid=3, bg='#bfe1f2', btn='#0085ca',
        blurb='Explore over 60 modern dance styles and topics with our expertly developed programme, complete with lesson plans, demo movies, music, and extensive cross-curricular links.',
        prices=(247, 277, 397)),
    'pe': dict(name='PE', pid=4, bg='#fde3cb', btn='#f68d2e',
        blurb='Save up to £848 with our AfPE accredited PE programme, encompassing PE fundamentals, traditional games, OAA, dance, gymnastics, and Pilates. PLUS bonus content like breaktime games, Yoga and line activities.',
        prices=(357, 397, 597)),
    'blasts': dict(name='Active Blasts', pid=1, bg='#f7cecc', btn='#e03c31',
        blurb='Enhance your school day with 250+ Active Blasts for engaging, no-prep brain breaks. Energise and refocus your entire school with no additional planning required!',
        prices=(147, 177, 247)),
    'learning': dict(name='Active Learning', pid=8, bg='#dbcbe2', btn='#702f8a',
        blurb='Save £499 with the Active Learning Bundle, featuring over 250 dynamic Active Blasts and Active Lessons in Maths, Literacy, and Humanities.',
        prices=(247, 277, 397)),
    'school': dict(name='Active School', pid=9, bg='#fdd4dd', btn='#f65275',
        blurb='Unlock our comprehensive library of 2,500+ resources, SAVING up to £1,192 (when compared to buying individual packages). This all-encompassing package covers your entire PE curriculum, Active Learning, Mental Wellbeing and more.',
        prices=(597, 697, 997)),
}

# Feature labels and ticks exactly as on the retired comparison image (1 = included).
FAMILIES = [
    dict(title='PE subscriptions', products=['dance', 'pe'], features=[
        ('Up to 60 Dance Topics and Styles', (1, 1)),
        ('Gymnastics Programme', (0, 1)),
        ("Children's Pilates Programme", (0, 1)),
        ('Holistic PE Skills for Games (36 lessons per year)', (0, 1)),
        ('12 Sports Specific Deep Dives', (0, 1)),
        ('OAA and Athletics', (0, 1)),
        ('Assessment Tools', (1, 1)),
        ('Online Curriculum Planner', (1, 1)),
        ('Online CPD', (1, 1)),
    ]),
    dict(title='Active School subscriptions', products=['blasts', 'learning', 'school'], features=[
        ('250+ Active Blasts Videos', (1, 1, 1)),
        ('Active Learning Lessons 1000+', (0, 1, 1)),
        ('Breaktime Games, Line and Corridor Activities', (0, 1, 1)),
        ('PE programme', (0, 0, 1)),
        ('Mental Wellbeing Programme', (0, 0, 1)),
        ('Online Curriculum Planner', (1, 1, 1)),
        ('Online CPD', (1, 1, 1)),
    ]),
]
TIERS = [('Infant School', 'EYFS+KS1'), ('Junior School', 'KS2'), ('Primary School', 'EYFS,KS1+KS2')]

CSS = """/* Version D v0.12: package comparison component (homepage and /pricing) */
.cmp{max-width:1140px;margin:0 auto;text-align:left;color:#000}
.cmp-family{margin:0 0 36px}
.cmp-family-title{font-weight:700;font-size:1.5rem;color:#702f8a;margin:0 0 14px;text-align:center}
.cmp-grid{display:grid;gap:16px;grid-template-columns:1fr}
.cmp-card{display:grid;grid-template-rows:subgrid;border-radius:8px;box-shadow:0 1rem 3rem rgba(0,0,0,.175);overflow:hidden;transition:transform .2s}
.cmp-card:hover{transform:translateY(-4px)}
.cmp-head{padding:14px 16px;color:#fff;text-align:center;font-weight:700;font-size:1.6rem;line-height:1.2;margin:0}
.cmp-blurb{padding:14px 16px 6px;font-weight:300;font-size:1.05rem;line-height:1.35;margin:0;text-align:center}
.cmp-features{list-style:none;margin:0;padding:8px 16px 4px}
.cmp-features li{display:flex;align-items:flex-start;gap:10px;padding:5px 0;font-size:1rem;line-height:1.3;border-top:1px solid rgba(0,0,0,.08)}
.cmp-features li:first-child{border-top:0}
.cmp-features li.no{color:rgba(0,0,0,.55)}
.cmp-ico{flex:none;width:22px;height:22px;border-radius:50%;margin-top:0;position:relative;display:inline-block}
.yes .cmp-ico{background:#1fa34a}.no .cmp-ico{background:#e02b2b}
.cmp-ico::before,.cmp-ico::after{content:"";position:absolute;background:#fff;border-radius:2px}
.yes .cmp-ico::before{width:6px;height:11px;left:8px;top:3px;transform:rotate(45deg);background:none;border:solid #fff;border-width:0 3px 3px 0;border-radius:0}
.no .cmp-ico::before,.no .cmp-ico::after{width:3px;height:12px;left:9.5px;top:5px;transform:rotate(45deg)}
.no .cmp-ico::after{transform:rotate(-45deg)}
.cmp-tiers{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:12px 16px 4px;font-size:1.05rem}
.cmp-tier{text-align:center;line-height:1.25}
.cmp-tier-name{font-weight:700}
.cmp-tier-ks{font-weight:300;font-size:.85em}
.cmp-price{margin-top:4px;font-weight:700}
.cmp-foot{padding:12px 16px 20px}
.cmp-btn{display:block;text-align:center;color:#fff;text-decoration:none;border:1px solid #733088;border-radius:5px;padding:8px 12px;font-size:1.1rem;font-weight:700}
.cmp-btn:hover{filter:brightness(.92);color:#fff}
.cmp-note{text-align:center;font-weight:300;font-size:1rem;margin:0 auto;max-width:700px}
@media (min-width:768px){.cmp-grid{grid-template-columns:repeat(var(--n),1fr)}.cmp-grid.cmp-2{max-width:760px;margin:0 auto}}
@media (max-width:480px){.cmp-tiers{grid-template-columns:1fr}.cmp-tier{display:grid;grid-template-columns:1fr auto auto;gap:8px;text-align:left}.cmp-price{margin:0}}
"""

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def component(level):
    """level = aria-level for the family titles; product names are one level below."""
    out = ['<div class="cmp">']
    for fam in FAMILIES:
        n = len(fam['products']); rows = 5  # head, blurb, features, tiers, button
        out.append(f'<div class="cmp-family"><div class="cmp-family-title" role="heading" aria-level="{level}">{esc(fam["title"])}</div>')
        out.append(f'<div class="cmp-grid cmp-{n}" style="--n:{n}">')
        for i, key in enumerate(fam['products']):
            p = PRODUCTS[key]
            out.append(f'<div class="cmp-card" style="background:{p["bg"]};grid-row:span {rows}">')
            out.append(f'<div class="cmp-head" role="heading" aria-level="{level+1}" style="background:{p["btn"]}">{esc(p["name"])}</div>')
            out.append(f'<p class="cmp-blurb">{esc(p["blurb"])}</p>')
            out.append(f'<ul class="cmp-features" aria-label="What is included in {esc(p["name"])}">')
            for label, inc in fam['features']:
                yes = inc[i]
                out.append(f'<li class="{"yes" if yes else "no"}"><span class="cmp-ico" aria-hidden="true"></span><span class="sr-only-text" style="position:absolute;left:-9999px">{"Included: " if yes else "Not included: "}</span>{esc(label)}</li>')
            out.append('</ul>')
            out.append('<div class="cmp-tiers">' + ''.join(
                f'<div class="cmp-tier"><div class="cmp-tier-name">{t}</div><div class="cmp-tier-ks">{ks}</div><div class="cmp-price">£{pr}</div></div>'
                for (t, ks), pr in zip(TIERS, p['prices'])) + '</div>')
            out.append(f'<div class="cmp-foot"><a class="cmp-btn" href="{PLATFORM}{p["pid"]}" style="background:{p["btn"]}">Get {esc(p["name"])}</a></div>')
            out.append('</div>')
        out.append('</div></div>')
    out.append('<p class="cmp-note">Prices are per school per year, plus VAT.</p>')
    out.append('</div>')
    return '\n'.join(out)

def add_css(soup, href):
    if not soup.find('link', href=re.compile(r'compare\.css')):
        l = soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': href})
        app = soup.find('link', href=re.compile(r'app\.css')); app.insert_after(l)

os.makedirs(os.path.join(ROOT, 'default/dist/css'), exist_ok=True)
open(os.path.join(ROOT, 'default/dist/css/compare.css'), 'w').write(CSS)

# --- homepage: replace the PNG with the component ---
f = os.path.join(ROOT, 'index.html'); soup = BeautifulSoup(open(f, encoding='utf-8'), 'html.parser')
pic = soup.find('picture', lambda t: False) or soup.find('source', srcset=re.compile('subscription-image'))
pic = pic.parent if pic and pic.name == 'source' else pic
assert pic is not None, 'homepage image not found'
h = soup.find('h3', string=re.compile('Find the right support'))
pic.replace_with(BeautifulSoup(component(level=4), 'html.parser'))
add_css(soup, './default/dist/css/compare.css')
open(f, 'w', encoding='utf-8').write(str(soup))

# --- pricing page: replace the cards with heading + component, drop the old card CSS ---
f = os.path.join(ROOT, 'pricing/index.html'); soup = BeautifulSoup(open(f, encoding='utf-8'), 'html.parser')
grid = soup.select_one('.pr-grid'); assert grid is not None
style = [s for s in soup.find_all('style') if 'pr-grid' in s.text][0]
style.string = '.pr-note{text-align:center;font-weight:300;font-size:1.1rem;margin:0 auto 24px;max-width:700px}'
heading = BeautifulSoup('<h3 class="text-3xl md:text-4xl font-semibold leading-snug px-20 mb-30 text-center text-purple" role="heading" aria-level="1">Find the right support for your school</h3>', 'html.parser')
grid.replace_with(BeautifulSoup(component(level=2), 'html.parser'))
first_note = soup.select_one('.pr-note'); first_note.insert_before(heading)
add_css(soup, '../default/dist/css/compare.css')
# Product schema: keep names/prices in step with the data
for sc in soup.find_all('script', attrs={'type': 'application/ld+json'}):
    d = json.loads(sc.string)
    if d.get('@type') != 'Product': continue
    key = next(k for k, p in PRODUCTS.items() if d['name'] == 'imoves ' + p['name'])
    p = PRODUCTS[key]
    for off, pr in zip(d['offers'], p['prices']): off['price'] = str(pr); off['url'] = PLATFORM + str(p['pid'])
    sc.string = json.dumps(d, ensure_ascii=False)
open(f, 'w', encoding='utf-8').write(str(soup))
print('done: homepage and pricing rebuilt from PRODUCTS/FAMILIES')
