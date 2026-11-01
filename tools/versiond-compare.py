#!/usr/bin/env python3
"""Version D: the package comparison, generated from one data block for two pages.

v0.12 introduced one component on both pages (two families of cards). v0.13 replaces it, after
David's review, with:
  /pricing   a single comparison matrix: products across (price order), features down in three
             groups (Included with every package, Physical education, Active classroom), ticks and
             crosses, then Infant / Junior / Primary price rows and the Get buttons.
  homepage   five compact cards in the same order, each listing only what it includes, "from" price
             and the three tiers, Get button. Same PRODUCTS/GROUPS data, so the two cannot drift.
Names follow Ian's list (Active Learning, not Active 30; PE and Dance without "Primary").
Feature rows come from the retired comparison PNG plus rows agreed with David on 1 Nov 2026
(unlimited accounts and usage, demonstration videos, free trial, afPE approval, Active Play
training); all are for imoves to review (issues log #15).
Run after any price or feature change; it rewrites both pages and default/dist/css/compare.css.
"""
import os, re, json
from bs4 import BeautifulSoup

ROOT = '/home/claude/imoves-website'
PLATFORM = 'https://platform.imoves.com/subscribe/'

# key, name, card background, header/button colour, platform product id, prices (Infant, Junior, Primary)
PRODUCTS = [
    ('blasts',   'Active Blasts',   '#f7cecc', '#e03c31', 1, (147, 177, 247)),
    ('learning', 'Active Learning', '#dbcbe2', '#702f8a', 8, (247, 277, 397)),
    ('dance',    'Dance',           '#bfe1f2', '#0085ca', 3, (247, 277, 397)),
    ('pe',       'PE',              '#fde3cb', '#f68d2e', 4, (357, 397, 597)),
    ('school',   'Active School',   '#fdd4dd', '#f65275', 9, (597, 697, 997)),
]
ALL = {'blasts', 'learning', 'dance', 'pe', 'school'}
PE_FAMILY = {'pe', 'school'}
GROUPS = [
    ('Included with every package', [
        ('Unlimited teacher accounts', ALL),
        ('Unlimited admin accounts', ALL),
        ('Unlimited usage', ALL),
        ('Child-facing demonstration videos', ALL),
        ('Online Curriculum Planner', ALL),
        ('Online CPD', ALL),
        ('28-day free trial', ALL),
    ]),
    ('Physical education', [
        ('Holistic PE Skills for Games (36 lessons per year)', PE_FAMILY),
        ('12 Sports Specific Deep Dives', PE_FAMILY),
        ('OAA and Athletics', PE_FAMILY),
        ('Gymnastics Programme', PE_FAMILY),
        ("Children's Pilates Programme", PE_FAMILY),
        ('Up to 60 Dance Topics and Styles', {'dance', 'pe', 'school'}),
        ('Assessment Tools', {'dance', 'pe', 'school'}),
        ('afPE Approved Curriculum Resource', {'dance', 'pe', 'school'}),
    ]),
    ('Active classroom', [
        ('250+ Active Blasts Videos', {'blasts', 'learning', 'school'}),
        ('1000+ Active Learning Lessons in Maths, Literacy and Humanities', {'learning', 'school'}),
        ('Breaktime Games', {'learning', 'school'}),
        ('Line and Corridor Activities', {'learning', 'school'}),
        ('Active Play breaktime supervisor training', {'learning', 'school'}),
        ('Mental Wellbeing Programme', {'school'}),
    ]),
]
TIERS = [('Infant school', 'EYFS and KS1'), ('Junior school', 'KS2'), ('Primary school', 'EYFS, KS1 and KS2')]
VAT_NOTE = 'Prices are per school per year, plus VAT.'

