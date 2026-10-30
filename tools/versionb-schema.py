#!/usr/bin/env python3
"""Version B, step 2: structured data and AI discovery. Invisible to visitors.

Adds JSON-LD to each indexable page:
- WebSite (homepage only) and BreadcrumbList (every page, from the URL path and page titles).
- Article on guide/blog pages (Teacher Knowledge Hub, Resource Hub articles, blog-* and how-* pages).
- FAQPage where a page carries a "Frequently Asked Questions" block of numbered Q&A paragraphs.
- Product + Offer for each of the eight products on /pricing.
Writes /llms.txt.
"""
import glob, os, re, json, datetime
import html as html_mod
from bs4 import BeautifulSoup

ROOT = '/home/claude/imoves-website'
SITE = 'https://imoves.com'
TODAY = datetime.date.today().isoformat()
ORG = {"@type": "Organization", "name": "imoves", "url": SITE, "logo": {"@type": "ImageObject", "url": SITE + "/default/dist/ui/og-share.png"}}
log = {'breadcrumb': 0, 'article': 0, 'faq': 0, 'faq_questions': 0, 'product': 0}

titles = {}
for f in glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True):
    if '/version-a/' in f: continue
    html = open(f, encoding='utf-8').read()
    if 'http-equiv="refresh"' in html: continue
    rel = os.path.relpath(os.path.dirname(f), ROOT); path = '/' if rel == '.' else '/' + rel
    m = re.search(r'<title>(.*?)</title>', html, re.S)
    titles[path] = re.sub(r'\s*\|\s*imoves\s*$', '', m.group(1).strip()) if m else path

HUB_PARENTS = {'/teacher-knowledge-hub': 'Teacher Knowledge Hub', '/resource-hub': 'Resource Hub'}

def is_article(path, soup):
    if path.startswith(('/teacher-knowledge-hub/', '/resource-hub/')) and path.count('/') >= 2 and path not in ('/resource-hub/policy-funding', '/resource-hub/mental-health-well-being', '/resource-hub/primary-pe-and-dance-lesson-planning', '/resource-hub/active-advent'):
        return True
    if re.match(r'^/(blog-|how-|what-|where-|7-key|teachers-guide|teaching-|unlock-|girls-in-sport|dance-terminology|structured-active-play|primary-school-active-learning-ideas|sats-survival|where-did|getting-started|imoves-in-the-edtech|nurturing-pe|top-100|walk-to-school|kings-coronation|national-maths|sports-day-planning|make-the-most|empower|empowering)', path):
        return True
    return False

def breadcrumb(path):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
    if path == '/': return None
    parts = path.strip('/').split('/'); acc = ''
    for i, part in enumerate(parts):
        acc += '/' + part
        name = titles.get(acc) or HUB_PARENTS.get(acc) or part.replace('-', ' ').title()
        items.append({"@type": "ListItem", "position": i + 2, "name": name[:80], "item": SITE + acc})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}

def faq(soup):
    heads = [x for x in soup.find_all(['h1', 'h2', 'h3']) if 'frequently asked' in x.get_text().lower()]
    if not heads: return None
    blk = heads[0].find_parent(attrs={'data-block': True})
    nxt = blk.find_next_sibling() if blk is not None else None
    if nxt is None: return None
    qas = []
    for p in nxt.find_all('p'):
        st = p.find('strong')
        if not st: continue
        q = re.sub(r'^\d+\.\s*', '', st.get_text(' ', strip=True)).strip()
        # answer = text of everything after the <strong> element
        a = ' '.join(x.get_text(' ', strip=True) if hasattr(x, 'get_text') else str(x) for x in st.next_siblings)
        a = re.sub(r'\s+', ' ', a).strip()
        if not a:  # question and answer in separate paragraphs
            sib = p.find_next_sibling('p')
            if sib is not None and not sib.find('strong'):
                a = re.sub(r'\s+', ' ', sib.get_text(' ', strip=True))
        if len(q) > 8 and len(a) > 15 and q.endswith('?'):
            qas.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
    if len(qas) < 2: return None
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": qas}

def article(path, soup, desc):
    h1 = soup.find('h1'); headline = (h1.get_text(' ', strip=True) if h1 else titles.get(path, ''))[:110]
    img = None
    og = soup.find('meta', attrs={'property': 'og:image'})
    main = soup.find(attrs={'data-block': 'main-content'})
    if main is not None:
        im = main.find('img', src=True)
        if im: img = SITE + '/' + re.sub(r'^(\.\./|\./)+', '', im['src'])
    return {"@context": "https://schema.org", "@type": "Article", "headline": headline, "description": desc, "url": SITE + path,
            "image": img or (og['content'] if og else None), "author": ORG, "publisher": ORG, "dateModified": TODAY, "inLanguage": "en-GB",
            "mainEntityOfPage": {"@type": "WebPage", "@id": SITE + path}}

