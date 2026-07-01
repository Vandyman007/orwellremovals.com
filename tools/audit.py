#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Orwell Removals & Storage SEO audit — enforces the SEO "bible" against the built site.
Configured for orwellremovals.com. Run from project root: python3 tools/audit.py
Exit code 0 = all hard rules pass; 1 = failures. Warnings don't fail the build.
"""
import os, re, sys, html as _html, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://orwellremovals.com"

# ---- page classification -------------------------------------------------
EXEMPT_WORDS = {  # transactional / legal / utility — no word-count floor
    "contact-us/index.html", "get-a-quote/index.html", "reviews/index.html",
    "gallery/index.html", "privacy-policy/index.html", "terms-conditions/index.html",
    "404.html",
}
# Banned phrases (user content rules): never claim "fully insured" — always "fully covered";
# this is NOT a BAR member; no third-party review/rating widgets.
BANNED_TOKENS = ["fully insured"]
NOINDEX_OK = {"404.html", "home/index.html", "contact/index.html", "quote/index.html",
              "thank-you/index.html"}
# The blog index lists every article with its own hero image; with 58 posts and a
# 44-photo pool, repeats are unavoidable on this listing — exempt it from R9 only.
R9_EXEMPT = {"blog/index.html", "gallery/index.html"}
GENERIC_ANCHORS = {"click here", "read more", "learn more", "here", "more", "read article", "book", "find out more"}

def page_url(rel):
    if rel == "index.html":
        return "/"
    if rel == "404.html":
        return "/404.html"
    return "/" + rel[:-len("index.html")] if rel.endswith("/index.html") else "/" + rel

HUBS = {"locations/index.html", "services/index.html", "helpful-tips/index.html", "blog/index.html"}

def _blog_slugs():
    f = os.path.join(ROOT, "data", "blog_slugs.txt")
    return set(l.strip() for l in open(f, encoding="utf-8")) if os.path.exists(f) else set()
BLOG_SLUGS = _blog_slugs()

def word_min(rel):
    # navigational hubs: shorter by design
    if rel in HUBS:
        return 700
    # blog posts under /blog/<slug>/ — long-form (master SEO rules: 1300–1500)
    if rel.endswith("/index.html") and rel[:-len("/index.html")] in BLOG_SLUGS:
        return 1300
    # location town + county pages
    if rel.startswith("locations/"):
        return 1500
    # focused how-to / advice articles
    if rel.startswith("helpful-tips/"):
        return 800
    # service pages
    if rel.startswith("services/"):
        return 1000
    # pillar content pages
    if rel in ("about-us/index.html", "pricing/index.html"):
        return 1200
    # FAQ page (Q&A-dense)
    if rel == "frequently-asked-questions/index.html":
        return 1100
    # home
    if rel == "index.html":
        return 1000
    return 0

def text_of(h):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", h, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", _html.unescape(t)).strip()

# ---- collect pages -------------------------------------------------------
def all_pages():
    out = []
    for p in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        rel = os.path.relpath(p, ROOT)
        if rel.startswith(("_source/", "node_modules/", "tools/", "data/", "image-check/", "_image-review/", "_photo-library/", "videos/")):
            continue
        out.append(rel)
    return sorted(out)

def link_target_exists(href):
    """Return True if an internal link resolves to a real file."""
    href = href.split("#")[0].split("?")[0]
    if not href or href.startswith(("http://", "https://", "tel:", "mailto:", "javascript:", "data:")):
        return True  # external / non-file handled elsewhere
    if not href.startswith("/"):
        return True  # relative anchors rare here; skip
    # assets
    if re.search(r"\.(pdf|xml|txt|png|jpe?g|webp|svg|ico|css|js|woff2?|webmanifest|gif)$", href, re.I):
        return os.path.exists(os.path.join(ROOT, href.lstrip("/")))
    if href.endswith("/"):
        return os.path.exists(os.path.join(ROOT, href.strip("/"), "index.html"))
    if href == "/":
        return os.path.exists(os.path.join(ROOT, "index.html"))
    # bare path without slash -> try dir/index.html or .html
    base = href.strip("/")
    return (os.path.exists(os.path.join(ROOT, base, "index.html"))
            or os.path.exists(os.path.join(ROOT, base + ".html")))

# ---- run -----------------------------------------------------------------
def run():
    pages = all_pages()
    fails, warns = [], []
    titles, h1s, descs = {}, {}, {}
    pending_links = {}
    img_srcs = set()

    def fail(rule, rel, msg):
        fails.append((rule, rel, msg))
    def warn(rule, rel, msg):
        warns.append((rule, rel, msg))

    for rel in pages:
        h = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        img_srcs.update(re.findall(r'<img\b[^>]*\bsrc="(/images/[^"]+)"', h))
        url = page_url(rel)
        body_text = text_of(h)
        wc = len(body_text.split())

        # R1 head essentials
        if "<meta charset" not in h.lower(): fail("R1-charset", rel, "no charset")
        if "viewport" not in h: fail("R1-viewport", rel, "no viewport")
        if not re.search(r'<html[^>]+lang=', h): fail("R1-lang", rel, "no lang attribute")

        # R2 title
        mt = re.search(r"<title>(.*?)</title>", h, re.S)
        if not mt or not mt.group(1).strip():
            fail("R2-title", rel, "missing title")
        else:
            t = mt.group(1).strip()
            if len(t) > 65: warn("R2-title-len", rel, f"{len(t)} chars (>65)")
            titles.setdefault(t, []).append(rel)

        # R3 meta description
        md = re.search(r'name="description"\s+content="(.*?)"', h, re.S)
        if not md:
            fail("R3-desc", rel, "missing meta description")
        else:
            d = _html.unescape(md.group(1)).strip()
            if len(d) > 145: fail("R3-desc-len", rel, f"{len(d)} chars (>145)")
            descs.setdefault(d, []).append(rel)

        # R4 single, unique H1
        hh = re.findall(r"<h1\b[^>]*>(.*?)</h1>", h, re.S | re.I)
        if len(hh) != 1:
            fail("R4-h1-count", rel, f"{len(hh)} H1s")
        else:
            h1t = re.sub(r"<[^>]+>", "", hh[0]).strip()
            h1s.setdefault(h1t, []).append(rel)

        # R5 canonical
        mc = re.search(r'<link rel="canonical" href="([^"]+)"', h)
        if not mc:
            fail("R5-canonical", rel, "missing canonical")
        else:
            want = SITE + (url if url.startswith("/") else "/" + url)
            if rel == "404.html":
                pass
            elif mc.group(1).rstrip("/") != want.rstrip("/"):
                fail("R5-canonical-self", rel, f"{mc.group(1)} != {want}")

        # R6 OG/twitter
        for need in ('property="og:title"', 'property="og:description"', 'property="og:image"', 'name="twitter:card"'):
            if need not in h: fail("R6-og", rel, f"missing {need}")
        mog = re.search(r'property="og:image" content="([^"]+)"', h)
        if mog and not mog.group(1).startswith(SITE):
            fail("R6-og-image", rel, "og:image not absolute on-domain")

        # R7 schema
        if "application/ld+json" not in h: fail("R7-schema", rel, "no JSON-LD")
        elif "MovingCompany" not in h and "LocalBusiness" not in h: fail("R7-localbiz", rel, "no LocalBusiness/MovingCompany")

        # R8 images alt + dims
        for im in re.findall(r"<img\b[^>]*>", h, re.I):
            decorative = ('role="presentation"' in im) or ('aria-hidden="true"' in im)
            am = re.search(r'\balt="([^"]*)"', im)
            if am is None and not decorative:
                fail("R8-alt", rel, f"img missing alt: {im[:70]}")
            elif am and len(am.group(1)) > 100:
                warn("R8-alt-len", rel, f"alt {len(am.group(1))} chars")
            if not re.search(r"\bwidth=", im) or not re.search(r"\bheight=", im):
                warn("R8-dims", rel, f"img missing width/height: {im[:60]}")

        # R9 no duplicate content photo on a page (RULE) — brand logos may repeat;
        # the hero rubik mosaic (data-tile) is one image sliced 9× and is exempt.
        photo_srcs = []
        for _tag in re.findall(r'<img\b[^>]*>', h, re.I):
            if "data-tile" in _tag:
                continue
            _m = re.search(r'\bsrc="([^"]+)"', _tag)
            if _m and "/images/photos/" in _m.group(1):
                photo_srcs.append(_m.group(1))
        dup = {s for s in photo_srcs if photo_srcs.count(s) > 1}
        if dup and rel not in R9_EXEMPT: fail("R9-dup-img", rel, f"{len(dup)} duplicate photo(s) e.g. {sorted(dup)[0]}")

        # R10 broken internal links + R11 no index.html / mixed content
        for href in re.findall(r'href="([^"]+)"', h):
            if href.startswith("http://"):
                fail("R11-mixed", rel, f"http:// link {href}")
            if "index.html" in href and not href.endswith(".html") is False:
                pass
            if re.search(r"/index\.html(\b|$)", href):
                fail("R11-indexhtml", rel, f"links to index.html: {href}")
            if not link_target_exists(href):
                pending_links.setdefault(href, []).append(rel)

        # R12 word count
        wmin = word_min(rel)
        if rel not in EXEMPT_WORDS and wmin and wc < wmin:
            fail("R12-words", rel, f"{wc} words (<{wmin})")

        # R13 FAQ on content pages (warn only for non-location/blog)
        if wmin and rel not in EXEMPT_WORDS and "FAQPage" not in h:
            (fail if rel.startswith("locations/") else warn)("R13-faq", rel, "no FAQPage schema")

        # R13b banned phrases (content rules): "fully insured" → must be "fully covered"
        _lt = body_text.lower()
        for _bad in BANNED_TOKENS:
            if _bad in _lt:
                fail("R13b-banned", rel, f'banned phrase "{_bad}" (use "fully covered")')

        # R14 clickable phone/email
        if re.search(r"01473\s?411531", body_text) and 'tel:+441473411531' not in h:
            warn("R14-tel", rel, "phone shown but no tel: link")

        # R15 descriptive link text (incl. cards). Accessible name = aria-label if present,
        # else visible text. Every link must have a non-generic, non-empty accessible name.
        for m in re.finditer(r"<a\b([^>]*)>(.*?)</a>", h, re.S | re.I):
            attrs, inner = m.group(1), m.group(2)
            al = re.search(r'aria-label="([^"]*)"', attrs)
            if al is not None:
                name = al.group(1)
            else:
                # an <img alt="..."> inside the link contributes to its accessible name
                with_alt = re.sub(r'<img\b[^>]*\balt="([^"]*)"[^>]*>', r" \1 ", inner, flags=re.I)
                name = re.sub(r"<[^>]+>", "", with_alt)
            name = re.sub(r"\s+", " ", _html.unescape(name)).strip().lower()
            if not name:
                if 'aria-hidden="true"' not in inner and "aria-label" not in attrs:
                    fail("R15-anchor-empty", rel, f"link with no accessible name: {m.group(0)[:70]}")
            elif name in GENERIC_ANCHORS:
                fail("R15-anchor-generic", rel, f"generic link text: '{name}'")

        # R17 robots noindex only on 404
        if 'content="noindex' in h and rel not in NOINDEX_OK:
            fail("R17-noindex", rel, "unexpected noindex")

    # cross-page uniqueness
    for t, fs in titles.items():
        if len(fs) > 1: fail("R2-title-unique", fs[1], f"duplicate title '{t[:40]}' ({len(fs)} pages)")
    for t, fs in h1s.items():
        if len(fs) > 1: fail("R4-h1-unique", fs[1], f"duplicate H1 '{t[:40]}' ({len(fs)} pages)")
    for d, fs in descs.items():
        if len(fs) > 1: fail("R3-desc-unique", fs[1], f"duplicate description ({len(fs)} pages)")

    # R16 image weight (<=200KB) + R19 descriptive filenames (no IMG_/numeric; content photos 50-70 chars)
    for src in sorted(img_srcs):
        path = os.path.join(ROOT, src.lstrip("/"))
        base = os.path.basename(src)
        stem = re.sub(r"\.[a-z0-9]+$", "", base, flags=re.I)
        if os.path.exists(path):
            kb = os.path.getsize(path) / 1024
            if kb > 200:
                fail("R16-img-weight", src, f"{int(kb)}KB (>200KB)")
        else:
            fail("R10-img-missing", src, "referenced image not found")
        if re.match(r"(?i)(img|dsc|image|photo|screenshot)[-_]?\d", stem) or re.fullmatch(r"\d+", stem):
            fail("R19-img-name", src, "non-descriptive image filename")
        # House style: descriptive kebab-case filenames of 3-6 words (memory: feedback-image-filenames).
        _nwords = len(stem.split("-"))
        if src.startswith("/images/photos/") and not (3 <= _nwords <= 6):
            warn("R19-img-name-len", src, f"{_nwords} words (must be 3-6 descriptive words)")

    # ---- per-page table (--by-page) ----
    if "--by-page" in sys.argv:
        from collections import defaultdict
        pageset = set(pages)
        pf = defaultdict(set); pw = defaultdict(set)
        for r, rel, m in fails:
            if rel in pageset: pf[rel].add(r)
        for r, rel, m in warns:
            if rel in pageset: pw[rel].add(r)
        npass = sum(1 for rel in pages if not pf[rel])
        print(f"PER-PAGE SEO AUDIT  —  {npass}/{len(pages)} pages PASS  (rules R1-R19)\n" + "=" * 78)
        print(f"{'PAGE (URL)':<44}{'RESULT':<9}{'ISSUES'}")
        print("-" * 78)
        for rel in pages:
            u = page_url(rel)
            status = "PASS" if not pf[rel] else "FAIL"
            issues = ""
            if pf[rel]: issues += "FAIL: " + ", ".join(sorted(pf[rel]))
            if pw[rel]: issues += ("  " if issues else "") + "warn: " + ", ".join(sorted(pw[rel]))
            mark = "OK" if status == "PASS" and not pw[rel] else ("PASS*" if status == "PASS" else "FAIL")
            print(f"{u[:43]:<44}{mark:<9}{issues}")
        print("-" * 78)
        print(f"TOTAL: {npass}/{len(pages)} pass  ·  {len(pages)-npass} fail  ·  PASS* = passes with non-blocking warning(s)\n")

    # ---- report ----
    print(f"Audited {len(pages)} pages\n" + "=" * 60)
    if pending_links:
        print(f"\nBROKEN / PENDING internal links ({len(pending_links)} targets):")
        for href, fs in sorted(pending_links.items()):
            print(f"  {href}  <- {len(fs)} page(s) e.g. {fs[0]}")
    from collections import Counter
    fc = Counter(r for r, _, _ in fails)
    wc_ = Counter(r for r, _, _ in warns)
    if fails:
        print(f"\nFAILURES ({len(fails)}):")
        for rule in sorted(fc):
            ex = [m for r, rel, m in fails if r == rule][:3]
            egp = [rel for r, rel, m in fails if r == rule][:3]
            print(f"  [{rule}] x{fc[rule]}  e.g. {egp[0]}: {ex[0]}")
    if warns:
        print(f"\nWARNINGS ({len(warns)}):")
        for rule in sorted(wc_):
            print(f"  [{rule}] x{wc_[rule]}")
            if os.environ.get("AUDIT_VERBOSE"):
                for r, rel, m in warns:
                    if r == rule:
                        print(f"      {rel}: {m}")
    print("\n" + "=" * 60)
    broken_real = {h for h in pending_links}
    if not fails and not broken_real:
        print("RESULT: PASS — all hard rules satisfied.")
        return 0
    print(f"RESULT: {len(fails)} failures, {len(broken_real)} broken-link targets, {len(warns)} warnings.")
    return 1

if __name__ == "__main__":
    sys.exit(run())
