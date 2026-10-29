#!/usr/bin/env python3
"""Make every root-relative URL in the mirrored site relative to its own file,
so the site works at any mount point (dmlaycock.github.io/imoves-website/ now,
imoves.com/ later)."""
import os, re, sys, glob

ROOT = sys.argv[1]

def prefix_for(path):
    rel = os.path.relpath(os.path.dirname(path), ROOT)
    depth = 0 if rel == "." else rel.count(os.sep) + 1
    return "../" * depth if depth else "./"

# attribute values: ="/something" but not ="//host"
ATTR = re.compile(r'((?:href|src|poster|action|content|data-src|data-href|data-background|data-image)=["\'])/(?!/)([^"\']*)(["\'])')
SRCSET = re.compile(r'(srcset=["\'])([^"\']+)(["\'])')
CSSURL = re.compile(r'(url\(\s*["\']?)/(?!/)([^"\')]*)(["\']?\s*\))')
REFRESH = re.compile(r'(content=["\']\d+;\s*url=)/(?!/)([^"\']*)')

def fix_path(prefix, rest):
    return prefix + rest if rest else prefix

def process_html(path):
    s = open(path, encoding="utf-8").read()
    p = prefix_for(path)
    def a(m):
        # leave canonical/og meta content that points to absolute URLs alone (they are http...)
        return m.group(1) + fix_path(p, m.group(2)) + m.group(3)
    s2 = ATTR.sub(a, s)
    def ss(m):
        parts = []
        for cand in m.group(2).split(","):
            bits = cand.strip().split()
            if bits and bits[0].startswith("/") and not bits[0].startswith("//"):
                bits[0] = fix_path(p, bits[0][1:])
            parts.append(" ".join(bits))
        return m.group(1) + ", ".join(parts) + m.group(3)
    s2 = SRCSET.sub(ss, s2)
    s2 = CSSURL.sub(lambda m: m.group(1) + fix_path(p, m.group(2)) + m.group(3), s2)
    s2 = REFRESH.sub(lambda m: m.group(1) + fix_path(p, m.group(2)), s2)
    if s2 != s:
        open(path, "w", encoding="utf-8").write(s2)
        return 1
    return 0

def process_css(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    p = prefix_for(path)
    s2 = CSSURL.sub(lambda m: m.group(1) + fix_path(p, m.group(2)) + m.group(3), s)
    if s2 != s:
        open(path, "w", encoding="utf-8").write(s2); return 1
    return 0

n = 0
for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
    n += process_html(f)
for f in glob.glob(os.path.join(ROOT, "**", "*.css"), recursive=True):
    n += process_css(f)
print("files changed:", n)
