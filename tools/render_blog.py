# -*- coding: utf-8 -*-
"""Blog for Orwell Removals & Storage.
Renders /blog/<slug>/ posts from data/blog/<slug>.json (body content) + data/blog_plan.py
(title, category, parent). Each post: >=1300 words, H1 = post title, every H2's beside-image
matched to that H2's topic (media_rows + match_photo), 4 FAQs, BlogPosting + FAQPage +
Breadcrumb schema, related posts (same category). Writes data/blog_slugs.txt for the audit.
"""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
from engine import esc, icon, img, section, prose, card_grid, cta_band, faq_block
import blog_plan as BP

ROOT = E.S.ROOT
BLOGDIR = os.path.join(ROOT, "data", "blog")

def _mp(text, seed="", used=()):
    """Topic-matched photo, varied per page via `seed` salt, with a deterministic fallback."""
    return E.match_photo(text, used=used, salt=seed) or E.page_photos(seed or text, 1)[0]

# deterministic publish dates (newest first by plan order) — datetime is fine here (not a workflow)
def _dates():
    from datetime import date, timedelta
    base = date(2026, 6, 12)
    out = {}
    for i, b in enumerate(BP.BLOGS):
        out[b["slug"]] = (base - timedelta(days=i * 3)).isoformat()
    return out
DATES = _dates()

def _rendered_slugs():
    return set(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(BLOGDIR, "*.json")))

def _hero(title, kicker, photo):
    return E.hero(title, "", photo, kicker=kicker, cta=True)

def _related(slug, category, rendered):
    cards = []
    for b in BP.BLOGS:
        if b["slug"] == slug or b["category"] != category or b["slug"] not in rendered:
            continue
        photo = _mp(b["title"] + " " + b.get("kw", ""), b["slug"])
        cards.append((b["title"], "/blog/" + b["slug"] + "/",
                      '<p><span class="text-blue font-semibold text-sm uppercase">' + esc(b["category"]) + '</span></p>', photo))
        if len(cards) >= 3:
            break
    if not cards:
        return ""
    return card_grid(cards, cols=len(cards) if len(cards) in (2, 3) else 3,
                     heading="Related Articles", bg="bg-lightgrey", reveal=True,
                     intro="More moving tips and guides from our Suffolk team.")