PRODUCTS = [
 ("Active Blasts","Enhance your school day with 250+ Active Blasts for engaging, no-prep brain breaks.",("147","177","247"),"1"),
 ("PE","AfPE accredited primary PE programme covering fundamentals, games, OAA, dance, gymnastics and Pilates.",("357","397","597"),"4"),
 ("Active Learning","Active Learning Bundle with 250+ Active Blasts and Active Lessons in Maths, Literacy and Humanities.",("247","277","397"),"8"),
 ("Active School","Whole-school programme: 2,500+ resources across PE, Active 30, mental wellbeing and more.",("597","697","997"),"9"),
 ("Dance","Over 60 modern dance styles and topics with lesson plans, demo movies and music.",("247","277","397"),"3"),
 ("Gymnastics","12-week primary gymnastics programme with lesson plans, demo movies, music and resources.",("147","177","247"),"6"),
 ("Wellbeing","Mental Health and Wellbeing programme with structured activities for all year groups.",("247","277","397"),"11"),
 ("After-School","Active Adventure club for KS1 after-school clubs and lunchtime activities.",("150","150","150"),"12"),
]
TIERS = (("Infant School (EYFS and KS1)"),("Junior School (KS2)"),("Primary School (EYFS, KS1 and KS2)"))
def products():
    out = []
    for name, desc, prices, n in PRODUCTS:
        offers = [{"@type": "Offer", "name": f"{name} - {t}", "price": p, "priceCurrency": "GBP", "availability": "https://schema.org/InStock",
                   "url": f"https://platform.imoves.com/subscribe/{n}", "eligibleCustomerType": "https://schema.org/Business"} for t, p in zip(TIERS, prices)]
        out.append({"@context": "https://schema.org", "@type": "Product", "name": f"imoves {name}", "description": desc, "brand": {"@type": "Brand", "name": "imoves"},
                    "url": SITE + "/pricing", "offers": offers, "audience": {"@type": "EducationalAudience", "educationalRole": "teacher"}})
    return out

for f in sorted(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)):
    if '/version-a/' in f: continue
    html = open(f, encoding='utf-8').read()
    if 'http-equiv="refresh"' in html: continue
    rel = os.path.relpath(os.path.dirname(f), ROOT); path = '/' if rel == '.' else '/' + rel
    soup = BeautifulSoup(html, 'html.parser')
    robots = soup.find('meta', attrs={'name': 'robots'})
    if robots is not None and 'noindex' in (robots.get('content') or ''): continue
    # remove any schema we added on a previous run
    for sc in soup.find_all('script', attrs={'data-vb': 'schema'}): sc.decompose()
    d = soup.find('meta', attrs={'name': 'description'}); desc = (d.get('content') if d else '') or ''
    blocks = []
    if path == '/':
        blocks.append({"@context": "https://schema.org", "@type": "WebSite", "name": "imoves", "url": SITE + "/", "description": desc, "publisher": ORG, "inLanguage": "en-GB"})
    bc = breadcrumb(path)
    if bc: blocks.append(bc); log['breadcrumb'] += 1
    if is_article(path, soup): blocks.append(article(path, soup, desc)); log['article'] += 1
    fq = faq(soup)
    if fq: blocks.append(fq); log['faq'] += 1; log['faq_questions'] += len(fq['mainEntity'])
    if path == '/pricing': blocks += products(); log['product'] += len(PRODUCTS)
    for b in blocks:
        tag = soup.new_tag('script', type='application/ld+json'); tag['data-vb'] = 'schema'
        tag.string = json.dumps(b, ensure_ascii=False, separators=(',', ':'))
        soup.head.append(tag)
    open(f, 'w', encoding='utf-8').write(str(soup))

# llms.txt
key = ['/', '/active-school', '/active-learning', '/active-blasts', '/primary-pe', '/dance', '/imoves-gymnastics', '/imoves-mental-wellbeing', '/mats', '/cpd-for-primary-school-teachers', '/pricing', '/about-us', '/team', '/contact-us', '/teacher-knowledge-hub', '/resource-hub']
lines = ["# imoves", "", "> imoves is a UK platform of ready-to-use primary school PE, active learning, movement break (Active Blasts), dance, gymnastics and wellbeing resources, made so that non-specialist teachers can get children moving throughout the school day with less planning. AfPE Approved Curriculum Resource. 4,000+ lessons and activities. Used by UK primary schools for over 10 years. Published by imoves active education ltd, 109 Rustlings Road, Sheffield, S11 7AB. Phone +44 114 266 1061. Email kirsty@imoves.com.", "",
         "Teachers log in and use the resources at https://platform.imoves.com. Schools subscribe per product and per key stage; current prices are on the pricing page. A free 28-day trial is available at https://platform.imoves.com/sign-up.", "", "## Main pages", ""]
for p in key:
    lines.append(f"- [{html_mod.unescape(titles.get(p, p))}]({SITE}{p})")
lines += ["", "## Guides for teachers (Teacher Knowledge Hub and Resource Hub)", ""]
for p in sorted(titles):
    if p.startswith(('/teacher-knowledge-hub/', '/resource-hub/')) and p.count('/') >= 2:
        lines.append(f"- [{html_mod.unescape(titles[p])}]({SITE}{p})")
lines += ["", "## Optional", "", f"- [Sitemap]({SITE}/sitemap.xml)", f"- [Terms and conditions]({SITE}/terms-and-conditions)", f"- [Privacy policy]({SITE}/privacy-policy)", ""]
open(os.path.join(ROOT, 'llms.txt'), 'w').write('\n'.join(lines))
json.dump(log, open(os.path.join(ROOT, 'tools', 'versionb-schema.json'), 'w'), indent=1)
print(log)
