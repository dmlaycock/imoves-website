#!/usr/bin/env python3
"""Mirror the public imoves.com site into a static folder.

- Seeds from sitemap.xml plus the homepage, follows every same-site link.
- Saves each page as <path>/index.html so clean URLs work on static hosting.
- Downloads same-origin assets (css, js, images, fonts, documents) including
  url() references inside CSS, and rewrites them to root-relative paths.
- Leaves third-party hosts (Wistia, Google Fonts, LeadConnector, platform) as-is.
"""
import json, os, re, sys, time, hashlib
from urllib.parse import urljoin, urlparse, urldefrag, unquote
import requests
from bs4 import BeautifulSoup

SITE = "https://imoves.com"
HOST = "imoves.com"
OUT = os.path.join(os.path.dirname(__file__), "site")
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0 (Macintosh) imoves-mirror/1.0"

pages_done, pages_todo = {}, []
assets_done = {}
log = {"pages": {}, "assets": {}, "errors": []}

def is_same(u):
    p = urlparse(u)
    return p.netloc in ("", HOST, "www." + HOST)

def norm_page(u):
    u, _ = urldefrag(urljoin(SITE, u))
    p = urlparse(u)
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return SITE + path + (("?" + p.query) if p.query else "")

def page_file(url):
    p = urlparse(url)
    path = p.path.strip("/")
    d = os.path.join(OUT, path) if path else OUT
    return os.path.join(d, "index.html")

def asset_local(url):
    """Root-relative path for an asset, keeping the original path where possible."""
    p = urlparse(url)
    path = unquote(p.path)
    if p.query:  # cache-busters like app.css?123 -> keep file name only
        pass
    return path  # e.g. /default/dist/css/app.css

def fetch(url, binary=True):
    for attempt in range(3):
        try:
            r = S.get(url, timeout=40)
            if r.status_code == 200:
                return r
            if r.status_code in (404, 410):
                return r
        except Exception as e:
            err = str(e)
        time.sleep(1.5)
    log["errors"].append({"url": url, "error": "fetch failed"})
    return None

ASSET_EXT = re.compile(r"\.(css|js|png|jpe?g|gif|svg|webp|ico|woff2?|ttf|otf|eot|pdf|docx?|xlsx?|pptx?|mp4|mp3|json|xml|txt|webmanifest)(\?.*)?$", re.I)

def save_asset(url):
    """Download a same-origin asset once; return its root-relative path."""
    url, _ = urldefrag(urljoin(SITE, url))
    if url in assets_done:
        return assets_done[url]
    local = asset_local(url)
    dest = os.path.join(OUT, local.lstrip("/"))
    assets_done[url] = local
    if os.path.exists(dest):
        return local
    r = fetch(url)
    if r is None or r.status_code != 200:
        log["assets"][url] = r.status_code if r is not None else "fail"
        return local
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    data = r.content
    if local.lower().endswith(".css"):
        data = rewrite_css(r.text, url).encode("utf-8")
    with open(dest, "wb") as f:
        f.write(data)
    log["assets"][url] = len(data)
    return local

CSS_URL = re.compile(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)")
CSS_IMPORT = re.compile(r"@import\s+(?:url\()?['\"]?([^'\")]+)['\"]?\)?")

def rewrite_css(text, base):
    def rep(m):
        q, u = m.group(1), m.group(2).strip()
        if u.startswith(("data:", "#")):
            return m.group(0)
        absu = urljoin(base, u)
        if is_same(absu):
            return "url(%s%s%s)" % (q, save_asset(absu), q)
        return m.group(0)
    text = CSS_URL.sub(rep, text)
    def repi(m):
        absu = urljoin(base, m.group(1))
        if is_same(absu):
            return '@import url("%s")' % save_asset(absu)
        return m.group(0)
    return CSS_IMPORT.sub(repi, text)