def blog_post(slug, content, rendered):
    spec = BP.BY_SLUG[slug]
    title, category, parent = spec["title"], spec["category"], spec["parent"]
    hero_photo = _mp(title + " " + spec.get("kw", ""), slug)
    body_inner = "".join(f'<h2>{esc(s["h"])}</h2>{s["body"]}' for s in content["sections"])
    date = DATES.get(slug, "2026-06-01")
    body = "\n".join([
        _hero(title, category, hero_photo),
        section(prose(f'<p class="text-darkgrey text-sm uppercase tracking-wide font-semibold mb-2">{esc(category)} &middot; '
                      f'Orwell Removals &amp; Storage</p><div class="text-lg xl:text-xl font-medium text-black">{content["lead"]}</div>'),
                bg="bg-white"),
        E.media_rows(body_inner, seed=slug, bg="bg-beige", topic=title + " " + spec.get("kw", "")),
        E.trusted_by("bg-white"),
        _related(slug, category, rendered),
    ])
    faq_html, faq_schema = faq_block(content["faqs"], heading="Related Questions", bg="bg-lightgrey")
    body += "\n" + faq_html
    body += "\n" + cta_band("Planning a Move in Suffolk?",
                            "Let our friendly, family-run team take the strain. Call 01473 411531 or request a free, no-obligation quote.",
                            "Get a Free Quote", "/get-a-quote/", bg="bg-white")
    plain = E._strip_tags(content["lead"])
    desc = (plain[:152].rsplit(" ", 1)[0] + "…") if len(plain) > 153 else plain
    url = E.S.SITE_URL + "/blog/" + slug + "/"
    blogposting = {
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": E._html.unescape(E._strip_tags(title))[:110],
        "description": E._html.unescape(desc),
        "image": E.abs_url("images/photos/" + hero_photo[0] + ".webp"),
        "datePublished": date, "dateModified": date,
        "author": {"@type": "Organization", "name": E.S.BUSINESS["name"], "url": E.S.SITE_URL},
        "publisher": {"@type": "Organization", "name": E.S.BUSINESS["name"],
                      "logo": {"@type": "ImageObject", "url": E.abs_url("images/brand/orwell-removals-logo.png")}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    doc = E.render_page(
        title=(E._html.unescape(E._strip_tags(title))[:53] + " | Orwell"),
        description=desc, canonical_path="/blog/" + slug + "/", body=body,
        og_image="images/photos/" + hero_photo[0] + ".webp",
        breadcrumb=[("Home", "/"), ("Blog", "/blog/"), (E._strip_tags(title), "/blog/" + slug + "/")],
        extra_schema=[blogposting, faq_schema], active="blog")
    return E.write("blog/" + slug + "/index.html", doc)

_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def _fmt_date(slug):
    iso = DATES.get(slug, "")
    if not iso:
        return ""
    y, m, d = iso.split("-")
    return f"{int(d)} {_MONTHS[int(m) - 1]} {y}"

def _excerpt(slug, n=150):
    try:
        d = json.load(open(os.path.join(BLOGDIR, slug + ".json"), encoding="utf-8"))
        t = E._html.unescape(E._strip_tags(d.get("lead", "")))
    except Exception:
        t = ""
    if len(t) > n:
        t = t[:n].rsplit(" ", 1)[0] + "…"
    return esc(t)

def _zoom_img(photo, eager=False):
    return img("images/photos/" + photo[0] + ".webp", photo[1],
               cls="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105", eager=eager)

def _mag_feature(b, used):
    photo = _mp(b["title"] + " " + b.get("kw", ""), b["slug"], used=tuple(used)); used.append(photo[0])
    return (f'<a class="mag-feature group" href="/blog/{b["slug"]}/" aria-label="{esc(b["title"])}">'
            f'<div class="absolute inset-0">{_zoom_img(photo, eager=True)}</div>'
            f'<div class="mag-feature-body">'
            f'<span class="mag-cat">{esc(b["category"])}</span>'
            f'<h2 class="mag-feature-title">{esc(b["title"])}</h2>'
            f'<p class="mag-feature-ex">{_excerpt(b["slug"], 165)}</p>'
            f'<span class="mag-meta mag-meta--light">{_fmt_date(b["slug"])}</span></a>')

def _mag_sec(b, used):
    photo = _mp(b["title"] + " " + b.get("kw", ""), b["slug"], used=tuple(used)); used.append(photo[0])
    return (f'<a class="mag-sec group" href="/blog/{b["slug"]}/" aria-label="{esc(b["title"])}">'
            f'<span class="mag-sec-thumb"><span class="absolute inset-0">{_zoom_img(photo)}</span></span>'
            f'<span class="mag-sec-body"><span class="mag-cat mag-cat--sm">{esc(b["category"])}</span>'
            f'<span class="mag-sec-title">{esc(b["title"])}</span>'
            f'<span class="mag-meta mt-1">{_fmt_date(b["slug"])}</span></span></a>')

def _mag_card(b, used, i):
    photo = _mp(b["title"] + " " + b.get("kw", ""), b["slug"], used=tuple(used)); used.append(photo[0])
    return (f'<div class="col-span-12 sm:col-span-6 lg:col-span-4 reveal-lr" style="transition-delay:{(i % 3) * 90}ms">'
            f'<a class="mag-card group" href="/blog/{b["slug"]}/" aria-label="{esc(b["title"])}">'
            f'<span class="mag-card-thumb"><span class="absolute inset-0">{_zoom_img(photo)}</span>'
            f'<span class="mag-cat">{esc(b["category"])}</span></span>'
            f'<span class="mag-card-body"><span class="mag-card-title">{esc(b["title"])}</span>'
            f'<span class="mag-card-ex">{_excerpt(b["slug"], 130)}</span>'
            f'<span class="mag-card-foot"><span class="mag-meta">{_fmt_date(b["slug"])}</span>'
            f'<span class="mag-card-go">Read article {icon("chevron","h-3.5 w-3.5 -rotate-90 fill-current")}</span>'
            f'</span></span></a></div>')

def blog_index(rendered):
    posts = [b for b in BP.BLOGS if b["slug"] in rendered]
    posts.sort(key=lambda b: DATES.get(b["slug"], ""), reverse=True)
    used = []
    # distinct category chips (magazine-style topic row)
    chips, seen = [], set()
    for b in posts:
        if b["category"] not in seen:
            seen.add(b["category"]); chips.append(b["category"])
    chip_row = ('<div class="mag-chips">' + "".join(f'<span class="mag-chip">{esc(c)}</span>' for c in chips)
                + '</div>') if chips else ""

    grid_cards = "".join(_mag_card(b, used, i) for i, b in enumerate(posts))
    grid_block = section(
        '<div class="text-center max-w-3xl mx-auto mb-2">'
        '<h2 class="relative leading-tight text-black">Latest Moving Advice &amp; Suffolk Guides</h2>'
        '<p class="text-lg mt-2">Step-by-step moving guides, <a href="/services/packing-service/">packing</a> tips, '
        '<a href="/services/storage/">storage</a> advice and local guides to towns across '
        '<a href="/locations/suffolk-removals/">Suffolk</a> &mdash; and when you&rsquo;re ready, '
        '<a href="/get-a-quote/">get a free quote</a>.</p></div>'
        + chip_row
        + (f'<div class="grid grid-cols-12 gap-6 lg:gap-8">{grid_cards}</div>' if grid_cards else ""),
        bg="bg-lightgrey")

    body = "\n".join([
        E.hero("The Orwell Removals &amp; Storage Blog",
               "Practical moving advice, packing and storage tips, and local guides to moving around Ipswich and Suffolk.",
               E.resolve_photo("orwell-van-packing-moving-storage"), kicker="Moving tips &amp; local guides", cta=True),
        grid_block,
        cta_band("Ready to Plan Your Move?",
                 "Tell us what you&rsquo;re moving and we&rsquo;ll give you a clear, no-obligation quote.",
                 "Get a Free Quote", "/get-a-quote/", bg="bg-white"),
    ])
    doc = E.render_page(
        title="Moving Tips & Suffolk Guides | Orwell Removals Blog",
        description="Practical moving and packing advice, storage tips and local guides to moving around Ipswich and Suffolk, from family-run Orwell Removals & Storage.",
        canonical_path="/blog/", body=body,
        og_image="images/photos/orwell-van-packing-moving-storage.webp",
        breadcrumb=[("Home", "/"), ("Blog", "/blog/")], active="blog")
    return E.write("blog/index.html", doc)

def build():
    rendered = _rendered_slugs()
    # write blog_slugs.txt for the audit word-count rule
    with open(os.path.join(ROOT, "data", "blog_slugs.txt"), "w", encoding="utf-8") as f:
        for s in sorted(rendered):
            f.write("blog/%s\n" % s)
    n = 0
    for slug in sorted(rendered):
        if slug not in BP.BY_SLUG:
            continue
        content = json.load(open(os.path.join(BLOGDIR, slug + ".json"), encoding="utf-8"))
        blog_post(slug, content, rendered)
        n += 1
    blog_index(rendered)
    print("rendered %d blog posts + /blog/ index" % n)

if __name__ == "__main__":
    build()
