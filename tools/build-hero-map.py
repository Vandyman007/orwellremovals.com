#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate data/hero_map.py from the LIVE WordPress site (wolves-removals.co.uk).

Pipeline:
  1. Read the live page-sitemap.xml to list every page.
  2. Fetch each page and read its hero image (the eager fetchpriority img).
  3. Download each unique hero, optimise to WebP (<=200KB) into images/photos/ (+ _photo-library/),
     with descriptive, curated filenames.
  4. Build {canonical_path: (filename, alt)} for direct matches, then topic-fallback over the
     LOCAL sitemap.xml (locations -> location hero, storage -> storage hero, services -> service
     hero, everything else -> home hero).
  5. Write data/hero_map.py. engine.render_page consults it to PIN each page's hero.

Network + cwebp + sips required. On failure it leaves data/hero_map.py untouched.
Edit a single entry in data/hero_map.py to change one page's hero without re-crawling.
"""
import os, re, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PH   = os.path.join(ROOT, "images", "photos")
LIB  = os.path.join(ROOT, "_photo-library")
SITE = "https://wolves-removals.co.uk"
TMP  = os.path.join(os.path.expanduser("~"), ".wtmp-heromap")

# Curated names for cryptic/hashed WordPress filenames + the shared template heroes.
CURATED = {
    'a1cd759503ecc7161f1d504ff232fa0d.jpg': ('wolves-removals-sussex-location-hero', 'Wolves Removals carrying out a house removal in Sussex'),
    'IMG_5020.jpg': ('wolves-removals-service-van-hero', 'A Wolves Removals van ready for a Sussex removal service'),
    '0ef874a3-3e71-40a6-8936-da49bf76c15a.jpg': ('wolves-removals-storage-warehouse-hero', 'Inside the Wolves Removals secure storage warehouse'),
    'about-us.jpg': ('wolves-removals-van-fleet-hero', 'The Wolves Removals van fleet in Sussex'),
    'wolves-removals.jpg': ('wolves-removals-sussex-house-hero', 'Wolves Removals vans at a large Sussex house'),
    '8BEC8F97-3CDC-47FE-B386-971ED8582517-copy2-1.png': ('wolves-fine-art-statue-hero', 'An antique statue handled by the Wolves Removals fine-art team'),
    'bb5da1aa-db4e-428e-8b92-1f44c1bdf17d.jpg': ('wolves-removals-team-hero', 'The Wolves Removals team'),
    'IMG_5056.jpg': ('wolves-removals-country-lane-hero', 'A Wolves Removals van on a Sussex country lane'),
    'services.jpg': ('wolves-removals-services-hero', 'Wolves Removals services across Sussex'),
    'IMG_5022.jpg': ('non-fragile-packing-hero', 'Wolves Removals non-fragile packing service'),
    'IMG_5026.jpg': ('wolves-removals-faqs-hero', 'Wolves Removals frequently asked questions'),
    'IMG_5031.jpg': ('student-removals-hero', 'Wolves Removals student removals service'),
    'IMG_5039.jpg': ('full-unpacking-service-hero', 'Wolves Removals full unpacking service'),
    'IMG_5041.jpg': ('house-clearance-hero', 'Wolves Removals house clearance service'),
    'IMG_5052.jpg': ('full-packing-service-hero', 'Wolves Removals full packing service'),
    'IMG_5108.jpg': ('export-packing-service-hero', 'Wolves Removals export packing service'),
    'xIMG_5031.png.pagespeed.ic_.j4r7y6ww-s-600x400.jpg': ('move-to-west-sussex-hero', 'Moving to West Sussex with Wolves Removals'),
    'Choosing-a-removal-company-featured-image.jpg': ('choosing-removal-company-hero', 'Choosing a removal company with Wolves Removals'),
    'hero_billingshurst-1024x576.jpg': ('billingshurst-removals-hero', 'Wolves Removals in Billingshurst'),
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 hero-map"})
    return urllib.request.urlopen(req, timeout=30).read()


def ttl(s):  return re.sub(r'-+', ' ', s).strip().title()
def bn(u):   return u.split("?")[0].split("/")[-1] if u else ""
def slugify(name):
    n = name.rsplit('.', 1)[0]
    n = re.sub(r'\.pagespeed.*', '', n); n = re.sub(r'-?\d+x\d+$', '', n); n = re.sub(r'^x', '', n)
    return re.sub(r'[^A-Za-z0-9]+', '-', n).strip('-').lower()


def dims(p):
    o = subprocess.check_output(["/usr/bin/sips", "-g", "pixelWidth", "-g", "pixelHeight", p],
                                text=True, stderr=subprocess.DEVNULL)
    return int(re.search(r"pixelWidth: (\d+)", o)[1]), int(re.search(r"pixelHeight: (\d+)", o)[1])


def to_webp(src, slug):
    dst = os.path.join(PH, slug + ".webp"); w, _ = dims(src); ok = False
    for maxw in (1600, 1400, 1200, 1024):
        rs = ["-resize", str(maxw), "0"] if w > maxw else []
        for q in (84, 76, 68, 60, 52, 44, 38, 32):
            subprocess.run(["cwebp", "-quiet", "-m", "6", "-q", str(q)] + rs + [src, "-o", dst],
                           stderr=subprocess.DEVNULL)
            if os.path.getsize(dst) <= 204800:
                ok = True; break
        if ok or not rs:
            break
    subprocess.run(["cp", dst, os.path.join(LIB, slug + ".webp")])


def town_alt(path):
    m = re.match(r'/locations/([a-z0-9-]+)-removals/?$', path)
    return ('Wolves Removals carrying out a removal in ' + ttl(m.group(1))) if m else None


def main():
    os.makedirs(TMP, exist_ok=True)
    try:
        sm = get(SITE + "/page-sitemap.xml").decode("utf-8", "ignore")
    except Exception as e:
        print("Could not reach the live site (%s) — left data/hero_map.py untouched." % e); return
    urls = re.findall(r'<loc>([^<]+)</loc>', sm)
    pairs = []   # (canonical_path, hero_url)
    for u in urls:
        path = u.replace(SITE, "") or "/"
        try:
            html = get(u).decode("utf-8", "ignore")
        except Exception:
            continue
        tag = re.search(r'<img\b[^>]*fetchpriority[^>]*>', html)
        src = re.search(r'src="([^"]+)"', tag.group(0)) if tag else None
        pairs.append((path, src.group(1) if src else ""))
    if not pairs:
        print("No pages crawled — left data/hero_map.py untouched."); return

    # slug + alt per unique hero basename
    b2slug, b2alt = {}, {}
    for b in set(bn(u) for _, u in pairs if u):
        if b in CURATED:
            b2slug[b], b2alt[b] = CURATED[b]
        else:
            sl = slugify(b); sl = sl if sl.endswith('hero') else sl + '-hero'
            b2slug[b] = sl; b2alt[b] = 'Wolves Removals ' + ttl(slugify(b)) + ' in Sussex'

    # download every unique hero once, then optimise to WebP
    conv = 0
    seen = set()
    for path, u in pairs:
        b = bn(u)
        if not b or b in seen:
            continue
        seen.add(b)
        src = os.path.join(TMP, b)
        if not os.path.exists(src):
            try:
                full = u if u.startswith("http") else SITE + "/" + u.lstrip("/")
                open(src, "wb").write(get(full))
            except Exception:
                continue
        to_webp(src, b2slug[b]); conv += 1

    # direct matches
    hero = {}
    for path, u in pairs:
        b = bn(u)
        if b and b in b2slug:
            hero[path] = (b2slug[b], town_alt(path) or b2alt[b])
    direct = len(hero)

    # topic fallback over the LOCAL sitemap
    loc = b2slug.get('a1cd759503ecc7161f1d504ff232fa0d.jpg')
    svc = b2slug.get('IMG_5020.jpg')
    sto = b2slug.get('0ef874a3-3e71-40a6-8936-da49bf76c15a.jpg')
    home = b2slug.get('wolves-removals.jpg')
    local_sm = open(os.path.join(ROOT, "sitemap.xml")).read()
    fb = 0
    for p in set(re.findall(r'<loc>https://wolves-removals\.co\.uk([^<]*)</loc>', local_sm)):
        if p in hero:
            continue
        if p.startswith('/locations/'):
            hero[p] = (loc, town_alt(p) or 'Wolves Removals in Sussex')
        elif p.startswith('/services/storage'):
            hero[p] = (sto, 'Wolves Removals secure storage')
        elif p.startswith('/services/'):
            hero[p] = (svc, 'A Wolves Removals removal service in Sussex')
        else:
            hero[p] = (home, 'Wolves Removals — Sussex removals and storage')
        fb += 1

    with open(os.path.join(ROOT, "data", "hero_map.py"), "w", encoding="utf-8") as f:
        f.write("# Auto-generated by tools/build-hero-map.py from the live WordPress wolves-removals.co.uk heroes.\n")
        f.write("# key = canonical path, value = (image filename without ext, alt). Used by engine.render_page.\n")
        f.write("OLD_HEROES = {\n")
        for k in sorted(hero):
            n, a = hero[k]; a = a.replace('\\', '\\\\').replace('"', '\\"')
            f.write(f'    "{k}": ("{n}", "{a}"),\n')
        f.write("}\n")
    print(f"Wrote data/hero_map.py: {conv} images, {direct} direct WP matches, {fb} topic-fallback, {len(hero)} total.")


if __name__ == "__main__":
    main()
