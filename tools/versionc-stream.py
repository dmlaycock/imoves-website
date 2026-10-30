#!/usr/bin/env python3
"""Version C, step 1: replace every Wistia popover embed with a Cloudflare Stream player.

Each Wistia block on the site is the same shape:
  <div class="wistia_responsive_padding" style="padding:56.25% 0 0 0; position:relative;">
    <div class="wistia_responsive_wrapper" ...>
      <div class="wistia_embed wistia_async_<id> popover=true popoverAnimateThumbnail=true" ...>
        <div class="wistia_swatch">...</div>
It renders as a 16:9 rounded thumbnail with a purple play button; clicking opens the video in a
lightbox and autoplays. This script replaces it with:
  <div class="cf-video" data-uid="<stream uid>" data-title="<name>">
    <button class="cf-video-thumb"><picture>...thumbnail...</picture><span class="cf-video-play"/></button>
  </div>
plus one shared stylesheet/script (video/cf-player.css, video/cf-player.js) that reproduces the
thumbnail look (17.5px radius, 127x81 purple play button at 76% opacity) and the lightbox
(dark overlay, centred 16:9 player, close on X, overlay click or Escape) and loads the Stream
iframe with autoplay only when clicked. The Wistia <script> tags are removed.
Wistia ids with no Stream UID keep their Wistia block (fallback) and are reported.
"""
import glob, os, re, json
from bs4 import BeautifulSoup

ROOT = '/home/claude/imoves-website'
MAP = json.load(open('/home/claude/imoves-site/website-map.json'))
CUSTOMER = 'customer-q4gm0gw925cd2f03.cloudflarestream.com'
THUMBS = os.path.join(ROOT, 'video', 'thumbs')

CSS = """/* Version C: Cloudflare Stream player (replaces Wistia popover embeds) */
.cf-video{position:relative;padding-top:56.25%;width:100%}
.cf-video-thumb{position:absolute;inset:0;width:100%;height:100%;border:0;padding:0;margin:0;background:#1c1c1c;border-radius:17.5px;overflow:hidden;cursor:pointer;display:block}
.cf-video-thumb img{width:100%;height:100%;object-fit:cover;display:block}
.cf-video-play{position:absolute;left:50%;top:50%;width:22.7%;max-width:127px;aspect-ratio:127/81;transform:translate(-50%,-50%);background:rgba(112,47,138,.76);border-radius:13.125px;display:flex;align-items:center;justify-content:center;transition:background .2s}
.cf-video-thumb:hover .cf-video-play,.cf-video-thumb:focus-visible .cf-video-play{background:rgba(112,47,138,1)}
.cf-video-play::after{content:"";display:block;width:0;height:0;border-style:solid;border-width:16px 0 16px 28px;border-color:transparent transparent transparent #fff;margin-left:4px}
.cf-video-thumb:focus-visible{outline:3px solid #fff;outline-offset:-3px}
.cf-lightbox{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.75);display:flex;align-items:center;justify-content:center;padding:24px;opacity:0;transition:opacity .2s}
.cf-lightbox.is-open{opacity:1}
.cf-lightbox-inner{position:relative;width:min(1100px,100%);aspect-ratio:16/9;background:#000;border-radius:8px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.cf-lightbox-inner iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.cf-lightbox-close{position:absolute;top:-40px;right:0;width:36px;height:36px;border:0;background:transparent;color:#fff;font-size:32px;line-height:1;cursor:pointer}
@media (max-width:640px){.cf-lightbox{padding:12px}.cf-lightbox-close{top:-38px}}
"""