CSS = """/* Version D v0.13: package comparison (matrix on /pricing, cards on the homepage) */
.cmp{max-width:1140px;margin:0 auto;text-align:left;color:#000}
.cmp .cmp-ico{display:inline-block;width:20px;height:20px;border-radius:50%;position:relative;vertical-align:middle}
.cmp .yes{background:#1fa34a}.cmp .no{background:#e02b2b}
.cmp .yes::before{content:"";position:absolute;width:5px;height:10px;left:7px;top:3px;border:solid #fff;border-width:0 3px 3px 0;transform:rotate(45deg)}
.cmp .no::before,.cmp .no::after{content:"";position:absolute;width:3px;height:11px;left:8.5px;top:4.5px;background:#fff;border-radius:2px;transform:rotate(45deg)}
.cmp .no::after{transform:rotate(-45deg)}
.cmp-btn{display:block;text-align:center;color:#fff;text-decoration:none;border:1px solid #733088;border-radius:5px;padding:8px 6px;font-size:.95rem;font-weight:700;line-height:1.2}
.cmp-btn:hover{filter:brightness(.92);color:#fff}
.cmp-note{text-align:center;font-weight:300;font-size:1rem;margin:18px auto 0;max-width:700px}
/* matrix */
.cmp-scroll{border-radius:8px;box-shadow:0 1rem 3rem rgba(0,0,0,.175)}
.cmp-table{width:100%;table-layout:fixed;border-collapse:separate;border-spacing:0;background:#fff}
.cmp-table th,.cmp-table td{padding:9px 10px;text-align:center;font-size:.95rem;border-bottom:1px solid #eee;line-height:1.3}
.cmp-table th.f,.cmp-table td.f{text-align:left;width:31%}
.cmp-table thead th{color:#fff;font-weight:700;font-size:1.05rem;padding:14px 6px}
.cmp-table tr.grp td{background:#f3eef6;color:#702f8a;font-weight:700;text-align:left;font-size:.85rem;letter-spacing:.03em;text-transform:uppercase;padding-top:11px}
.cmp-table tr.price td{font-weight:700;font-size:1.1rem}
.cmp-table tr.price th.f{font-size:.95rem}.cmp-table tr.price th.f small{display:block;font-weight:300;font-size:.8rem}
.cmp-table tr.price.first td{border-top:2px solid #702f8a}
.cmp-table tr.buy td{padding:12px 6px 16px;border-bottom:0}
.cmp-mobile{display:none}
@media (max-width:767px){.cmp-desktop{display:none}.cmp-mobile{display:block}}
/* cards */
.cmp-grid{display:grid;grid-template-columns:1fr;gap:12px}
.cmp-card{border-radius:8px;box-shadow:0 1rem 3rem rgba(0,0,0,.175);overflow:hidden;display:flex;flex-direction:column;transition:transform .2s}
.cmp-card:hover{transform:translateY(-4px)}
.cmp-head{color:#fff;font-weight:700;font-size:1.15rem;text-align:center;padding:12px 8px;line-height:1.2;margin:0}
.cmp-price{text-align:center;padding:12px 8px 4px;line-height:1.3}
.cmp-price b{font-size:1.5rem;display:block}.cmp-price small{display:block;font-weight:300;font-size:.8rem}
.cmp-features{list-style:none;margin:0;padding:8px 14px;flex:1}
.cmp-features li{font-size:.88rem;padding:5px 0;border-top:1px solid rgba(0,0,0,.08);display:flex;gap:7px;align-items:flex-start;line-height:1.3}
.cmp-features li:first-child{border-top:0}
.cmp-features .cmp-ico{flex:none;width:16px;height:16px;margin-top:1px}
.cmp-features .yes::before{width:4px;height:8px;left:5px;top:2px}
.cmp-foot{padding:10px 14px 16px}
@media (min-width:600px){.cmp-grid{grid-template-columns:repeat(2,1fr)}}
@media (min-width:1024px){.cmp-grid{grid-template-columns:repeat(5,1fr)}}
"""

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def ico(yes): return f'<span class="cmp-ico {"yes" if yes else "no"}" aria-hidden="true"></span><span style="position:absolute;left:-9999px">{"Included" if yes else "Not included"}</span>'

def matrix():
    o = ['<div class="cmp"><div class="cmp-scroll"><table class="cmp-table"><caption style="position:absolute;left:-9999px">What each imoves package includes, with prices</caption><thead><tr><th class="f" scope="col"><span style="position:absolute;left:-9999px">Feature</span></th>']
    o += [f'<th scope="col" style="background:{btn}">{esc(name)}</th>' for k, name, bg, btn, pid, pr in PRODUCTS]
    o.append('</tr></thead><tbody>')
    for g, feats in GROUPS:
        o.append(f'<tr class="grp"><td colspan="{len(PRODUCTS)+1}">{esc(g)}</td></tr>')
        for f, s in feats:
            o.append(f'<tr><th scope="row" class="f" style="font-weight:400">{esc(f)}</th>' + ''.join(f'<td style="background:{bg}66">{ico(k in s)}</td>' for k, name, bg, btn, pid, pr in PRODUCTS) + '</tr>')
    for i, (t, ks) in enumerate(TIERS):
        o.append(f'<tr class="price{" first" if i == 0 else ""}"><th scope="row" class="f">{t}<small>{ks}</small></th>' + ''.join(f'<td style="background:{bg}66">£{pr[i]}</td>' for k, name, bg, btn, pid, pr in PRODUCTS) + '</tr>')
    o.append('<tr class="buy"><td class="f"></td>' + ''.join(f'<td style="background:{bg}66"><a class="cmp-btn" style="background:{btn}" href="{PLATFORM}{pid}">Get {esc(name)}</a></td>' for k, name, bg, btn, pid, pr in PRODUCTS) + '</tr>')
    o.append(f'</tbody></table></div><p class="cmp-note">{VAT_NOTE}</p></div>')
    return ''.join(o)

