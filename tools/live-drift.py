#!/usr/bin/env python3
"""Compare every page on the live imoves.com with the original copy (version-a) and report any page whose
text or images have changed since the copy was taken, so CMS edits are not lost at go-live. Usage: python3 tools/live-drift.py"""
import re, sys, requests, concurrent.futures as cf
from bs4 import BeautifulSoup
import os
ROOT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'version-a')
paths=[l.strip() for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'live-pages.txt')) if l.strip()]
def text_of(html):
    s=BeautifulSoup(html,'html.parser')
    for t in s(['script','style','noscript']): t.decompose()
    for h in s.select('#justreview-testimonials'):   # the expired JustReview block, removed on purpose (issues log)
        h.decompose()
    txt=re.sub(r'\s+',' ',s.body.get_text(' ',strip=True) if s.body else '')
    for known in ('Our latest reviews...', '5-Star Rated By Teachers And Loved By Over 150,000 Kids', 'What to teachers say about imoves?', 'Trusted by THOUSANDS of happy primary school teachers:'):
        txt=re.sub(r'\s*'+re.escape(known)+r'\s*',' ',txt)
    txt=re.sub(r'\s+',' ',txt).strip()
    imgs=sorted(set(re.sub(r'^.*?/(images|default)/',r'\1/',i.get('src') or i.get('data-src') or '').split('?')[0] for i in s.find_all('img') if (i.get('src') or i.get('data-src'))))
    title=s.title.get_text(strip=True) if s.title else ''
    return txt,imgs,title
def check(p):
    try:
        r=requests.get('https://imoves.com'+p, timeout=30, headers={'User-Agent':'Mozilla/5.0 (site comparison)'})
        live=text_of(r.text)
    except Exception as e:
        return p,'ERR '+str(e)[:60]
    f=ROOT+('/index.html' if p=='/' else p+'/index.html')
    try: loc=text_of(open(f,encoding='utf-8').read())
    except Exception as e: return p,'NOLOCAL'
    out=[]
    if r.status_code!=200: out.append(f'status {r.status_code} final {r.url}')
    if live[0]!=loc[0]:
        a,b=live[0],loc[0]; i=0
        while i<min(len(a),len(b)) and a[i]==b[i]: i+=1
        out.append(f'TEXT live[{a[max(0,i-60):i+120]}] copy[{b[max(0,i-60):i+120]}]')
    if live[1]!=loc[1]: out.append(f'IMG +{sorted(set(live[1])-set(loc[1]))[:4]} -{sorted(set(loc[1])-set(live[1]))[:4]}')
    return p,' | '.join(out) or 'same'
with cf.ThreadPoolExecutor(6) as ex:
    res=list(ex.map(check,paths))
same=[p for p,r in res if r=='same']
print('same',len(same),'of',len(res))
for p,r in res:
    if r!='same': print(p,'::',r[:700])
