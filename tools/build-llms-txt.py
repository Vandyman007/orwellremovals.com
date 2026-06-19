#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate /llms.txt — a structured map of the Orwell Removals & Storage site for LLMs / AI search.
Pulls page lists from data/siteconfig.py and the blog plan; no fabricated trust signals
(NOT a BAR member, no third-party review widgets, "fully covered" not "fully insured")."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data"))
import siteconfig as S
try:
    import blog_plan as BP
except Exception:
    BP = None

SITE = S.SITE_URL
B = S.BUSINESS

def main():
    lines = []
    lines.append("# Orwell Removals & Storage")
    lines.append("")
    lines.append(
        f"> Family-run removals and storage company based at {B['street']}, {B['locality']}, "
        f"{B['region']} {B['postcode']} (moving goods since {B['founded']}). Home, office, "
        "commercial, long-distance and piano removals, professional packing and secure "
        "container storage across Ipswich and the whole of Suffolk. Fully covered, Euro 6 fleet, "
        f"free no-obligation surveys. Tel {B['phone']} / {B['email']}.")
    lines.append("")

    lines.append("## Key pages")
    for label, path in [("Home", "/"), ("About Us", "/about-us/"), ("Services", "/services/"),
                        ("Pricing", "/pricing/"), ("Areas We Cover", "/locations/"),
                        ("FAQs", "/frequently-asked-questions/"), ("Blog", "/blog/"),
                        ("Gallery", "/gallery/"), ("Reviews", "/reviews/"),
                        ("Get a Quote", "/get-a-quote/"), ("Contact", "/contact-us/")]:
        lines.append(f"- [{label}]({SITE}{path})")
    lines.append("")

    lines.append("## Services")
    for path, label in S.SERVICES + S.STORAGE[1:]:
        lines.append(f"- [{label}]({SITE}/{path})")
    lines.append("")

    lines.append("## Areas we cover")
    for path, name in S.COUNTY_HUBS:
        lines.append(f"- [{name} removals]({SITE}/{path})")
    for path, name in S.load_locations():
        lines.append(f"- [{name} removals]({SITE}/{path})")
    lines.append("")

    # Blog — list rendered posts only (read from the audit's slug manifest)
    slugfile = os.path.join(ROOT, "data", "blog_slugs.txt")
    if BP and os.path.exists(slugfile):
        rendered = set(l.strip().split("/", 1)[1] for l in open(slugfile, encoding="utf-8") if l.strip())
        posts = [b for b in BP.BLOGS if b["slug"] in rendered]
        if posts:
            lines.append("## Blog")
            for b in posts:
                lines.append(f"- [{b['title']}]({SITE}/blog/{b['slug']}/)")
            lines.append("")

    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines).rstrip() + "\n")
    print(f"llms.txt: {len(lines)} lines")

if __name__ == "__main__":
    main()