JS = """// Version C: Cloudflare Stream lightbox player
(function(){
  var CUSTOMER='%s';
  function open(uid,title){
    var lb=document.createElement('div');lb.className='cf-lightbox';lb.setAttribute('role','dialog');lb.setAttribute('aria-modal','true');lb.setAttribute('aria-label',title||'Video');
    var inner=document.createElement('div');inner.className='cf-lightbox-inner';
    var close=document.createElement('button');close.className='cf-lightbox-close';close.setAttribute('aria-label','Close video');close.innerHTML='&times;';
    var f=document.createElement('iframe');
    f.src='https://'+CUSTOMER+'/'+uid+'/iframe?autoplay=true&preload=true';
    f.allow='accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture; fullscreen';f.setAttribute('allowfullscreen','');f.title=title||'Video';
    inner.appendChild(close);inner.appendChild(f);lb.appendChild(inner);document.body.appendChild(lb);
    document.body.style.overflow='hidden';
    requestAnimationFrame(function(){lb.classList.add('is-open');});
    function shut(){lb.classList.remove('is-open');document.body.style.overflow='';setTimeout(function(){lb.remove();},200);document.removeEventListener('keydown',esc);}
    function esc(e){if(e.key==='Escape')shut();}
    close.addEventListener('click',shut);
    lb.addEventListener('click',function(e){if(e.target===lb)shut();});
    document.addEventListener('keydown',esc);
    close.focus();
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('.cf-video-thumb');if(!b)return;
    var v=b.closest('.cf-video');open(v.getAttribute('data-uid'),v.getAttribute('data-title'));
  });
})();
""" % CUSTOMER

os.makedirs(os.path.join(ROOT, 'video'), exist_ok=True)
open(os.path.join(ROOT, 'video', 'cf-player.css'), 'w').write(CSS)
open(os.path.join(ROOT, 'video', 'cf-player.js'), 'w').write(JS)

def rel(frm_dir, target):
    r = os.path.relpath(target, frm_dir)
    return r if r.startswith('.') else './' + r

swapped = 0; kept = []; pages = 0
for f in sorted(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)):
    if '/version-a/' in f or '/version-b/' in f: continue
    html = open(f, encoding='utf-8').read()
    if 'wistia_embed' not in html: continue
    soup = BeautifulSoup(html, 'html.parser'); d = os.path.dirname(f); changed = False
    for emb in soup.select('.wistia_embed'):
        wid = next((c.replace('wistia_async_', '') for c in emb.get('class', []) if c.startswith('wistia_async_')), None)
        if not wid or wid not in MAP:
            kept.append((os.path.relpath(f, ROOT), wid)); continue
        uid = MAP[wid]['uid']; title = MAP[wid]['name'].replace('&amp;', '&')
        # the outer responsive_padding div is what we replace
        outer = emb.find_parent(class_='wistia_responsive_padding') or emb
        box = soup.new_tag('div', attrs={'class': 'cf-video', 'data-uid': uid, 'data-title': title, 'data-wistia': wid})
        btn = soup.new_tag('button', attrs={'class': 'cf-video-thumb', 'type': 'button', 'aria-label': 'Play video: ' + title})
        webp = os.path.join(THUMBS, wid + '.webp'); jpg = os.path.join(THUMBS, wid + '.jpg')
        if not os.path.exists(jpg):
            img = soup.new_tag('img', attrs={'src': f'https://{CUSTOMER}/{uid}/thumbnails/thumbnail.jpg?time=2s&width=1280&height=720&fit=crop', 'alt': '', 'loading': 'lazy', 'width': '1280', 'height': '720'})
            btn.append(img)
        if os.path.exists(jpg):
            pic = soup.new_tag('picture')
            if os.path.exists(webp):
                src = soup.new_tag('source', attrs={'srcset': rel(d, webp), 'type': 'image/webp'}); pic.append(src)
            img = soup.new_tag('img', attrs={'src': rel(d, jpg), 'alt': '', 'loading': 'lazy', 'width': '1280', 'height': '720'}); pic.append(img)
            btn.append(pic)
        play = soup.new_tag('span', attrs={'class': 'cf-video-play', 'aria-hidden': 'true'}); btn.append(play)
        box.append(btn)
        outer.replace_with(box); swapped += 1; changed = True
    if changed:
        # remove Wistia scripts
        for sc in soup.find_all('script', src=re.compile(r'fast\.wistia\.com')):
            sc.decompose()
        # add player css + js once
        head = soup.head
        if not soup.find('link', href=re.compile(r'cf-player\.css')):
            l = soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': rel(d, os.path.join(ROOT, 'video', 'cf-player.css'))}); head.append(l)
        if not soup.find('script', src=re.compile(r'cf-player\.js')):
            s = soup.new_tag('script', attrs={'src': rel(d, os.path.join(ROOT, 'video', 'cf-player.js')), 'defer': ''}); soup.body.append(s)
        open(f, 'w', encoding='utf-8').write(str(soup)); pages += 1
print('swapped', swapped, 'embeds on', pages, 'pages; kept on Wistia (no UID):', kept)