def process_page(url):
    r = fetch(url)
    if r is None:
        return
    if r.status_code != 200:
        log["pages"][url] = r.status_code
        return
    final = norm_page(r.url)
    html = r.text
    soup = BeautifulSoup(html, "html.parser")

    # Rewrite asset references
    for tag, attr in (("link", "href"), ("script", "src"), ("img", "src"), ("img", "data-src"),
                      ("source", "src"), ("source", "srcset"), ("img", "srcset"), ("video", "poster"),
                      ("video", "src"), ("audio", "src"), ("iframe", "src"), ("meta", "content"),
                      ("a", "href"), ("input", "src"), ("use", "href"), ("use", "xlink:href")):
        for el in soup.find_all(tag):
            v = el.get(attr)
            if not v:
                continue
            if attr == "srcset":
                parts = []
                for cand in v.split(","):
                    bits = cand.strip().split()
                    if not bits:
                        continue
                    u = urljoin(final, bits[0])
                    if is_same(u) and ASSET_EXT.search(urlparse(u).path):
                        bits[0] = save_asset(u)
                    parts.append(" ".join(bits))
                el[attr] = ", ".join(parts)
                continue
            if v.startswith(("data:", "mailto:", "tel:", "javascript:", "#", "sms:")):
                continue
            u = urljoin(final, v)
            if tag == "meta":
                # download the asset but keep social-sharing images absolute (scrapers need full URLs)
                if is_same(u) and ASSET_EXT.search(urlparse(u).path):
                    local = save_asset(u)
                    if (el.get("property") or el.get("name") or "") in ("og:image", "twitter:image"):
                        el[attr] = SITE + local
                    else:
                        el[attr] = local
                continue
            if not is_same(u):
                continue
            path = urlparse(u).path
            if tag == "a" or (tag == "link" and "stylesheet" not in (el.get("rel") or []) and not ASSET_EXT.search(path)):
                if ASSET_EXT.search(path):
                    el[attr] = save_asset(u)
                else:
                    # internal page link -> root-relative clean path, queue it
                    pu = norm_page(u)
                    if pu not in pages_done and pu not in pages_todo:
                        pages_todo.append(pu)
                    pth = urlparse(pu).path
                    q = urlparse(pu).query
                    frag = urlparse(v).fragment
                    el[attr] = (pth if pth != "" else "/") + (("?" + q) if q else "") + (("#" + frag) if frag else "")
                continue
            if ASSET_EXT.search(path) or tag in ("img", "script", "source", "video", "audio", "input", "use"):
                el[attr] = save_asset(u)
            else:
                el[attr] = urlparse(u).path or "/"

    # Inline style attributes and <style> blocks with url()
    for el in soup.find_all(style=True):
        el["style"] = rewrite_css(el["style"], final)
    for st in soup.find_all("style"):
        if st.string:
            st.string = rewrite_css(st.string, final)

    # Canonical / base tags: keep canonical but strip <base>
    for b in soup.find_all("base"):
        b.decompose()

    dest = page_file(final)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(str(soup))
    log["pages"][url] = {"final": final, "file": os.path.relpath(dest, OUT), "bytes": len(html)}
    if final != url:
        log["pages"][url]["redirect"] = True

def main():
    os.makedirs(OUT, exist_ok=True)
    seeds = [SITE + "/"]
    sm = fetch(SITE + "/sitemap.xml")
    if sm is not None and sm.status_code == 200:
        seeds += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm.text)
        with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
            f.write(sm.text)
    extra = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = "--only" in sys.argv
    if only:
        seeds = []
        import glob
        for f in glob.glob(os.path.join(OUT, "**", "index.html"), recursive=True):
            rel = os.path.relpath(os.path.dirname(f), OUT)
            pages_done[SITE + ("" if rel == "." else "/" + rel)] = True
    seeds += [SITE + p for p in extra]
    for s in seeds:
        n = norm_page(s)
        if n not in pages_todo:
            pages_todo.append(n)
    i = 0
    while pages_todo:
        url = pages_todo.pop(0)
        if url in pages_done:
            continue
        pages_done[url] = True
        i += 1
        print(f"[{i}] {url}  (queue {len(pages_todo)})", flush=True)
        try:
            process_page(url)
        except Exception as e:
            log["errors"].append({"url": url, "error": repr(e)})
            print("   ERROR", repr(e), flush=True)
    with open(os.path.join(os.path.dirname(__file__), "mirror-log.json"), "w") as f:
        json.dump(log, f, indent=1)
    print("pages:", len(log["pages"]), "assets:", len(log["assets"]), "errors:", len(log["errors"]))

if __name__ == "__main__":
    main()
