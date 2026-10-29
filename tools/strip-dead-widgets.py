#!/usr/bin/env python3
"""v0.3: remove the dead JustReview and Paddle integrations from every page.

- JustReview: stylesheet, script, the DOMContentLoaded init block, and on pages
  that carry the reviews block, the whole <div ... data-block="main-content"> row
  whose only content is the 'Our latest reviews' heading (the widget rendered an
  'expired subscription' notice there on the live site).
- Paddle: paddle.js script and the Paddle.Setup inline script. Any leftover
  'paddle_button' anchors are left in place but reported.
"""
import glob, os, re, sys
from bs4 import BeautifulSoup

ROOT = sys.argv[1]
changed = 0; blocks = 0; paddle_buttons = []
for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
    html = open(f, encoding="utf-8").read()
    if "justreview" not in html and "paddle" not in html.lower():
        continue
    soup = BeautifulSoup(html, "html.parser")
    touched = False
    for el in soup.find_all(["link", "script"]):
        src = (el.get("href") or el.get("src") or "")
        if "justreview.co" in src or "cdn.paddle.com" in src:
            el.decompose(); touched = True
    for sc in soup.find_all("script"):
        txt = sc.string or sc.get_text() or ""
        if "JustReview.initTestimonials" in txt or "Paddle.Setup" in txt:
            sc.decompose(); touched = True
    h = soup.find(id="justreview-testimonials")
    if h is not None:
        row = h.find_parent(attrs={"data-block": "main-content"})
        target = row if row is not None and len(row.get_text(strip=True)) <= len(h.get_text(strip=True)) + 2 else h
        target.decompose(); touched = True; blocks += 1
    for a in soup.select("a.paddle_button"):
        paddle_buttons.append(os.path.relpath(f, ROOT))
    if touched:
        open(f, "w", encoding="utf-8").write(str(soup)); changed += 1
print("files changed:", changed, "review blocks removed:", blocks)
print("paddle buttons left (dead links):", sorted(set(paddle_buttons)))
