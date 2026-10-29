#!/usr/bin/env python3
"""Pixel-compare live/copy screenshot pairs in a directory; append to a CSV; delete matched PNGs.
Writes a diff image for any pair above threshold."""
import glob, os, sys, csv
from PIL import Image, ImageChops
d = sys.argv[1]; out = sys.argv[2]
rows = []
for live in sorted(glob.glob(os.path.join(d, '*-live.png'))):
    copy = live.replace('-live.png', '-copy.png')
    key = os.path.basename(live)[:-9]
    if not os.path.exists(copy):
        rows.append((key, 'missing-copy', '', '')); continue
    a = Image.open(live).convert('RGB'); b = Image.open(copy).convert('RGB')
    if a.size != b.size:
        h = min(a.height, b.height)
        a2 = a.crop((0, 0, a.width, h)); b2 = b.crop((0, 0, b.width, h))
        sizenote = f'{a.size[1]}vs{b.size[1]}'
    else:
        a2, b2, sizenote = a, b, ''
    if a2.size != b2.size:
        rows.append((key, 'size', sizenote, '')); continue
    diff = ImageChops.difference(a2, b2).convert('L').point(lambda v: 255 if v > 24 else 0)
    bbox = diff.getbbox()
    n = sum(1 for v in diff.getdata() if v)
    pct = 100.0 * n / (a2.width * a2.height)
    rows.append((key, f'{pct:.3f}', sizenote, str(bbox) if bbox else ''))
    if pct > 0.02 or sizenote:
        # side-by-side with diff highlighted
        w = a2.width; out_img = Image.new('RGB', (w * 3 + 20, a2.height), 'white')
        out_img.paste(a2, (0, 0)); out_img.paste(b2, (w + 10, 0))
        red = Image.new('RGB', a2.size, (255, 0, 0)); hl = Image.composite(red, b2, diff)
        out_img.paste(hl, (2 * w + 20, 0))
        if out_img.height > 6000: out_img = out_img.crop((0, 0, out_img.width, 6000))
        out_img.save(os.path.join(d, f'DIFF-{key}.png'))
    os.remove(live); os.remove(copy)
with open(out, 'a', newline='') as f:
    csv.writer(f).writerows(rows)
for r in rows:
    if r[1] not in ('0.000',) : print(r)