def cards(level, link=True):
    o = ['<div class="cmp"><div class="cmp-grid">']
    for k, name, bg, btn, pid, pr in PRODUCTS:
        inc = [f for g, feats in GROUPS[1:] for f, s in feats if k in s]  # the common group is stated once below the cards
        o.append(f'<div class="cmp-card" style="background:{bg}"><div class="cmp-head" role="heading" aria-level="{level}" style="background:{btn}">{esc(name)}</div>'
                 f'<div class="cmp-price"><small>from</small><b>£{pr[0]}</b><small>Infant £{pr[0]} · Junior £{pr[1]} · Primary £{pr[2]}</small></div>'
                 f'<ul class="cmp-features" aria-label="What is included in {esc(name)}">' + ''.join(f'<li>{ico(True)}{esc(f)}</li>' for f in inc) +
                 f'</ul><div class="cmp-foot"><a class="cmp-btn" style="background:{btn}" href="{PLATFORM}{pid}">Get {esc(name)}</a></div></div>')
    def lc(f): return f if f.startswith('Online') else f[0].lower() + f[1:]
    common = [('the ' + f if f == 'Online Curriculum Planner' else lc(f)) for f, s in GROUPS[0][1]]
    common[-1] = 'a ' + common[-1] if common[-1].startswith('28-day') else common[-1]
    common_txt = ', '.join(common[:-1]) + ' and ' + common[-1]
    o.append(f'</div><p class="cmp-note" style="margin-top:22px;font-weight:400">Every package includes {esc(common_txt)}.</p>')
    more = ' <a href="./pricing/" style="color:#702f8a;font-weight:700">Compare everything that is included</a>' if link else ''
    o.append(f'<p class="cmp-note" style="margin-top:8px">{VAT_NOTE}{more}</p></div>')
    return ''.join(o)

def add_css(soup, href):
    if not soup.find('link', href=re.compile(r'compare\.css')):
        l = soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': href})
        soup.find('link', href=re.compile(r'app\.css')).insert_after(l)

os.makedirs(os.path.join(ROOT, 'default/dist/css'), exist_ok=True)
open(os.path.join(ROOT, 'default/dist/css/compare.css'), 'w').write(CSS)

# --- homepage: cards (replaces the v0.12 component or the original PNG) ---
f = os.path.join(ROOT, 'index.html'); soup = BeautifulSoup(open(f, encoding='utf-8'), 'html.parser')
old = soup.select_one('.cmp')
if old is None:
    src = soup.find('source', srcset=re.compile('subscription-image')); old = src.parent if src else None
assert old is not None, 'homepage comparison block not found'
old.replace_with(BeautifulSoup(cards(level=4), 'html.parser'))
add_css(soup, './default/dist/css/compare.css')
open(f, 'w', encoding='utf-8').write(str(soup))

# --- pricing page: matrix (replaces the v0.12 component; the v0.12 H1 and notes stay) ---
f = os.path.join(ROOT, 'pricing/index.html'); soup = BeautifulSoup(open(f, encoding='utf-8'), 'html.parser')
old = soup.select_one('.cmp'); assert old is not None, 'pricing comparison block not found'
# matrix for desktop and tablet; the card view (same data) for phones, where a six-column table cannot fit
old.replace_with(BeautifulSoup('<div class="cmp-desktop">' + matrix() + '</div><div class="cmp-mobile">' + cards(level=2, link=False) + '</div>', 'html.parser'))
add_css(soup, '../default/dist/css/compare.css')
# Product schema: keep prices and checkout links in step with the data
by_name = {name: (pid, pr) for k, name, bg, btn, pid, pr in PRODUCTS}
for sc in soup.find_all('script', attrs={'type': 'application/ld+json'}):
    d = json.loads(sc.string)
    if d.get('@type') != 'Product': continue
    pid, pr = by_name[d['name'].replace('imoves ', '')]
    for off, p in zip(d['offers'], pr): off['price'] = str(p); off['url'] = PLATFORM + str(pid)
    sc.string = json.dumps(d, ensure_ascii=False)
open(f, 'w', encoding='utf-8').write(str(soup))
print('done: homepage cards and pricing matrix rebuilt from PRODUCTS/GROUPS')
