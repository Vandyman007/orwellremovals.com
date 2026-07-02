#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate sitemap.xml listing every indexable page with real lastmod (file mtime).
Excludes _source, node_modules, 404 and any noindex pages."""
import os, re, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://orwellremovals.com"

def url_for(rel):
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return SITE + "/" + rel[:-len("index.html")]
    return SITE + "/" + rel

def priority(rel):
    if rel == "index.html": return "1.0"
    if rel in ("services/index.html", "locations/index.html"): return "0.9"
    if rel.startswith("services/") or rel.startswith("locations/"): return "0.8"
    if rel in ("about-us/index.html", "pricing/index.html", "get-a-quote/index.html", "contact-us/index.html"): return "0.7"
    return "0.6"

def main():
    urls = []
    for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(p, ROOT)
        if rel.startswith(("_source/", "node_modules/", "tools/", "data/", "_image-review/",
                           "_photo-library/", "image-check/", "videos/")) or rel == "404.html":
            continue
        h = open(p, encoding="utf-8").read()
        if re.search(r'name="robots"\s+content="noindex', h):
            continue
        lastmod = datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()
        urls.append((url_for(rel), lastmod, priority(rel)))
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, lm, pr in urls:
        out.append(f"  <url><loc>{u}</loc><lastmod>{lm}</lastmod><changefreq>monthly</changefreq><priority>{pr}</priority></url>")
    out.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"sitemap.xml: {len(urls)} URLs")

if __name__ == "__main__":
    main()
