# -*- coding: utf-8 -*-
"""Orwell Removals & Storage static render engine.

Renders the site chrome (header / footer / sections) using the compiled
stylesheet (css/site.min.css) + Barlow fonts + brand classes, while emitting
markup that satisfies the SEO bible
(canonical, OG/Twitter, JSON-LD LocalBusiness + Breadcrumb + FAQPage,
clickable tel/mailto, descriptive anchors, alt text, etc.).

Pure stdlib. Render scripts import from here.
"""
import json, os, sys, re, subprocess, functools, zlib, hashlib, html as _html
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
import siteconfig as S  # data/siteconfig.py
try:
    from hero_map import OLD_HEROES   # data/hero_map.py — curated hero per canonical path
except ImportError:
    OLD_HEROES = {}

def _asset_ver():
    """Cache-buster derived from the COMPILED stylesheet so `?v=` changes whenever the
    output CSS changes — including when new Tailwind utility classes are added in markup
    (a source-only hash missed those). Build CSS before HTML so this reads the fresh file."""
    for rel in ("css/site.min.css", "tools/css/site.input.css"):
        try:
            return hashlib.md5(open(os.path.join(S.ROOT, rel), "rb").read()).hexdigest()[:8]
        except Exception:
            continue
    return "23"

ASSET_VER = _asset_ver()

# ---------------------------------------------------------------- helpers
def esc(t):
    # Idempotent: unescape first so pre-existing entities (&, &mdash;, &rsquo;) aren't
    # double-encoded into visible "&amp;" / "&mdash;" text, then escape exactly once.
    return _html.escape(_html.unescape(str(t)), quote=True)

def abs_url(path):
    path = path or "/"
    if path.startswith("http"):
        return path
    return S.SITE_URL.rstrip("/") + "/" + path.lstrip("/")

def _clip(t, n):
    t = " ".join(str(t).split())
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"

# Inline SVG icons (no external sprite dependency)
ICONS = {
    "phone": '<svg viewBox="0 0 512 512" class="{c}" fill="currentColor" aria-hidden="true"><path d="M493 384l-91-91c-12-12-31-12-43 0l-45 45c-58-30-104-77-134-134l45-45c12-12 12-31 0-43l-91-91c-12-12-31-12-43 0L46 30C32 44 25 64 28 84c19 122 76 232 163 319s197 144 319 163c20 3 40-4 54-18l39-39c12-12 12-31 0-43z"/></svg>',
    "mobile": '<svg viewBox="0 0 24 24" class="{c}" fill="currentColor" aria-hidden="true"><path d="M8 2h8a3 3 0 0 1 3 3v14a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V5a3 3 0 0 1 3-3zm0 2a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1H8zm4 14.5a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/></svg>',
    "mail": '<svg viewBox="0 0 512 512" class="{c}" fill="currentColor" aria-hidden="true"><path d="M48 96c-18 0-32 14-32 32v10l240 156 240-156v-10c0-18-14-32-32-32H48zm448 79L262 332c-4 3-9 4-6 4-3 0-7-1-10-3L16 175v209c0 18 14 32 32 32h416c18 0 32-14 32-32V175z"/></svg>',
    "facebook": '<svg viewBox="0 0 320 512" class="{c}" fill="currentColor" aria-hidden="true"><path d="M279 288l14-93h-89v-60c0-26 12-50 52-50h41V6S250 0 215 0c-73 0-121 44-121 124v71H12v93h82v224h102V288z"/></svg>',
    "twitter": '<svg viewBox="0 0 512 512" class="{c}" fill="currentColor" aria-hidden="true"><path d="M389 48h70L305 224l181 240H345L235 320 108 464H38l164-188L28 48h145l99 131zm-25 374h39L156 88h-42z"/></svg>',
    "instagram": '<svg viewBox="0 0 448 512" class="{c}" fill="currentColor" aria-hidden="true"><path d="M224 141c-63 0-114 51-114 114s51 114 114 114 114-51 114-114-51-114-114-114zm0 188c-41 0-74-33-74-74s33-74 74-74 74 33 74 74-33 74-74 74zm145-194c0 15-12 27-27 27s-27-12-27-27 12-27 27-27 27 12 27 27zM224 48c66 0 74 0 100 1 24 1 37 5 46 9 12 4 20 10 28 18s14 16 18 28c4 9 8 22 9 46 1 26 1 34 1 100s0 74-1 100c-1 24-5 37-9 46-4 12-10 20-18 28s-16 14-28 18c-9 4-22 8-46 9-26 1-34 1-100 1s-74 0-100-1c-24-1-37-5-46-9-12-4-20-10-28-18s-14-16-18-28c-4-9-8-22-9-46-1-26-1-34-1-100s0-74 1-100c1-24 5-37 9-46 4-12 10-20 18-28s16-14 28-18c9-4 22-8 46-9 26-1 34-1 100-1z"/></svg>',
    "linkedin": '<svg viewBox="0 0 448 512" class="{c}" fill="currentColor" aria-hidden="true"><path d="M100 448H7V148h93v300zM53 107a54 54 0 1 1 0-108 54 54 0 0 1 0 108zm395 341h-92V302c0-35-1-79-49-79-48 0-55 38-55 77v148h-93V148h89v41h1c12-23 43-48 88-48 94 0 111 62 111 142v165z"/></svg>',
    "pinterest": '<svg viewBox="0 0 496 512" class="{c}" fill="currentColor" aria-hidden="true"><path d="M248 8C111 8 0 119 0 256c0 105 65 195 158 231-2-20-4-50 1-72 4-19 29-122 29-122s-7-15-7-37c0-35 20-61 45-61 21 0 32 16 32 35 0 21-14 53-21 83-6 25 13 45 37 45 44 0 78-47 78-114 0-60-43-101-104-101-71 0-112 53-112 108 0 21 8 44 18 57 2 2 2 4 2 6-2 8-6 24-7 28-1 4-4 5-9 3-32-15-52-62-52-100 0-80 59-155 170-155 89 0 159 64 159 149 0 89-56 161-134 161-26 0-51-14-59-30l-16 62c-6 22-21 50-32 67 24 7 49 11 76 11 137 0 248-111 248-248C496 119 385 8 248 8z"/></svg>',
    "tumblr": '<svg viewBox="0 0 320 512" class="{c}" fill="currentColor" aria-hidden="true"><path d="M309 480c-14 14-49 26-91 26-110 0-130-81-130-138V236H40v-72c66-17 93-74 97-124h62v112h81v84h-81v122c0 35 18 47 46 47 13 0 31-5 39-10l29 49z"/></svg>',
    "youtube": '<svg viewBox="0 0 576 512" class="{c}" fill="currentColor" aria-hidden="true"><path d="M549.7 124.1c-6.3-23.7-24.8-42.3-48.3-48.6C458.8 64 288 64 288 64S117.2 64 74.6 75.5c-23.5 6.3-42 24.9-48.3 48.6-11.4 42.9-11.4 132.3-11.4 132.3s0 89.4 11.4 132.3c6.3 23.7 24.8 41.5 48.3 47.8C117.2 448 288 448 288 448s170.8 0 213.4-11.5c23.5-6.3 42-24.1 48.3-47.8 11.4-42.9 11.4-132.3 11.4-132.3s0-89.4-11.4-132.3zm-317.5 213.5V175.2l142.7 81.2-142.7 81.2z"/></svg>',
    "instagram-color": '<svg viewBox="0 0 448 512" class="{c}" aria-hidden="true"><defs><linearGradient id="igg" x1="0%" y1="100%" x2="100%" y2="0%"><stop offset="0%" stop-color="#FEDA77"/><stop offset="25%" stop-color="#F58529"/><stop offset="50%" stop-color="#DD2A7B"/><stop offset="75%" stop-color="#8134AF"/><stop offset="100%" stop-color="#515BD4"/></linearGradient></defs><path fill="url(#igg)" d="M224 141c-63 0-114 51-114 114s51 114 114 114 114-51 114-114-51-114-114-114zm0 188c-41 0-74-33-74-74s33-74 74-74 74 33 74 74-33 74-74 74zm145-194c0 15-12 27-27 27s-27-12-27-27 12-27 27-27 27 12 27 27zM224 48c66 0 74 0 100 1 24 1 37 5 46 9 12 4 20 10 28 18s14 16 18 28c4 9 8 22 9 46 1 26 1 34 1 100s0 74-1 100c-1 24-5 37-9 46-4 12-10 20-18 28s-16 14-28 18c-9 4-22 8-46 9-26 1-34 1-100 1s-74 0-100-1c-24-1-37-5-46-9-12-4-20-10-28-18s-14-16-18-28c-4-9-8-22-9-46-1-26-1-34-1-100s0-74 1-100c1-24 5-37 9-46 4-12 10-20 18-28s16-14 28-18c9-4 22-8 46-9 26-1 34-1 100-1z"/></svg>',
    "chevron": '<svg viewBox="0 0 20 20" class="{c}" fill="currentColor" aria-hidden="true"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>',
    "check": '<svg viewBox="0 0 20 20" class="{c}" fill="currentColor" aria-hidden="true"><path d="M16.7 5.3a1 1 0 010 1.4l-7.5 7.5a1 1 0 01-1.4 0L3.3 9.7a1 1 0 011.4-1.4L8.5 12l6.8-6.7a1 1 0 011.4 0z"/></svg>',
    # 50% thicker stroke-style tick (use without fill-current — stroke takes currentColor)
    "check-bold": '<svg viewBox="0 0 24 24" class="{c}" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.4 4.5L19.5 7"/></svg>',
    "download": '<svg viewBox="0 0 20 20" class="{c}" fill="currentColor" aria-hidden="true"><path d="M10 2a1 1 0 011 1v7.59l2.3-2.3a1 1 0 011.4 1.42l-4 4a1 1 0 01-1.4 0l-4-4a1 1 0 011.4-1.42l2.3 2.3V3a1 1 0 011-1zM4 15a1 1 0 011 1v1h10v-1a1 1 0 112 0v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2a1 1 0 011-1z"/></svg>',
}
def icon(name, cls=""):
    return ICONS.get(name, "").format(c=cls)

# --- Per-page content expansions (authored by helper agents, kept in data/expansions/<kind>/<slug>.json)
_EXP_DIR = os.path.join(S.ROOT, "data", "expansions")
def load_expansion(kind, slug):
    """Return {'sections': [[h2,html],...], 'body': str, 'faqs': [[q,a],...]} or empties."""
    p = os.path.join(_EXP_DIR, kind, slug + ".json")
    if not os.path.exists(p):
        return {"sections": [], "body": "", "faqs": []}
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return {"sections": [], "body": "", "faqs": []}
    return {"sections": d.get("sections", []), "body": d.get("body", ""), "faqs": d.get("faqs", [])}

@functools.lru_cache(maxsize=None)
def _dims(abspath):
    """Real pixel dimensions via macOS sips (cached). Returns (w,h) or (None,None)."""
    try:
        out = subprocess.check_output(["/usr/bin/sips", "-g", "pixelWidth", "-g", "pixelHeight", abspath],
                                      text=True, stderr=subprocess.DEVNULL)
        w = re.search(r"pixelWidth:\s*(\d+)", out)
        h = re.search(r"pixelHeight:\s*(\d+)", out)
        return (int(w.group(1)), int(h.group(1))) if w and h else (None, None)
    except Exception:
        return (None, None)

def img(src, alt, cls="", eager=False, extra=""):
    """<img> with auto width/height (no CLS), lazy by default, alt<=100 chars (bible)."""
    src = src.lstrip("/")
    w, h = _dims(os.path.join(S.ROOT, src))
    wh = (f' width="{w}" height="{h}"' if w else "")
    loading = ' loading="eager" fetchpriority="high"' if eager else ' loading="lazy"'
    a = esc(_clip(alt, 100))
    # Responsive hero: serve an 800w variant to mobile (LCP) when one exists for this eager image.
    srcset = ""
    if eager and w and src.endswith(".webp"):
        s800 = src[:-5] + "-800.webp"
        if os.path.exists(os.path.join(S.ROOT, s800)):
            srcset = f' srcset="/{s800} 800w, /{src} {w}w" sizes="100vw"'
    return f'<img src="/{src}" alt="{a}"{wh}{srcset}{loading} decoding="async" class="{cls}"{(" " + extra) if extra else ""}>'

# ---- contextual photo pool (real, optimised webp moving photos) ----
PHOTOS = [
    ("orwell-lorry-packing-moving-storage", "An Orwell Removals lorry — packing, moving and storage in Ipswich"),
    ("orwell-van-packing-moving-storage", "An Orwell Removals van — packing, moving and storage in Ipswich"),
    ("orwell-box-lorry-ipswich-street", "An Orwell Removals box lorry on an Ipswich street"),
    ("orwell-box-lorry-residential-street", "An Orwell Removals box lorry on a residential street"),
    ("orwell-lorry-loading-on-street", "An Orwell Removals lorry loading on a street"),
    ("orwell-lorry-van-outside-home", "An Orwell Removals lorry and van outside a customer's home"),
    ("orwell-lorry-house-driveway", "An Orwell Removals lorry on a house driveway"),
    ("orwell-lorry-period-suffolk-house", "An Orwell Removals lorry at a period Suffolk house"),
    ("orwell-lorry-gravel-driveway", "An Orwell Removals lorry on a gravel driveway"),
    ("orwell-lorry-livery-ipswich-phone", "The Orwell Removals lorry livery showing the Ipswich phone number"),
    ("orwell-lorry-outside-suffolk-house", "An Orwell Removals box lorry parked outside a Suffolk house"),
    ("orwell-crew-loading-townhouse", "An Orwell Removals crew loading at a red-brick townhouse"),
    ("orwell-van-outside-suffolk-home", "An Orwell Removals van outside a Suffolk home"),
    ("orwell-van-on-customer-driveway", "An Orwell Removals van on a customer's driveway"),
    ("orwell-van-modern-driveway", "An Orwell Removals van on a modern block-paved driveway"),
    ("orwell-van-narrow-suffolk-street", "An Orwell Removals van on a narrow Suffolk street"),
    ("orwell-van-brick-suffolk-house", "An Orwell Removals van outside a brick Suffolk house"),
    ("orwell-van-period-suffolk-house", "An Orwell Removals van outside a period Suffolk house"),
    ("orwell-van-narrow-side-passage", "An Orwell Removals van down a narrow side passage"),
    ("orwell-van-outside-modern-home", "An Orwell Removals van outside a modern Suffolk home"),
    ("orwell-van-packed-with-boxes", "An Orwell van packed with moving boxes"),
    ("two-orwell-vans-residential-street", "Two Orwell Removals vans on a residential street"),
    ("orwell-luton-van-ipswich-road", "An Orwell Removals Luton van on an Ipswich road"),
    ("loaded-luton-van-residential-street", "A loaded Orwell Luton van on a residential street"),
    ("luton-van-loading-at-house", "An Orwell Removals Luton van loading at a house with a hedge"),
    ("clean-luton-van-interior", "The clean interior of an Orwell Removals Luton van"),
    ("mover-loading-van-on-driveway", "An Orwell mover loading the van on a customer's driveway"),
    ("orwell-commercial-shop-move", "Orwell handling a shop and commercial move on the high street"),
    ("orwell-removals-storage-signage", "Orwell Removals & Storage signage on an Ipswich house"),
    ("removal-lorry-suffolk-street", "An Orwell Removals lorry on a Suffolk street"),
    ("packed-boxes-wrapped-furniture", "Packed boxes and wrapped furniture ready for an Orwell move"),
    ("wrapped-furniture-strapped-in-van", "Wrapped furniture strapped securely inside an Orwell removal van"),
    ("furniture-wrapped-inside-removal-van", "Furniture wrapped and strapped inside an Orwell removal van"),
    ("wrapped-furniture-loaded-in-van", "Wrapped furniture loaded inside an Orwell removal van"),
    ("van-loaded-boxes-wrapped-furniture", "An Orwell van loaded with boxes and wrapped furniture"),
    ("orwell-boxes-loaded-in-van", "Orwell-branded boxes loaded inside a removal van"),
    ("wrapped-sofa-in-removal-van", "A wrapped sofa loaded inside an Orwell removal van"),
    ("wrapped-furniture-and-boxes", "Wrapped furniture and boxes ready to move"),
    ("wrapped-furniture-outside-period-home", "Wrapped furniture waiting outside a period Suffolk home"),
    ("wrapped-packing-materials-ready", "Wrapped packing materials ready for an Orwell move"),
    ("armchairs-wrapped-for-removal", "Armchairs wrapped and ready for an Orwell removal"),
    ("suffolk-bungalow-moving-day", "A Suffolk bungalow on moving day"),
    ("modern-suffolk-housing-estate", "A modern Suffolk housing estate, the kind of area Orwell covers"),
    ("removal-lorry-customer-driveway", "A removal lorry on a customer's driveway"),
    ('removal-lorry-parked-on-residential-street', 'An Orwell Removals lorry parked on a residential street in Ipswich, Suffolk'),
    ('removal-vans-outside-detached-house', 'Orwell Removals vans parked outside a detached house ready for a move in Ipswich'),
    ('crew-loading-luton-van-tail-lift', 'A removals crew member loading a Luton van with the tail lift up in Ipswich'),
    ('storage-container-exterior-at-depot', 'A steel storage container at the Orwell Removals storage depot in Ipswich'),
    ('removal-lorry-and-trailer-on-road', 'A large Orwell Removals lorry and trailer travelling on the road in Suffolk'),
    ('white-removal-van-on-driveway', 'A white Orwell Removals van parked on a residential driveway in Ipswich'),
    ('furniture-and-boxes-loaded-in-lorry', 'Furniture and packed boxes loaded inside a removal lorry ready for transport'),
    ('sofas-wrapped-and-stacked-in-lorry', 'Wrapped sofas stacked carefully inside the back of a removal lorry in Ipswich'),
    ('wooden-storage-vaults-stacked-in-warehouse', 'Wooden storage vaults stacked with stored belongings in the Ipswich depot'),
    ('red-removal-van-on-wet-street', 'A red Orwell Removals van parked on a wet residential street in Ipswich'),
    ('wrapped-sofa-inside-empty-lorry', 'A wrapped sofa standing inside the empty body of a removal lorry'),
    ('boxes-and-furniture-stacked-in-van', 'Boxes and wrapped furniture neatly stacked inside a removal van interior'),
    ('bungalow-frontage-with-driveway', 'A bungalow frontage with a gravel driveway ready for a house removal in Suffolk'),
    ('boxes-loaded-inside-removal-lorry', 'Packed cardboard boxes loaded inside the body of a removal lorry in Ipswich'),
    ('removal-lorry-fleet-on-rural-road', 'An Orwell Removals lorry parked on a tree-lined rural road in Suffolk'),
    ('removal-lorry-under-autumn-trees', 'A white Orwell Removals lorry parked beneath autumn trees in Ipswich'),
    ('storage-depot-warehouse-exterior', 'The exterior of the Orwell Removals storage depot warehouse in Ipswich'),
    ('stacked-cardboard-moving-boxes', 'A stack of cardboard moving boxes ready for a house removal in Ipswich'),
    ('removal-vans-outside-modern-flats', 'Orwell Removals vans parked outside modern flats during a move in Ipswich'),
    ('luton-van-with-tail-lift-on', 'A Luton removal van with its tail lift down parked on a street in Ipswich'),
    ('removals-lorry-parked-residential-street', 'Orwell Removals lorry parked on a residential street outside red brick houses'),
    ('removals-truck-parked-suburban-road', 'Removals truck parked on a quiet suburban road lined with trees'),
    ('removals-van-outside-stone-building', 'White removals van parked outside a traditional stone building'),
    ('loaded-van-interior-blankets-boxes', 'Interior of a removals van loaded with wrapped furniture and boxes'),
    ('removals-van-outside-pink-house', 'White removals van parked on a driveway beside a pink rendered house'),
    ('bungalow-conservatory-front-garden', 'Detached bungalow with a conservatory and front garden on a sunny day'),
    ('removal-crew-loading-house-doorway', 'Removal crew loading items from a house doorway with information board'),
    ('removals-van-suburban-street-houses', 'Branded removals van parked on a suburban street outside homes'),
    ('office-interior-desks-furniture', 'Open plan office interior with desks and furniture before an office move'),
    ('residential-footpath-houses-view', 'Residential footpath leading between houses on an overcast day'),
    ('stacked-wooden-storage-vaults', 'Stacked wooden storage vaults used for secure furniture storage'),
    ('wrapped-furniture-storage-room', 'Wrapped furniture and packed items stored together in a storage room'),
    ('removals-truck-parked-car-park', 'Removals truck and car parked in a tarmac car park beside buildings'),
    ('wrapped-mattresses-furniture-storage', 'Wrapped mattresses and furniture stacked together in storage'),
    ('removals-lorry-side-branding', 'Side view of a branded removals lorry parked outdoors'),
    ('stacked-cardboard-boxes-storage', 'Stacked labelled cardboard moving boxes filling a storage area'),
    ('wooden-storage-vault-close-up', 'Close up of a wooden storage vault holding packed household goods'),
    ('removals-van-parked-street-kerb', 'White removals van parked at the kerb on a residential street'),
    ('wood-shavings-packing-material', 'Wood shavings and packing material used to protect stored items'),
    ('removals-lorry-outside-bungalow', 'Removals lorry parked outside a bungalow ready for a house move'),
    ('orwell-removals-lorry-outside-house', 'Orwell Removals lorry parked outside a residential house on moving day in Suffolk'),
    ('orwell-removals-branded-van-road', 'Red and white Orwell Removals branded van parked on a residential road'),
    ('removals-lorry-loading-driveway', 'Removals lorry with open rear loading furniture on a tree-lined driveway'),
    ('lorry-loading-bay-doors-street', 'Open lorry loading bay doors on a quiet residential street'),
    ('office-interior-clearance-space', 'Bright office interior with desks during a commercial removals clearance'),
    ('sandy-ground-excavated-cables', 'Excavated sandy ground with exposed cables on a building site'),
    ('removals-lorry-loading-house-driveway', 'Orwell Removals lorry loading boxes outside a detached house driveway'),
    ('orwell-removals-lorry-front-lawn', 'Orwell Removals lorry parked on a road beside a green front lawn'),
    ('removals-vehicles-parked-street', 'Removals vehicles parked along a brick terraced residential street'),
    ('wrapped-furniture-stacked-storage', 'Wrapped furniture and boxes stacked and protected for storage'),
    ('lorry-loading-bay-open-bins', 'Open removals lorry loading bay beside wheelie bins on collection day'),
    ('orwell-removals-van-residential-street', 'White Orwell Removals van parked on a residential street under blue sky'),
    ('stacked-boxes-wrapped-goods-store', 'Stacked cardboard boxes and wrapped goods inside a storage area'),
    ('orwell-removals-lorry-outside-houses', 'Orwell Removals lorry parked on grass outside a row of houses'),
    ('orwell-removals-lorry-pink-house', 'Orwell Removals lorry parked outside a pink rendered house'),
    ('orwell-removals-lorry-suburban-road', 'Orwell Removals lorry parked on a suburban road on moving day'),
    ('removals-van-fleet-parked-evening', 'Orwell Removals van fleet parked together in the evening light'),
    ('removals-lorry-brick-terrace-street', 'Removals lorry parked beside a brick terraced house on a street'),
    ('orwell-removals-van-cobbled-driveway', 'Orwell Removals van parked on a cobbled driveway outside houses'),
    ('removals-van-residential-road-distance', 'Orwell Removals van parked in the distance on a residential road'),
    ('orwell-removals-van-residential-street-2', 'Orwell Removals box van parked outside houses on a residential street in Ipswich'),
    ('removals-lorry-loaded-furniture-cab', 'White removals lorry with loaded furniture visible behind the cab'),
    ('boxes-cable-reels-loaded-lorry', 'Cardboard boxes and large cable reels packed inside a loaded removals lorry'),
    ('removals-lorry-parked-suburban-road', 'Large removals lorry parked on a suburban road outside houses'),
    ('removals-van-terraced-houses-street', 'Removals van parked on a street lined with terraced houses'),
    ('wrapped-furniture-blankets-van-interior', 'Furniture wrapped in protective blankets stacked inside a removals van'),
    ('removals-van-loading-pink-house', 'Removals van loading household items outside a pink-rendered house'),
    ('orwell-removals-lorry-depot-yard', 'Orwell Removals lorry parked in a depot yard with open shutter door'),
    ('orwell-removals-crew-branded-banner', 'Orwell Removals crew member standing beside a branded company banner'),
    ('removals-lorry-street-row-houses', 'Removals lorry working on a street beside a row of brick houses'),
    ('removals-vans-period-property-driveway', 'Removals vans parked on a paved driveway outside a large period property'),
    ('removals-van-tree-lined-road', 'Orwell Removals van parked on a quiet tree-lined residential road'),
    ('wrapped-furniture-boxes-van-loading', 'Wrapped furniture and stacked boxes being loaded into a removals van'),
    ('narrow-alley-church-background-access', 'Narrow alley access path with a church tower visible in the background'),
    ('boxes-stacked-lorry-interior-loading', 'Cardboard boxes stacked high inside a removals lorry during loading'),
    ('white-removals-van-roadside-houses', 'White removals van parked at the roadside outside residential houses'),
    ('removals-van-sunlit-residential-street', 'Removals van parked on a sunlit residential street with flare'),
    ('orwell-removals-lorry-road-houses', 'Orwell Removals lorry driving along a road past period houses'),
    ('white-removals-van-parked-kerb', 'White Orwell Removals van parked at the kerb on a town street'),
    ('removals-van-loading-bay-shutter', 'Removals van interior viewed from the open rear shutter loading bay'),
    ('orwell-removals-lorry-village-driveway', 'Orwell Removals branded box lorry parked on a village driveway near trees'),
    ('mercedes-removals-lorry-country-lane', 'Mercedes removals lorry parked on a narrow country lane by hedges'),
    ('removals-lorry-village-street-cones', 'Removals lorry parked on a village street with traffic cones set out'),
    ('white-removals-van-loading-bay', 'White removals van parked outside a building loading bay entrance'),
    ('wrapped-furniture-loaded-lorry-ramp', 'Wrapped furniture and blankets loaded inside a lorry on the tail ramp'),
    ('orwell-removals-lorry-outside-house-2', 'Orwell Removals lorry parked outside a house with a blue car'),
    ('white-removals-van-outside-brick-house', 'White removals van parked on the drive of a red brick house'),
    ('removals-lorry-night-driveway-lights', 'Removals lorry parked at night on a driveway with headlights on'),
    ('removals-lorry-tail-lift-loading', 'Removals lorry with tail lift down loading goods outside a building'),
    ('removals-van-rural-farmyard-timber-barn', 'Removals van parked in a rural farmyard beside a timber barn'),
    ('mercedes-removals-luton-van-street', 'Mercedes Luton removals van parked on a residential street'),
    ('white-house-removals-van-driveway', 'Removals van parked on a driveway beside a white rendered house'),
    ('orwell-removals-lorry-corner-trees', 'Orwell Removals lorry parked on a corner near brick houses and trees'),
    ('mercedes-removals-lorry-front-grille', 'Front view of a Mercedes removals lorry showing grille and cab'),
    ('lorry-load-secured-blankets-straps', 'Inside a removals lorry with furniture under blankets secured by straps'),
    ('orwell-removals-lorry-tree-lined-road', 'Orwell Removals lorry parked on a quiet tree-lined road'),
    ('removals-lorry-outside-period-house', 'Removals lorry parked outside a large period house with two cars'),
    ('white-removals-van-rural-track', 'White removals van parked on a rural track by trees and a fence'),
    ('orwell-removals-lorry-residential-road', 'Orwell Removals lorry parked on a residential road by houses'),
    ('karls-branded-lorry-house-driveway', 'Branded lorry parked on a driveway beside a house and parked car'),
    ('removals-van-outside-suffolk-cottage', 'Orwell Removals van parked outside a rural Suffolk cottage on moving day'),
    ('orwell-removals-van-on-residential-street', 'Orwell Removals branded van parked on a residential street during a house move'),
    ('luton-van-loading-outside-new-build', 'Removals Luton van with tail-lift loading outside a modern new-build house'),
    ('white-removals-van-outside-suburban-house', 'White removals van parked on driveway outside a suburban semi-detached house'),
    ('luton-removals-van-on-driveway', 'Orwell Luton removals van parked on a driveway by a block of flats'),
    ('orwell-storage-container-on-street', 'Orwell branded storage container unit parked on a terraced residential street'),
    ('loaded-removals-lorry-interior-furniture', 'Interior of a loaded removals lorry packed with wrapped furniture and boxes'),
    ('luton-van-tail-lift-loading-outside', 'Removals Luton van with open tail-lift loading outside a house'),
    ('orwell-removals-storage-lorry-side-branding', 'Orwell Removals and storage lorry showing side branding parked outdoors'),
    ('orwell-storage-container-by-garden', 'Orwell removals and storage container unit beside a garden with flowers'),
    ('empty-removals-van-interior-blankets', 'Interior view of an empty removals van lined with protective moving blankets'),
    ('removals-van-interior-door-detail', 'Close-up of a removals van interior wall and door panel detail'),
    ('orwell-removals-lorry-outside-house-3', 'Orwell Removals lorry parked outside a residential house ready to load'),
    ('house-frontage-with-paved-driveway', 'Frontage of a modern house with paved driveway on a removals job'),
    ('loaded-lorry-interior-stacked-furniture', 'Interior of removals lorry packed with stacked wrapped furniture and crates'),
    ('luton-removals-van-outside-flats', 'White Luton removals van parked outside a block of residential flats'),
    ('orwell-removals-lorry-residential-driveway', 'Orwell Removals lorry parked on a residential driveway by red cars'),
    ('orwell-storage-container-outside-house', 'Orwell storage container positioned outside a detached house for a move'),
    ('stacked-storage-crates-wrapped-goods', 'Stacked storage crates and wrapped household goods ready for storage'),
    ('orwell-removals-lorry-in-green-field', 'Orwell Removals and storage lorry parked in a green grassy field'),
    ('removals-van-outside-timber-house', 'Orwell Removals van parked outside a timber-framed house in Suffolk'),
    ('citizens-advice-banner-storage-cage', 'Citizens Advice banner displayed against a wire storage cage'),
    ('white-removals-lorry-on-driveway', 'White removals lorry parked on a residential driveway by trees'),
    ('white-van-outside-brick-house', 'White removals van parked outside a red brick house'),
    ('removals-van-on-residential-driveway', 'Removals van parked on a driveway beside a house and trees'),
    ('wrapped-mattress-loaded-in-van', 'Wrapped mattress and protected furniture loaded inside a van'),
    ('orwell-removals-van-front-view', 'Front view of branded Orwell Removals van on a sunny day'),
    ('mercedes-removals-lorry-on-street', 'Mercedes removals lorry parked on a residential street'),
    ('removals-van-outside-victorian-house', 'Removals van outside a large Victorian house with parked cars'),
    ('white-van-parked-on-block-paving', 'White removals van parked on block-paved driveway'),
    ('wrapped-furniture-being-unloaded-van', 'Wrapped furniture being unloaded from removals van near house'),
    ('empty-warehouse-storage-interior', 'Empty warehouse storage interior with grey flooring and units'),
    ('wrapped-furniture-stacked-inside-van', 'Wrapped furniture and items stacked inside removals van'),
    ('loaded-removals-van-interior-blankets', 'Removals van interior packed with blanket-wrapped furniture'),
    ('removals-van-outside-new-build-house', 'Removals van parked outside a new-build estate house'),
    ('orwell-van-on-new-build-street', 'Orwell Removals van on a street of new-build homes'),
    ('white-trailer-on-grass-verge', 'White box trailer parked on a grass verge'),
    ('removals-lorry-outside-townhouses', 'Branded removals lorry parked outside modern brick townhouses'),
    ('open-lorry-with-loading-ramp', 'Open removals lorry with rear loading ramp and tail lift'),
    ('removals-van-on-narrow-street', 'Removals van parked on a narrow town street by buildings'),
    ('removals-van-rural-village-street', 'Orwell Removals van parked on a quiet village street in rural Suffolk'),
    ('removals-van-outside-barn-conversion', 'White removals van parked on a driveway beside a brick barn conversion'),
    ('luton-van-loading-outside-house', 'Luton removals van with tail-lift open outside a detached house'),
    ('blue-trailer-with-load-outdoors', 'Blue flatbed trailer loaded with goods under trees outdoors'),
    ('tree-lined-country-lane-autumn', 'Empty tree-lined country lane in autumn in rural Suffolk'),
    ('removals-lorry-on-country-road', 'Orwell Removals lorry travelling along a tree-lined country road'),
    ('two-removals-vans-on-driveway', 'Two white removals vans parked together on a paved driveway'),
    ('movers-handling-upright-piano', 'Two removals crew carefully handling an upright piano on a doorstep'),
    ('grand-piano-in-room', 'Grand piano positioned inside a room being prepared for moving'),
    ('removals-van-by-pink-cottage', 'Removals van parked beside a pink rendered cottage with weeping willow'),
    ('wrapped-piano-on-trolley', 'Piano wrapped in protective covering loaded on a moving trolley'),
    ('removals-van-on-block-paved-drive', 'White removals van parked on a block-paved driveway by a house'),
    ('luton-van-clear-blue-sky', 'White Luton removals van parked under a clear blue sky'),
    ('movers-outside-terraced-houses', 'Removals crew working outside a row of terraced houses on bin day'),
    ('empty-garage-storage-space', 'Empty concrete garage interior used as storage space'),
    ('removals-lorry-by-detached-house', 'Box-bodied removals lorry parked outside a modern detached house'),
    ('village-hall-event-seating', 'Village hall interior with stacked blue chairs and tables'),
    ('container-storage-yard-sunrise', 'Steel storage containers in a depot yard at sunrise'),
    ('stored-goods-in-warehouse-vault', 'Stacked stored household goods inside a warehouse storage area'),
    ('removals-van-front-on-driveway', 'Front view of Orwell Removals van parked on a residential driveway'),
    ('stone-garden-wall-driveway', 'Stone garden wall and gravel driveway outside a property'),
    ('crew-moving-large-round-object', 'Removals crew member handling a large round object on a driveway'),
    ('white-van-rural-driveway-hedge', 'White removals van parked on a rural driveway beside a tall hedge'),
    ('orwell-removals-vans-pair', 'Pair of Orwell Removals white vans parked side by side'),
    ('removals-lorry-loading-house', 'Removals lorry parked outside a house ready for loading'),
    ('orwell-removals-storage-signboard', 'Orwell Removals and Storage company signboard outside a building'),
    ('removals-lorry-stone-building', 'Removals lorry parked beside a tall stone building'),
    ('removals-lorry-outside-house', 'Orwell removals lorry parked outside a detached house'),
    ('orwell-removals-lorry-building', 'Orwell Removals lorry parked outside a brick building'),
    ('office-building-aqua-signage', 'Office building entrance with signage and ramp access'),
    ('removals-lorry-open-tail-lift', 'Removals lorry with rear doors open showing the load space'),
    ('orwell-removals-storage-lorry-side', 'Side view of Orwell Removals and Storage branded lorry'),
    ('removals-van-residential-street', 'Removals van parked on a residential street outside a house'),
    ('scania-removals-lorry-front', 'Front view of a Scania removals lorry on a wet road'),
    ('quiet-residential-street-houses', 'Quiet residential street with houses and parked cars'),
    ('removals-vans-terraced-street', 'Removals vans parked along a terraced residential street'),
    ('loading-boxes-into-van', 'Boxes being loaded into the back of a removals van'),
    ('narrow-village-lane-houses', 'Narrow village lane lined with houses and greenery'),
    ('daf-removals-storage-lorry-front', 'Front of a DAF Orwell Removals and Storage lorry'),
    ('orwell-removals-lorry-side-trees', 'Side of Orwell Removals lorry parked near trees'),
    ('removals-van-on-driveway-bungalow', 'Orwell Removals van parked on a driveway outside a bungalow with ramp out'),
    ('removals-lorry-parked-residential-street-2', 'Orwell Removals lorry parked on a residential street outside houses'),
    ('removals-lorry-outside-apartment-block', 'Orwell Removals lorry parked beside a brick apartment block'),
    ('removals-van-bungalow-cloudy-day', 'Orwell Removals van on a road outside a bungalow on an overcast day'),
    ('removals-lorry-ramp-out-driveway', 'Orwell Removals lorry with loading ramp out on a residential driveway'),
    ('removals-lorry-cab-front-view', 'Front view of the Orwell Removals lorry cab parked on a road'),
    ('removals-lorry-loading-outside-house', 'Orwell Removals lorry loading goods outside a detached house'),
    ('white-removals-van-rural-road', 'White Orwell Removals van parked on a rural road by hedgerow'),
    ('removals-lorry-outside-flats-building', 'Orwell Removals lorry parked outside a multi-storey block of flats'),
    ('removals-van-side-view-street', 'Side view of Orwell Removals van parked on a street with houses'),
    ('removals-van-lorry-car-park', 'Orwell Removals vehicles parked in a car park area near a building'),
    ('removals-lorry-outside-brick-houses', 'Orwell Removals lorry parked outside a row of brick terraced houses'),
    ('furniture-loaded-tail-lift-removal', 'Furniture loaded on a removal lorry tail lift outside a property'),
    ('removals-van-tree-lined-street', 'Orwell Removals van parked on a tree-lined residential street'),
    ('removals-van-outside-semi-detached-house', 'Orwell Removals van parked outside a semi-detached house'),
    ('empty-removal-lorry-interior-loading', 'Empty interior of a removal lorry ready for loading furniture'),
    ('removals-van-modern-housing-estate', 'Orwell Removals van parked on a modern housing estate road'),
    ('removals-van-driveway-detached-house', 'Orwell Removals van on a driveway outside a detached house'),
    ('green-storage-building-depot-yard', 'Green storage building in a depot yard under cloudy sky'),
    ('removals-lorry-residential-street-houses', 'Orwell Removals lorry parked on a residential street with houses'),
    ('two-orwell-removals-vans-parked', 'Two Orwell Removals white Luton vans parked side by side in Ipswich'),
    ('removals-vans-lined-up-outside-building', 'Row of Orwell Removals vans lined up outside a building'),
    ('orwell-removals-lorry-loading-bay', 'Orwell Removals large lorry parked at a loading bay'),
    ('removals-van-outside-historic-house', 'Orwell Removals van parked outside a grand historic house'),
    ('removals-van-outside-brick-house', 'Orwell Removals van parked outside a red brick house'),
    ('lorry-loaded-with-stacked-boxes', 'Removals lorry interior loaded with stacked cardboard boxes and furniture'),
    ('daf-removals-lorry-with-crew', 'Orwell Removals DAF lorry with crew members beside it'),
    ('removals-van-by-house-stone-steps', 'Removals van parked beside a house with stone steps and garden'),
    ('wrapped-furniture-stored-in-vaults', 'Wrapped furniture and packed goods stored in a storage facility'),
    ('removals-van-on-narrow-street-2', 'Orwell Removals van parked on a narrow residential street'),
    ('gravel-driveway-with-trees', 'Gravel driveway lined with mature trees and hedges'),
    ('large-detached-house-front-view', 'Front view of a large detached period house with gravel drive'),
    ('daf-removals-lorry-front-view', 'Orwell Removals DAF lorry front view parked outdoors'),
    ('stacked-boxes-in-storage-area', 'Stacked cardboard boxes and goods in a storage holding area'),
    ('removals-lorry-outside-house-2', 'Orwell Removals lorry parked outside a residential house'),
    ('orwell-removals-lorry-side-branding', 'Orwell Removals lorry showing large side branding and logo'),
    ('removals-van-on-gravel-drive', 'Orwell Removals van parked on a gravel driveway'),
    ('removals-lorry-rear-doors-open', 'Orwell Removals lorry with rear doors open ready for loading'),
    ('orwell-removals-crew-team-portrait', 'Two Orwell Removals crew members posing for a team portrait'),
    ('removals-lorry-outside-stone-house', 'Orwell Removals lorry parked outside a large stone country house'),
    ('removals-lorry-parked-residential-street-3', 'Orwell Removals lorry parked on a residential street on a sunny day'),
    # ---- 22 photos added from the customer's June 2026 upload ----
    ('orwell-crew-of-four-with-lorry', 'The Orwell Removals crew of four in front of a box lorry outside a home'),
    ('armchair-in-orwell-padded-cover', 'An armchair wrapped in a padded Orwell Removals furniture cover'),
    ('suite-wrapped-in-padded-covers', 'A sofa and armchairs wrapped in padded Orwell Removals covers in a living room'),
    ('orwell-branded-wardrobe-cartons-stacked', 'Orwell Removals branded wardrobe cartons stacked in the van'),
    ('cartons-packed-inside-removal-van', 'Cartons packed neatly inside an Orwell Removals van'),
    ('upright-piano-strapped-in-van', 'An upright piano padded and strapped inside an Orwell removal van'),
    ('divan-bed-base-bubble-wrapped', 'A divan bed base bubble-wrapped and ready for an Orwell move'),
    ('padded-cover-protecting-tall-mirror', 'A padded Orwell Removals cover protecting a tall mirror in a doorway'),
    ('staircase-carpet-protected-with-film', 'A staircase carpet protected with film during an Orwell house move'),
    ('hallway-floor-felt-runner-protection', 'A hallway floor protected with felt runners and film during a move'),
    ('item-bubble-wrapped-for-protection', 'A household item bubble-wrapped for protection before an Orwell move'),
    ('chest-of-drawers-bubble-wrapped', 'A chest of drawers bubble-wrapped for protection during a move'),
    ('furniture-in-furni-soft-wrap', 'Furniture packed in Furni-Soft protective wrap ready to move'),
    ('packed-storage-container-warehouse', 'A packed wooden storage container in the Orwell storage warehouse'),
    ('floor-protection-runner-doorway', 'A felt floor-protection runner laid through a doorway during a move'),
    ('wardrobe-box-with-hanging-clothes', 'A portable wardrobe box with clothes hanging on the rail'),
    ('orwell-lorry-at-orwell-bridge', 'An Orwell Removals lorry on the road beneath the Orwell Bridge in Ipswich'),
    ('felt-runners-protecting-floors', 'Felt runners protecting carpet and wood floors during a house move'),
    ('canvas-moving-straps-on-rack', 'Canvas moving straps hung on a rack at the Orwell Removals depot'),
    ('stacks-of-removal-blankets', 'Stacks of folded removal blankets at the Orwell Removals depot'),
    ('orwell-lorries-then-and-now', 'Orwell Removals lorries then and now, showing the older and current livery'),
    ('hallway-stairs-fully-protected', 'A hallway and stairs fully protected with covers and mats during a move'),
]
# 287 customer-approved photos (265 prior + 22 added from the June 2026 upload).

def page_photos(seed, n=5):
    """Deterministic, distinct photos for a page (variety across pages, no dupes within).
    Excludes the photo reserved for the site-wide quote band so no page repeats it."""
    pool = [p for p in PHOTOS if p[0] != QUOTE_BAND_PHOTO]
    start = zlib.crc32(str(seed).encode()) % len(pool)
    return [pool[(start + i) % len(pool)] for i in range(min(n, len(pool)))]

# ---- topic matching: pick the photo whose alt text best fits a paragraph ----
_MATCH_STOP = {  # brand / location / generic filler — NOT topical subjects, so they must not drive matching
    "orwell", "ipswich", "suffolk", "westerfield", "removals", "removal", "across", "into",
    "with", "your", "that", "this", "from", "team", "crew", "movers", "mover", "professional",
    "professionally", "moving", "move", "house", "home", "homes", "family", "large", "whole",
    "simply", "keeping", "grand", "room", "rooms", "classical", "view", "busy", "recent", "based",
    "leading", "modern", "trained", "fully", "insured", "great", "care", "careful", "carefully",
    "work", "working", "completing", "preparing", "transport", "ready", "during", "full", "every",
    "single", "smaller", "handy", "online", "flexible", "choose", "settled", "sooner", "bridge",
    "complete", "options", "optional", "extras", "help", "kind", "take", "takes", "more",
    "daunting", "manageable", "mountain", "days"}
def _stem(w):
    return w[:-1] if len(w) > 4 and w.endswith("s") else w
def _kwset(text):
    return set(_stem(w) for w in re.findall(r'[a-z]+', text.lower())
               if len(w) > 3 and w not in _MATCH_STOP)
def _wc(text):
    d = {}
    for w in re.findall(r'[a-z]+', text.lower()):
        if len(w) > 3 and w not in _MATCH_STOP:
            sw = _stem(w); d[sw] = d.get(sw, 0) + 1
    return d
_PHOTO_DF = {}                                  # how many photos' alts contain each word
for _p in PHOTOS:
    for _w in _kwset(_p[1]):
        _PHOTO_DF[_w] = _PHOTO_DF.get(_w, 0) + 1
def match_photo(text, used=(), salt="", topn=6, prefer=None):
    """SITE RULE: the photo beside a paragraph must be about what the paragraph says.
    Score each pool photo by alt-vs-text word overlap, weighting rare/distinctive words
    (wardrobe, painting, storage, forklift...) most. Returns None if nothing overlaps.

    To avoid every page looking templated, we keep the `topn` MOST RELEVANT photos and,
    when a `salt` is given (e.g. the page slug + row index), deterministically pick one of
    them — so different pages/rows show DIFFERENT but still on-topic images.
    `prefer` (a set of slugs) restricts the pool — used to keep a section's imagery on a
    sub-theme (e.g. storage pages → only stored-goods / boxes / signage shots)."""
    tc = _wc(text)
    if not tc:
        return None
    scored = []
    for p in PHOTOS:
        if p[0] in used or p[0] == QUOTE_BAND_PHOTO:
            continue
        if prefer and p[0] not in prefer:
            continue
        s = sum(tc.get(w, 0) / _PHOTO_DF.get(w, 1) for w in _kwset(p[1]))
        if s > 0:
            scored.append((s, p))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1][0]))   # score desc, slug for determinism
    top = [p for _, p in scored[:max(1, topn)]]
    if not salt:
        return top[0]
    h = int(hashlib.md5(salt.encode("utf-8")).hexdigest(), 16)
    return top[h % len(top)]

def photo_block(photo, cls="w-full h-full object-cover", eager=False):
    fn, alt = photo
    return img("images/photos/" + fn + ".webp", alt, cls=cls, eager=eager)

def text_with_image(inner_html, photo, reverse=False, bg="bg-white"):
    """Two-column section: prose beside a contextual photo. The text + image sit
    inside the same cols-2..11 envelope as prose() so left/right edges line up
    with the rest of the page's content (no misaligned blocks)."""
    media = (f'<div class="h-64 sm:h-80 lg:h-full lg:min-h-[22rem] overflow-hidden rounded-xl shadow-custom">'
             f'{photo_block(photo)}</div>')
    # text occupies 5 of 12 cols, image 5 of 12; col-start positions them within cols 2..11
    if reverse:
        text_cls = "col-span-12 lg:col-span-5 lg:col-start-7"
        pic_cls = "col-span-12 lg:col-span-5 lg:col-start-2 lg:row-start-1"
    else:
        text_cls = "col-span-12 lg:col-span-5 lg:col-start-2"
        pic_cls = "col-span-12 lg:col-span-5 lg:col-start-7"
    text = f'<div class="{text_cls}">{inner_html}</div>'
    pic = f'<div class="{pic_cls}">{media}</div>'
    return section(f'<div class="grid grid-cols-12 gap-8 lg:gap-12 items-center">{text}{pic}</div>', bg=bg)

def text_with_video(inner_html, slug, reverse=False, bg="bg-white"):
    """Two-column row: prose beside an ambient, muted, auto-playing looped video
    (no sound, no controls). Files: /videos/<slug>.mp4 + .webp poster. Portrait clips
    are width-capped and centred so they don't dominate the row."""
    vw, vh = _dims(os.path.join(S.ROOT, "videos", f"{slug}.webp"))
    vw, vh = (vw or 1280), (vh or 720)
    style = ' style="max-width:300px"' if vh > vw else ""
    media = (f'<figure class="mx-auto rounded-xl overflow-hidden shadow-custom bg-black"{style}>'
             f'<video class="w-full block" autoplay muted loop playsinline preload="metadata" '
             f'poster="/videos/{slug}.webp" width="{vw}" height="{vh}">'
             f'<source src="/videos/{slug}.mp4" type="video/mp4"></video></figure>')
    if reverse:
        text_cls = "col-span-12 lg:col-span-5 lg:col-start-7"
        pic_cls = "col-span-12 lg:col-span-5 lg:col-start-2 lg:row-start-1"
    else:
        text_cls = "col-span-12 lg:col-span-5 lg:col-start-2"
        pic_cls = "col-span-12 lg:col-span-5 lg:col-start-7"
    return section(f'<div class="grid grid-cols-12 gap-8 lg:gap-12 items-center">'
                   f'<div class="{text_cls}">{inner_html}</div><div class="{pic_cls}">{media}</div></div>', bg=bg)

def _para_blocks(html):
    """(heading_html, [(tag, html),...]) — preserves EVERY top-level content element in
    order (paragraphs, lists, sub-headings, tables, blockquotes); nothing is dropped.
    head = a leading <h1>/<h2> (the section heading carried onto the first row)."""
    head = ""
    m = re.match(r'\s*(<h[12]\b[^>]*>.*?</h[12]>)\s*', html, re.S)
    if m:
        head, html = m.group(1), html[m.end():]
    return head, [(t.lower(), full) for full, t in re.findall(r'(<(\w+)\b[^>]*>.*?</\2>)', html, re.S)]

def _split_row(inner_html, photo, reverse=False, bg="bg-white", contain=False, obj_pos="center", square=False):
    """Tight text+image row. The image is ABSOLUTELY positioned inside a relative box,
    so it never pushes the row taller than the text — the text sets the height and the
    photo crops to fit (no whitespace, ever). Sides alternate (reverse=image-left). The
    faded brand logo watermark sits behind the text side (logo-row), like the home page.
    square=True instead shows the WHOLE photo in a 1:1 framed card (object-contain over a
    blurred fill of the same image), vertically centred beside the text."""
    src = "images/photos/" + photo[0] + ".webp"
    if square:   # show the whole photo, uncropped, in a square framed card
        frame = (f'<div class="mrow-frame-sq" style="--sqimg:url(\'/{src}\')">'
                 '<span class="sq-bg" aria-hidden="true"></span>'
                 + img(src, photo[1], cls="sq-fg") + '</div>')
        side_img = "reveal-left" if reverse else "reveal-right"
        side_txt = "reveal-right" if reverse else "reveal-left"
        media = f'<div class="mrow-sq {side_img}">{frame}</div>'
        if reverse:   # image left, text right
            pic_d = f'<div class="col-span-12 lg:col-span-5 lg:col-start-1 lg:row-start-1 flex items-center">{media}</div>'
            text_d = f'<div class="mrow-text {side_txt} col-span-12 lg:col-span-6 lg:col-start-7">{inner_html}</div>'
        else:         # image right, text left
            text_d = f'<div class="mrow-text {side_txt} col-span-12 lg:col-span-6 lg:col-start-1">{inner_html}</div>'
            pic_d = f'<div class="col-span-12 lg:col-span-5 lg:col-start-8 flex items-center">{media}</div>'
        return section(f'<div class="grid grid-cols-12 gap-7 lg:gap-12 items-center">{text_d}{pic_d}</div>',
                       bg=bg, pad="pt-8 lg:pt-14 pb-8 lg:pb-14", extra="logo-row overflow-hidden")
    # Default: show the WHOLE photo at its natural aspect (never cropped), in a white frame that
    # fits the image. Row is TOP-aligned so the H2 sits level with the top of the photo.
    icls = "mrow-img mrow-img--contain" if contain else "mrow-img"
    frame = f'<div class="mrow-frame{" mrow-frame--pad" if contain else ""}">{img(src, photo[1], cls=icls)}</div>'
    side_img = "reveal-left" if reverse else "reveal-right"
    side_txt = "reveal-right" if reverse else "reveal-left"
    media = f'<div class="mrow-media {side_img}">{frame}</div>'
    if reverse:   # image left, text right
        pic_d = f'<div class="mrow-pic col-span-12 lg:col-span-5 lg:col-start-1 lg:row-start-1 flex items-start justify-center">{media}</div>'
        text_d = f'<div class="mrow-text {side_txt} col-span-12 lg:col-span-6 lg:col-start-7">{inner_html}</div>'
    else:         # image right, text left
        text_d = f'<div class="mrow-text {side_txt} col-span-12 lg:col-span-6 lg:col-start-1">{inner_html}</div>'
        pic_d = f'<div class="mrow-pic col-span-12 lg:col-span-5 lg:col-start-8 flex items-start justify-center">{media}</div>'
    return section(f'<div class="grid grid-cols-12 gap-7 lg:gap-12 items-start">{text_d}{pic_d}</div>',
                   bg=bg, pad="pt-8 lg:pt-14 pb-8 lg:pb-14", extra="logo-row overflow-hidden")

def media_rows(inner_html, seed, bg="bg-white", used=None, group=2, force=None, force_contain=False, force_pos=None, pins=None, square=False, topic=None, prefer=None):
    """Site rule: a 2+ paragraph block is broken into tight text+image rows (`group`
    paragraphs each); each image is TOPIC-MATCHED to its paragraph (match_photo), crops
    to the text height (no whitespace), and sides alternate. Pass a shared `used` set to
    stop a page repeating photos. `bg` may be a callable or a string.
    square=True shows each photo whole in a 1:1 framed card (never cropped). `topic` (e.g.
    the page's service name) biases every row's photo match toward the page subject."""
    if used is None:
        used = set()
    head, blocks = _para_blocks(inner_html)
    if callable(bg):
        nextbg = bg
    else:
        _c = {"n": 0 if bg != "bg-beige" else 1}
        def nextbg():
            v = "bg-white" if _c["n"] % 2 == 0 else "bg-beige"
            _c["n"] += 1
            return v
    if not blocks:
        return section(prose(inner_html), bg=nextbg())
    # Group blocks into rows: a sub-heading (<h3>/<h4>) starts a new row; otherwise pack up
    # to `group` paragraphs. Every non-paragraph element rides along, so nothing is dropped.
    groups, cur, pc = [], [], 0
    for tag, full in blocks:
        if cur and (tag in ("h3", "h4") or (tag == "p" and pc >= group)):
            groups.append(cur); cur, pc = [], 0
        cur.append(full)
        if tag == "p":
            pc += 1
    if cur:
        groups.append(cur)
    if len(groups) >= 2 and len(groups[-1]) == 1:      # don't strand a lone trailing block
        last = groups.pop(); groups[-1] += last
    rows = []
    for gi, g in enumerate(groups):
        body = (head if gi == 0 else "") + "".join(g)
        if gi == 0 and force:                          # pinned image for the first row
            photo = force
        elif pins and gi in pins:                      # pinned image for a specific row: (file, alt[, obj_pos])
            photo = pins[gi]
        else:
            # The photo beside an H2 must be about THAT H2 mainly, then the page title, then the
            # surrounding copy. We weight the heading 4×, the page subject 2×, the body 1×, and
            # rotate among the top matches with a per-(page,row) salt so pages aren't templated.
            rsalt = f"{seed}-{gi}"
            _hm = re.search(r"<h[2-4][^>]*>(.*?)</h[2-4]>", body, re.S | re.I)
            heading = _strip_tags(_hm.group(1)) if _hm else ""
            mtext = (heading + " ") * 4 + ((topic + " ") * 2 if topic else "") + body
            # topn=4: pick from only the 4 closest matches — tight enough that the photo stays
            # about the heading, loose enough that different pages don't all land on the same one.
            photo = match_photo(mtext, used, salt=rsalt, prefer=prefer, topn=4)
            if photo is None and topic:                # thin paragraph: fall back to page subject
                photo = match_photo(heading + " " + topic, used, salt=rsalt + "-t", prefer=prefer)
            if photo is None:                          # no word overlap: pick an unused (preferred) photo
                cands = [p for p in PHOTOS if p[0] not in used and p[0] != QUOTE_BAND_PHOTO
                         and (not prefer or p[0] in prefer)]
                if cands:
                    photo = cands[int(hashlib.md5((rsalt + "-f").encode()).hexdigest(), 16) % len(cands)]
                else:
                    photo = next((p for p in page_photos(f"{seed}-{gi}", 16) if p[0] not in used),
                                 page_photos(seed, 1)[0])
        used.add(photo[0])
        rbg = nextbg()   # side tracks the (already-alternating) bg, so consecutive rows flip sides
        _pos = "center"
        if gi == 0 and force and force_pos:
            _pos = force_pos
        elif pins and gi in pins and len(pins[gi]) > 2:
            _pos = pins[gi][2]
        rows.append(_split_row(body, photo, reverse=(rbg == "bg-beige"), bg=rbg,
                               contain=(gi == 0 and bool(force) and force_contain), obj_pos=_pos, square=square))
    return "\n".join(rows)

def media_body(html, seed, bg="bg-white", used=None, group=2, span="lg:col-span-10 lg:col-start-2"):
    """Render a full body (one or more <h2> sections), applying the split rule per
    section: 2+ paragraphs -> topic-matched media rows; otherwise a single prose section
    with the logo watermark. bg + image-side alternation stays continuous across sections."""
    if used is None:
        used = set()
    if callable(bg):
        nextbg = bg
    else:
        _c = {"n": 0 if bg != "bg-beige" else 1}
        def nextbg():
            v = "bg-white" if _c["n"] % 2 == 0 else "bg-beige"
            _c["n"] += 1
            return v
    chunks = [c.strip() for c in re.split(r'(?=<h2)', html) if c.strip()] or [html]
    out = []
    for ci, chunk in enumerate(chunks):
        if chunk.count("<p") >= 2:
            out.append(media_rows(chunk, f"{seed}-{ci}", nextbg, used=used, group=group))
        else:
            out.append(section(prose(chunk, span=span), bg=nextbg(), extra="logo-row overflow-hidden"))
    return "\n".join(out)

def map_embed(query, title, cls="", zoom=10):
    """No-key Google Maps area embed (frame-src www.google.com is allow-listed in _headers).
    items-stretch + h-full lets it match the height of the text beside it. `query` like
    'Ipswich, Suffolk, UK'; lower `zoom` for wider county views."""
    from urllib.parse import quote as _q
    src = f"https://www.google.com/maps?q={_q(query)}&z={zoom}&output=embed"
    return (f'<div class="rounded-xl overflow-hidden shadow-custom border border-border '
            f'h-72 sm:h-80 lg:h-full lg:min-h-[20rem] {cls}">'
            f'<iframe title="Map of {esc(title)} — area {esc(S.BUSINESS["name"])} covers" src="{src}" '
            'width="100%" height="100%" style="border:0;display:block" loading="lazy" '
            'referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>')

FP_STATS = [
    ("clock", "Since 2005", "Family-run firm"),
    ("shield", "Fully covered", "Basil Fry cover"),
    ("van", "Euro 6 fleet", "Clean &amp; modern"),
    ("pin", "All of Suffolk", "Ipswich-based"),
]

def feature_panel(heading_html, body_html, photo, reverse=False, bg="bg-white", with_cta=True):
    """Advanced navy feature card: kicker + heading + body, a framed photo with a floating
    'Est. 2005' badge, a 4-stat trust strip and CTA. Image/content slide in on scroll."""
    b = S.BUSINESS
    est = b.get("founded", "2005")
    media = (
        '<div class="fp-media reveal-left">'
        '<div class="fp-media-img">'
        f'{img("images/photos/" + photo[0] + ".webp", photo[1], cls="w-full h-full object-cover")}'
        f'<div class="fp-badge"><span class="fp-badge-k">Est.</span><span class="fp-badge-y">{esc(est)}</span></div>'
        '</div>'
        '<span class="fp-spark" aria-hidden="true"></span>'
        '</div>')
    stats = "".join(
        f'<div class="fp-stat"><span class="fp-stat-ico">{_picto(k)}</span>'
        f'<span class="fp-stat-t"><strong>{t}</strong><span>{s}</span></span></div>'
        for k, t, s in FP_STATS)
    cta_html = ""
    if with_cta:
        cta_html = (
            '<div class="fp-cta">'
            '<a href="/get-a-quote/" class="button-orange">Get a Free Quote</a>'
            f'<a href="{b["phone_link"]}" class="fp-call" aria-label="Call {esc(b["name"])} on {b["phone"]}">'
            f'{icon("phone","w-5 h-5")}{b["phone"]}</a>'
            '</div>')
    content = (
        '<div class="feature-panel fp-content reveal-right">'
        '<span class="fp-kicker">Ipswich &amp; Suffolk &middot; Since ' + esc(est) + '</span>'
        f'{heading_html}{body_html}'
        f'<div class="fp-stats">{stats}</div>'
        f'{cta_html}</div>')
    return section(
        '<div class="grid grid-cols-12"><div class="col-span-12 lg:col-span-10 lg:col-start-2">'
        f'<div class="fp-card{" fp--rev" if reverse else ""}">'
        f'<div class="fp-grid">{media}{content}</div>'
        '</div></div></div>', bg=bg)

def standard_feature_panel(photo, reverse=False, bg="bg-white", name=None):
    """Standard slate feature panel for pages without their own feature section.
    `name` makes the heading a UNIQUE, page-specific <h2> (e.g. on service pages); without
    it the heading is a styled non-heading (recurring trust block) so it doesn't create a
    duplicate <h2> across the many generic pages that use this panel."""
    if name:
        heading = f'<h2 class="relative leading-tight">Why Move With Orwell Removals &amp; Storage for {esc(name)}?</h2>'
    else:
        heading = ('<div class="relative leading-tight font-bold uppercase text-3xl 2xl:text-4xl mb-4">'
                   'Why Move With Orwell Removals &amp; Storage?</div>')
    body = (
        '<p>We&rsquo;re a friendly, family-run Ipswich removals and storage company that has been moving Suffolk '
        'households and businesses since 2005. From a single item to a full home or office move, every job is fully '
        'covered and looked after by the same team from your first call to the last box, so you always know who you&rsquo;re dealing with.</p>'
        '<p>Every move is <strong>fully covered</strong> and our modern <strong>Euro&nbsp;6 fleet</strong> '
        'keeps it clean and efficient. We handle it all with real care &mdash; expert '
        '<a href="/services/packing-service/">packing</a>, '
        '<a href="/services/home-removals/">home</a> and <a href="/services/commercial-removals/">business removals</a>, '
        'safe <a href="/services/piano-removals/">piano moves</a> and clean, secure '
        '<a href="/services/storage/">storage</a> right across Ipswich and Suffolk.</p>')
    return feature_panel(heading, body, photo, reverse=reverse, bg=bg, with_cta=True)

# Shared trust strip. Orwell has real, verifiable credentials (NOT BAR, no estate-agent
# logo partnerships) — render them as honest text/icon "chips" so there are no missing
# logo files. ONE source of truth so it's identical on every page it appears.
TRUST_CHIPS = [
    ("Fully Covered", "Goods-in-transit & liability cover via Basil Fry"),
    ("Family-Run Since 2005", "Moving Ipswich & Suffolk for two decades"),
    ("Euro 6 Fleet", "Modern, low-emission removal vans & lorries"),
    ("Free Home Survey", "No-obligation quotes across the whole of Suffolk"),
    ("Local Ipswich Team", "Based at Old Station Works, Westerfield"),
]

def trusted_by(bg=None):
    """The shared accreditation / trust strip — a navy brand band (strong contrast anchor on
    every page). `bg` is kept for backwards-compatibility but ignored; the band is always navy."""
    check = ('<svg viewBox="0 0 24 24" class="w-5 h-5 shrink-0 text-orange" fill="none" stroke="currentColor" '
             'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M20 6 9 17l-5-5"/></svg>')
    chips = "".join(
        '<div class="glass-chip flex items-start gap-3 rounded-xl px-4 py-3">'
        f'{check}<div><span class="block font-semibold uppercase text-sm tracking-wide text-white">{esc(t)}</span>'
        f'<span class="block text-sm text-white/65 font-normal">{esc(d)}</span></div></div>'
        for t, d in TRUST_CHIPS)
    grid = f'<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">{chips}</div>'
    return (
        '<section class="band-navy w-full pt-8 lg:pt-16 pb-8 lg:pb-16 border-border">'
        '<div class="container">'
        '<div class="text-center mb-8">'
        '<span class="fp-kicker">Why Orwell</span>'
        '<h2 class="relative leading-tight text-white">Trusted Across Ipswich &amp; Suffolk</h2>'
        '<p class="text-lg xl:text-xl font-medium mt-2 max-w-3xl mx-auto text-white/80">Real credentials from a real '
        'local team &mdash; covered, experienced and on the road across Suffolk every day.</p></div>'
        + grid + '</div></section>')

def photo_strip(photos, heading="See Our Suffolk Movers in Action", intro=None, bg="bg-lightgrey"):
    # Build a richer, de-duplicated set so the carousel has images to scroll through.
    # Callers still pass ~3; we top up deterministically (seeded on the heading) to 7.
    pics, seen = [], set()
    for p in list(photos) + page_photos(heading or "gallery", len(PHOTOS)):
        if p[0] in seen or p[0] == QUOTE_BAND_PHOTO:
            continue
        pics.append(p); seen.add(p[0])
        if len(pics) >= 7:
            break
    slides = "".join(
        f'<figure class="pstrip-slide"><div class="pstrip-frame">{photo_block(p)}</div></figure>'
        for p in pics)
    arrow = lambda d, lbl, path: (
        f'<button type="button" class="pstrip-arrow pstrip-{d}" aria-label="{lbl}">'
        f'<svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true">'
        f'<path fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" '
        f'stroke-linejoin="round" d="{path}"/></svg></button>')
    arrows = (arrow("prev", "Show previous photos", "M15 5l-7 7 7 7")
              + arrow("next", "Show more photos", "M9 5l7 7-7 7"))
    head = ""
    if heading:
        head = f'<div class="text-center mb-8"><h2 class="relative leading-tight text-black">{esc(heading)}</h2>'
        head += (f'<p class="text-lg xl:text-xl font-medium mt-2 max-w-3xl mx-auto">{intro}</p>' if intro else "") + "</div>"
    carousel = (f'<div class="pstrip" data-carousel>'
                f'<div class="pstrip-track" role="group" aria-label="{esc(heading or "Photo gallery")}">{slides}</div>'
                f'{arrows}</div>')
    return section(head + carousel, bg=bg)

def photo_gallery(photos, heading=None, intro=None, bg="bg-white"):
    """Centre-focused scrolling carousel (reuses the pstrip styling + photo-carousel.js):
    a horizontal scroll-snap gallery where the middle slide sits 50% larger than its
    neighbours. Shows EVERY photo passed (no 7-image cap) — used for the full antique set."""
    seen, pics = set(), []
    for p in photos:
        if not p or p[0] in seen or p[0] == QUOTE_BAND_PHOTO:
            continue
        seen.add(p[0]); pics.append(p)
    if not pics:
        return ""
    slides = "".join(
        f'<figure class="pstrip-slide"><div class="pstrip-frame">{photo_block(p)}</div></figure>'
        for p in pics)
    arrow = lambda d, lbl, path: (
        f'<button type="button" class="pstrip-arrow pstrip-{d}" aria-label="{lbl}">'
        f'<svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true">'
        f'<path fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" '
        f'stroke-linejoin="round" d="{path}"/></svg></button>')
    arrows = (arrow("prev", "Show previous photos", "M15 5l-7 7 7 7")
              + arrow("next", "Show more photos", "M9 5l7 7-7 7"))
    head = ""
    if heading:
        head = (f'<div class="text-center mb-8"><h2 class="relative leading-tight text-black">{esc(heading)}</h2>'
                + (f'<p class="text-lg xl:text-xl font-medium mt-2 max-w-3xl mx-auto">{intro}</p>' if intro else "")
                + "</div>")
    carousel = (f'<div class="pstrip" data-carousel>'
                f'<div class="pstrip-track" role="group" aria-label="{esc(heading or "Antiques gallery")}">{slides}</div>'
                f'{arrows}</div>')
    return section(head + carousel, bg=bg)

# ---- site-wide quote band (photo background + inline enquiry form) ----
FORM_ENDPOINT = "/api/quote"   # TODO: Cloudflare Worker -> Resend (needs key + verified sender)
QUOTE_BAND_PHOTO = "orwell-lorry-loading-on-street"

def _qfield(name, placeholder, typ="text", required=False, half=True):
    req = ' required aria-required="true"' if required else ""
    col = "md:col-span-6" if half else "md:col-span-12"
    return (f'<div class="col-span-12 {col}">'
            f'<input class="w-full" type="{typ}" name="{name}" placeholder="{esc(placeholder)}" '
            f'aria-label="{esc(placeholder.rstrip("*"))}"{req}></div>')

def _contact_item(ic, label, value, href):
    return (f'<li><a class="qcontact" href="{href}">'
            f'<span class="qcontact-ico">{icon(ic, "w-5 h-5")}</span>'
            f'<span class="qcontact-t"><span class="qcontact-k">{esc(label)}</span>'
            f'<span class="qcontact-v">{esc(value)}</span></span></a></li>')

def quote_band():
    b = S.BUSINESS
    bg = img("images/photos/" + QUOTE_BAND_PHOTO + ".webp",
             "Orwell Removals & Storage team loading a removal van in Ipswich", cls="w-full h-full object-cover")
    checks = "".join(
        f'<label class="eopt"><input type="checkbox" name="enquiry" value="{esc(v)}">'
        f'<span class="eopt-tick"></span><span>{esc(v)}</span></label>'
        for v in ["Sales / New quotation", "General Enquiry"])
    arrow = ('<svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.4" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
    contacts = (
        '<ul class="qcontacts list-none p-0 m-0">'
        + _contact_item("phone", "Call us", b["phone"], b["phone_link"])
        + _contact_item("mail", "Email us", b["email"], "mailto:" + b["email"])
        + '</ul>')
    ticks = "".join(
        f'<li>{icon("check-bold","w-4 h-4")}<span>{t}</span></li>'
        for t in ["Free, no-obligation home survey", "Fully covered &amp; family-run", "Friendly local team since 2005"])
    form = (
        f'<form class="enquiry-form" method="post" action="{FORM_ENDPOINT}" novalidate>'
        '<div class="mb-5"><h3 class="text-xl xl:text-2xl font-bold text-black leading-tight mb-1">Request your free quote</h3>'
        '<p class="text-darkgrey text-sm normal-case mb-0">Fast response &mdash; usually the same working day.</p></div>'
        '<div class="grid grid-cols-12 gap-4">'
        + _qfield("first_name", "First Name*", required=True)
        + _qfield("last_name", "Last Name*", required=True)
        + _qfield("email", "Email*", typ="email", required=True)
        + _qfield("phone", "Phone", typ="tel")
        + '<div class="col-span-12"><span class="block font-semibold mb-2 text-black normal-case">Nature of enquiry <span class="text-blue">*</span></span>'
          f'<div class="flex flex-wrap gap-3">{checks}</div></div>'
        + '<div class="col-span-12"><textarea class="w-full" name="message" rows="4" placeholder="Tell us about your move (rooms, dates, addresses)" aria-label="Message"></textarea></div>'
        + '<div class="col-span-12 hidden" aria-hidden="true"><label>Leave blank<input type="text" name="company" tabindex="-1" autocomplete="off"></label></div>'
        + '<div class="col-span-12"><button type="submit" class="button-orange w-full justify-center inline-flex items-center gap-2">Send My Enquiry ' + arrow + '</button>'
          '<p class="mt-3 text-xs text-darkgrey mb-0 normal-case">By submitting this form you agree to our <a href="/privacy-policy/">privacy policy</a>. '
          'We&rsquo;ll only use your details to respond to your enquiry.</p></div>'
        '</div></form>')
    return (
        '<section id="quote" class="relative w-full overflow-hidden bg-darkgrey text-white">'
        f'<div class="absolute inset-0">{bg}</div>'
        '<div class="absolute inset-0 quote-overlay"></div>'
        '<div class="container relative z-10 py-12 lg:py-20"><div class="grid grid-cols-12 gap-8 lg:gap-14 items-center">'
        '<div class="col-span-12 lg:col-span-5 reveal-left">'
        '<span class="fp-kicker">Free, no-obligation quote</span>'
        '<h2 class="text-white leading-tight"><span class="bg-green text-white px-2 box-decoration-clone">Interested</span> in Our Services? Get In Touch</h2>'
        '<p class="mt-4 text-lg xl:text-xl text-white/90 normal-case">Fill in the form, call us or email us and a friendly member of our team will be straight back to you.</p>'
        f'{contacts}'
        f'<ul class="qticks list-none p-0 m-0">{ticks}</ul>'
        '</div>'
        '<div class="col-span-12 lg:col-span-7 reveal-right"><div class="enquiry-card bg-white rounded-2xl shadow-2xl p-6 lg:p-9 text-black">'
        f'{form}</div></div>'
        '</div></div></section>')

# ---- sticky floating action buttons (quote / call) ----
def fabs():
    # Two sticky action buttons: "Free Quote" bottom-left, "Call Us" bottom-right.
    b = S.BUSINESS
    quote = (f'<a href="/get-a-quote/" class="fab fab-quote" aria-label="Get a free removals quote from {esc(b["name"])}">'
             f'{icon("mail","")}<span class="fab-label">Free Quote</span></a>')
    call = (f'<a href="{b["phone_link"]}" class="fab" style="right:1rem;background:#254063;color:#fff" '
            f'aria-label="Call {esc(b["name"])} on {b["phone"]}">'
            f'{icon("phone","")}<span class="fab-label">Call Us</span></a>')
    return quote + call

# ---------------------------------------------------------------- HEAD
def head_html(title, description, canonical_path, og_image=None, robots="index, follow",
              extra_head="", schema=None):
    canonical = abs_url(canonical_path)
    desc = _clip(description, 145)              # bible: meta description <=145 chars
    og_img = abs_url(og_image) if og_image else abs_url("images/brand/orwell-removals-logo.png")
    parts = [
        "<!doctype html>",
        '<html lang="en-GB" class="scroll-smooth">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        # Security headers as meta (mirrors /_headers; covers hosts like GitHub Pages that
        # ignore /_headers). frame-ancestors is header-only (ignored in meta) so it's omitted here.
        ('<meta http-equiv="Content-Security-Policy" content="'
         "default-src 'self'; img-src 'self' data: https:; "
         "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
         "style-src 'self' 'unsafe-inline'; "
         "font-src 'self' data:; "
         "connect-src 'self'; "
         "frame-src https://www.google.com; "
         "form-action 'self'; base-uri 'self'"
         '">'),
        '<meta name="referrer" content="strict-origin-when-cross-origin">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        f'<meta name="robots" content="{robots}">',
        f'<link rel="canonical" href="{canonical}">',
        # Open Graph
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="en_GB">',
        f'<meta property="og:site_name" content="{esc(S.BUSINESS["name"])}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:image" content="{og_img}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
        f'<meta name="twitter:image" content="{og_img}">',
        '<meta name="theme-color" content="#254063">',
        # icons
        '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">',
        '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">',
        '<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">',
        '<link rel="manifest" href="/site.webmanifest">',
        # fonts (preload Barlow)
    ]
    for w in ("Regular", "Medium", "Semibold", "Bold"):
        parts.append(f'<link rel="preload" href="/fonts/Barlow-{w}.woff2" as="font" type="font/woff2" crossorigin>')
    if og_image:
        _ogrel = og_image.lstrip("/")
        _o800 = (_ogrel[:-5] + "-800.webp") if _ogrel.endswith(".webp") else ""
        if _o800 and os.path.exists(os.path.join(S.ROOT, _o800)):
            _ow, _ = _dims(os.path.join(S.ROOT, _ogrel))
            parts.append(f'<link rel="preload" as="image" imagesrcset="/{_o800} 800w, /{_ogrel} {_ow}w" '
                         'imagesizes="100vw" fetchpriority="high">')
        else:
            parts.append(f'<link rel="preload" as="image" href="{og_img}">')
    parts.append(f'<link rel="stylesheet" href="/css/site.min.css?v={ASSET_VER}">')
    if schema:
        for block in (schema if isinstance(schema, list) else [schema]):
            parts.append('<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False) + "</script>")
    if extra_head:
        parts.append(extra_head)
    parts.append("</head>")
    return "\n".join(parts)

def _font_face_css():
    faces = []
    for w, weight in (("Regular", 400), ("Medium", 500), ("Semibold", 600), ("Bold", 700)):
        faces.append(
            f"@font-face{{font-family:'Barlow';font-style:normal;font-weight:{weight};"
            f"font-display:swap;src:url('/fonts/Barlow-{w}.woff2') format('woff2');}}")
    return "<style>" + "".join(faces) + "</style>"

# ---------------------------------------------------------------- HEADER
# Nav model. type: "link" | "dropdown" (compact) | "mega" (full-width multi-column).
NAV = [
    {"label": "Services", "href": "/services/", "type": "mega", "design": "cards"},
    {"label": "Storage", "href": "/services/storage/", "type": "dropdown", "links": [
        ("Storage Overview", "/services/storage/"),
        ("Household Storage", "/services/storage/household-storage/"),
        ("Business Storage", "/services/storage/business-storage/")]},
    {"label": "Locations", "href": "/locations/", "type": "mega", "design": "loc-cards"},
    {"label": "About", "href": "/about-us/", "type": "dropdown", "links": [
        ("About Us", "/about-us/"), ("Pricing", "/pricing/"), ("Reviews", "/reviews/"),
        ("Gallery", "/gallery/"),
        ("Blog", "/blog/"), ("FAQs", "/frequently-asked-questions/")]},
    {"label": "Contact Us", "href": "/contact-us/", "type": "link"},
]

LINK_CLS = "text-black font-semibold uppercase lg:hover:text-orange text-base lg:text-sm xl:text-base"

# Bespoke "Services" mega: each item is an icon + title + one-line descriptor card.
# (title, href, pictogram-key, descriptor)
SERVICES_MEGA = [
    ("Home Removals", "/services/home-removals/", "house", "Full home moves, packed & placed"),
    ("Office Removals", "/services/office-removals/", "office", "Planned, low-downtime business moves"),
    ("Commercial Removals", "/services/commercial-removals/", "boxes", "Stock, kit & furniture, any size"),
    ("Long Distance Removals", "/services/long-distance-removals/", "globe", "Door-to-door UK relocations"),
    ("Man & Van", "/services/man-and-van/", "van", "Quick, cost-effective smaller moves"),
    ("Piano Removals", "/services/piano-removals/", "piano", "Upright & grand pianos, moved safely"),
    ("Packing Service", "/services/packing-service/", "box", "Expert packing & quality materials"),
    ("Storage", "/services/storage/", "shield", "Clean, dry, secure containers"),
]

# Bespoke "Locations" mega — same card design as Services. (town, href, pictogram, descriptor)
LOCATIONS_MEGA = [
    ("Ipswich", "/locations/ipswich-removals/", "pin", "Our home city — full home & office moves"),
    ("Bury St Edmunds", "/locations/bury-st-edmunds-removals/", "pin", "West Suffolk removals & storage"),
    ("Felixstowe", "/locations/felixstowe-removals/", "pin", "Coastal & port-town moves"),
    ("Lowestoft", "/locations/lowestoft-removals/", "pin", "East-coast removals & storage"),
    ("Woodbridge", "/locations/woodbridge-removals/", "pin", "Riverside town moves"),
    ("Stowmarket", "/locations/stowmarket-removals/", "pin", "Central Suffolk removals"),
    ("Sudbury", "/locations/sudbury-removals/", "pin", "South Suffolk home moves"),
    ("Newmarket", "/locations/newmarket-removals/", "pin", "West-edge & racing-town moves"),
    ("Haverhill", "/locations/haverhill-removals/", "pin", "South-west border-town moves"),
    ("Beccles", "/locations/beccles-removals/", "pin", "Waveney Valley removals"),
    ("Aldeburgh", "/locations/aldeburgh-removals/", "pin", "Heritage-coast moves & storage"),
    ("Framlingham", "/locations/framlingham-removals/", "pin", "Market-town home moves"),
    ("Hadleigh", "/locations/hadleigh-removals/", "pin", "Babergh-area removals"),
    ("Needham Market", "/locations/needham-market-removals/", "pin", "Mid-Suffolk moves"),
    ("Saxmundham", "/locations/saxmundham-removals/", "pin", "East-Suffolk removals"),
    ("Southwold", "/locations/southwold-removals/", "pin", "Seaside-town moves & storage"),
]

def _picto(key, cls="mega-ico-svg"):
    p = PICTOGRAMS.get(key, PICTOGRAMS["box"])
    return f'<svg viewBox="0 0 24 24" class="{cls}" fill="currentColor" aria-hidden="true">{p}</svg>'

def _toplink(label, href):
    return f'<a href="{href}" class="nav-top shrink-0 {LINK_CLS}">{esc(label)}</a>'

def _mega_promo():
    """Navy promo card shown on the right of the Services mega — survey + quote CTA."""
    b = S.BUSINESS
    return (
        '<div class="mega-promo h-full">'
        '<span class="mp-k">First Impressions Count</span>'
        '<span class="mp-h">Book a free home survey</span>'
        '<span class="mp-p">Tell us what you&rsquo;re moving and we&rsquo;ll give you a clear, no-obligation quote across Ipswich &amp; Suffolk.</span>'
        f'<a class="mp-call mt-2" href="{b["phone_link"]}" aria-label="Call {esc(b["name"])} on {b["phone"]}">'
        f'{icon("phone","w-5 h-5")}<span>{b["phone"]}</span></a>'
        '<a class="button-orange mt-2 w-fit" href="/get-a-quote/">Get a Free Quote</a>'
        '</div>')

def _mega_col(title, churl, links):
    """A column of town/area links (Locations mega)."""
    t_esc = esc(title)
    pin = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' + PICTOGRAMS["pin"] + '</svg>'
    if churl:
        title_html = f'<a href="{churl}" class="nav-top font-bold text-base lg:text-lg text-black hover:text-orange">{t_esc}</a>'
    else:
        title_html = f'<span class="font-bold text-base lg:text-lg text-darkgrey">{t_esc}</span>'
    chev = icon("chevron", "h-4 w-4 fill-current")
    lis = "".join(f'<li><a href="{h}" class="mega-town">{pin}<span>{esc(t)}</span></a></li>' for t, h in links)
    return (
        '<div x-data="{c:false}" class="border-b border-black/10 pb-2 mb-1 lg:border-0 lg:pb-0 lg:mb-0">'
        '<div class="flex items-center justify-between gap-2 lg:mb-2 lg:pb-2 lg:border-b lg:border-border">'
        f'{title_html}'
        f'<button type="button" @click="c=!c" :class="c?\'rotate-180\':\'\'" '
        f'class="lg:hidden p-2 -mr-2 bg-transparent transition-transform duration-200" aria-label="Toggle {t_esc}">{chev}</button>'
        '</div>'
        f'<ul class="mega-sublist list-none p-0 m-0 space-y-px pt-1 pb-2 lg:pt-0 lg:pb-0" x-show="c" x-cloak>{lis}</ul>'
        '</div>')

def _loc_promo():
    """Navy promo card shown on the right of the Locations mega."""
    b = S.BUSINESS
    return (
        '<div class="mega-promo h-full">'
        '<span class="mp-k">Across All of Suffolk</span>'
        '<span class="mp-h">Don&rsquo;t see your town?</span>'
        '<span class="mp-p">We move homes &amp; businesses right across the county &mdash; from the coast to the west-Suffolk border. Just ask.</span>'
        f'<a class="mp-call mt-2" href="{b["phone_link"]}" aria-label="Call {esc(b["name"])} on {b["phone"]}">'
        f'{icon("phone","w-5 h-5")}<span>{b["phone"]}</span></a>'
        '<a class="button-orange mt-2 w-fit" href="/locations/">View All Areas</a>'
        '</div>')

def _mega_cards(items, promo, left_grid="grid-cols-1 sm:grid-cols-2"):
    """Shared bespoke mega body: icon + title + descriptor cards beside a navy promo.
    Used by BOTH the Services and Locations menus so they share one design."""
    cards = "".join(
        f'<a href="{href}" class="mega-card">'
        f'<span class="mega-ico">{_picto(key, cls="")}</span>'
        f'<span class="mega-tt"><span class="mega-tt-title">{esc(title)}</span>'
        f'<span class="mega-tt-desc">{esc(desc)}</span></span></a>'
        for title, href, key, desc in items)
    return (
        '<div class="grid grid-cols-1 lg:grid-cols-12 gap-5 lg:gap-7 items-stretch">'
        f'<div class="lg:col-span-8 grid {left_grid} gap-2">{cards}</div>'
        f'<div class="lg:col-span-4">{promo}</div>'
        '</div>')

def _nav_items():
    li_base = "lg:h-full w-full lg:w-auto flex items-center lg:pr-4 xl:pr-5 2xl:pr-7 border-b border-black/10 lg:border-b-0"
    out = []
    for it in NAV:
        t, label, href = it["type"], it["label"], it["href"]
        if t == "link":
            out.append(f'<li class="{li_base} px-4 py-3 lg:p-0 lg:py-10">{_toplink(label, href)}</li>')
            continue
        trigger = (f'<div class="flex items-center w-full lg:w-auto justify-between px-4 lg:p-0 py-3 lg:py-0">'
                   f'{_toplink(label, href)}'
                   f'<button type="button" aria-label="Open {esc(label)} menu" @click="o=!o" '
                   f'class="nav-top lg:ml-1 p-1 bg-transparent transition-transform duration-200" :class="o?\'rotate-180\':\'\'">'
                   f'{icon("chevron","h-5 w-5 fill-current")}</button></div>')
        if t == "dropdown":
            links = "".join(f'<li><a href="{h}" class="nav-dd-link">{esc(lt)}</a></li>' for lt, h in it["links"])
            panel = (f'<ul x-cloak class="nav-panel bg-white w-full px-2 py-2 lg:absolute lg:top-full lg:left-0 lg:w-72 lg:z-30 '
                     f'list-none my-0 lg:py-2 lg:px-1" '
                     f':class="o ? \'block\' : \'hidden\'">{links}</ul>')
        elif it.get("design") in ("cards", "loc-cards"):  # bespoke mega (Services / Locations share one design)
            if it["design"] == "loc-cards":
                body = _mega_cards(LOCATIONS_MEGA, _loc_promo(), "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3")
            else:
                body = _mega_cards(SERVICES_MEGA, _mega_promo(), "grid-cols-1 sm:grid-cols-2")
            panel = (f'<div x-cloak class="nav-panel bg-white w-full lg:absolute lg:left-0 lg:right-0 lg:top-full lg:z-30" '
                     f':class="o ? \'block\' : \'hidden\'">'
                     f'<div class="px-5 py-4 lg:px-0 lg:py-8 lg:container">{body}</div></div>')
        else:  # legacy column mega (fallback; no nav item uses this now)
            cols = "".join(_mega_col(ct, cu, cl) for ct, cu, cl in it.get("cols", []))
            grid = it.get("grid", "grid-cols-1 md:grid-cols-2 lg:grid-cols-4")
            _m = re.search(r"lg:grid-cols-\d+", grid)
            grid_m = "grid-cols-1 " + (_m.group(0) if _m else "lg:grid-cols-4")
            panel = (f'<div x-cloak class="nav-panel bg-white w-full lg:absolute lg:left-0 lg:right-0 lg:top-full lg:z-30" '
                     f':class="o ? \'block\' : \'hidden\'">'
                     f'<div class="px-5 py-4 lg:px-0 lg:py-8 lg:container"><div class="grid {grid_m} gap-x-10 gap-y-5">{cols}</div></div></div>')
        pos = "lg:relative " if t == "dropdown" else ""   # mega panels span full header width
        # Desktop hover with a short close-delay: crossing the gap between the
        # trigger and the panel (or moving diagonally to a far column) starts a
        # 250ms timer; re-entering the <li> subtree (which includes the panel,
        # a DOM child) cancels it, so the menu no longer vanishes mid-select.
        out.append(
            f'<li class="{pos}{li_base} flex-col lg:flex-row lg:py-10" x-data="{{o:false,t:0}}" '
            f'@mouseenter="if(window.innerWidth>=1024){{clearTimeout(t);o=true}}" '
            f'@mouseleave="if(window.innerWidth>=1024){{t=setTimeout(()=>o=false,250)}}">{trigger}{panel}</li>')
    return "\n".join(out)

def _mobile_children(it):
    """Flat link list for a top-level nav item, used by the mobile drawer accordion."""
    d = it.get("design")
    if d == "cards":
        return [("All Services", "/services/")] + [(t, h) for t, h, _k, _d in SERVICES_MEGA]
    if d == "loc-cards":
        return [("All Areas We Cover", "/locations/")] + [(t, h) for t, h, _k, _d in LOCATIONS_MEGA]
    if it["type"] == "dropdown":
        return list(it["links"])
    return []

def _mobile_nav():
    """Bespoke mobile drawer: a clean accordion (tap label to go, chevron to expand)."""
    b = S.BUSINESS
    arrow = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>')
    rows = []
    for it in NAV:
        label, href = it["label"], it["href"]
        kids = _mobile_children(it)
        if not kids:
            rows.append(f'<div class="mnav-item"><div class="mnav-row"><a class="mnav-link" href="{href}">{esc(label)}</a></div></div>')
            continue
        sub = "".join(f'<a class="mnav-sublink" href="{h}">{arrow}<span>{esc(lt)}</span></a>' for lt, h in kids)
        rows.append(
            '<div class="mnav-item" x-data="{o:false}">'
            '<div class="mnav-row">'
            f'<a class="mnav-link" href="{href}">{esc(label)}</a>'
            f'<button type="button" class="mnav-toggle" @click="o=!o" :aria-expanded="o" aria-label="Show {esc(label)} links">'
            f'<span class="transition-transform duration-200" :class="o&&\'rotate-90\'">{arrow}</span></button>'
            '</div>'
            f'<div class="mnav-sub" x-show="o" x-cloak x-transition>{sub}</div>'
            '</div>')
    foot = (
        '<div class="mnav-foot">'
        '<a class="button-orange nav-cta w-full justify-center" href="/get-a-quote/">Get a Free Quote</a>'
        f'<a class="mnav-call" href="{b["phone_link"]}" aria-label="Call {esc(b["name"])} on {b["phone"]}">'
        f'{icon("phone","w-5 h-5")}<span>Call {b["phone"]}</span></a>'
        f'<a class="mnav-email" href="mailto:{b["email"]}">{icon("mail","w-4 h-4")}<span>{b["email"]}</span></a>'
        '</div>')
    return '<div class="mnav">' + "".join(rows) + foot + '</div>'

def header_html(active=""):
    b = S.BUSINESS
    nav = _nav_items()
    mob = _mobile_nav()
    return f'''<header id="header" class="h-[76px] sm:h-[84px] md:h-[84px] lg:h-[100px] xl:h-[104px] 2xl:h-[104px]">
  <div id="inner-header" class="bg-white z-50 w-full fixed shadow-custom-header">
    <div class="container mx-auto h-full">
      <div id="top-header" class="flex items-center h-full justify-between gap-3 lg:gap-4 xl:gap-8">
        <div id="logo" class="order-1 relative shrink-0 w-[150px] sm:w-[185px] lg:w-[230px] xl:w-[250px] z-50">
          <a id="site-logo" class="absolute left-0 top-1/2 -translate-y-1/2 flex z-50" href="/" title="{b['name']}">
            <img class="h-[42px] sm:h-[50px] lg:h-[66px] xl:h-[72px] w-auto drop-shadow" src="/images/brand/orwell-removals-logo.png" width="864" height="308" alt="{b['name']} logo" />
          </a>
        </div>
        <div class="order-2 hidden lg:flex lg:flex-1 items-center justify-end gap-4 xl:gap-6">
          <nav id="site-navigation" aria-label="Primary" class="font-medium">
            <ul class="flex lg:flex-row lg:items-center lg:justify-end p-0 mb-0 list-none">{nav}</ul>
          </nav>
          <a class="button-orange nav-cta shrink-0 whitespace-nowrap lg:px-8 xl:px-12" href="/get-a-quote/">Get a Free Quote</a>
        </div>
        <div class="order-3 w-fit flex lg:hidden items-center justify-end gap-2">
          <a class="flex items-center justify-center w-11 h-11 rounded-full bg-green text-white" href="{b['phone_link']}" aria-label="Call {b['phone']}">{icon('phone','w-5 h-5')}</a>
          <button type="button" aria-label="Open menu" @click="menuOpen=!menuOpen" class="flex items-center justify-center w-11 h-11 rounded-full bg-darkgreen text-white" :aria-expanded="menuOpen">
            <svg x-show="!menuOpen" viewBox="0 0 24 24" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
            <svg x-show="menuOpen" x-cloak viewBox="0 0 24 24" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
          </button>
        </div>
      </div>
    </div>
    <div x-cloak class="mnav-drawer lg:hidden absolute top-full left-0 w-full bg-white max-h-[82vh] overflow-y-auto shadow-2xl" :class="menuOpen ? 'block' : 'hidden'">
      <nav aria-label="Mobile">{mob}</nav>
    </div>
  </div>
</header>'''

# ---------------------------------------------------------------- FOOTER
def footer_html():
    b = S.BUSINESS
    cols = []
    # contact column first
    cols.append(f'''<div class="w-1/2 md:w-1/3 lg:w-auto lg:flex-1">
      <p class="text-lg font-semibold mb-3 text-white">Contact Us</p>
      <address class="not-italic leading-relaxed">
        <strong>{esc(b['name'])}</strong><br>{esc(b['street'])}<br>{esc(b['locality'])}<br>{esc(b['region'])} {esc(b['postcode'])}
      </address>
      <p class="mt-3 flex items-center gap-2"><a class="flex items-center gap-2 text-white hover:text-orange" href="{b['phone_link']}" aria-label="Call {b['phone']}">{icon('phone','w-4 text-beige')}{b['phone']}</a></p>
      <p class="flex items-center gap-2"><a class="flex items-center gap-2 text-white hover:text-orange" href="mailto:{b['email']}" aria-label="Email {b['email']}">{icon('mail','w-4 text-beige')}{b['email']}</a></p>
      <p class="flex items-center gap-2"><a class="flex items-center gap-2 text-white hover:text-orange" href="mailto:{b['email_info']}" aria-label="Email {b['email_info']}">{icon('mail','w-4 text-beige')}{b['email_info']}</a></p>
    </div>''')
    # map column — sits beside Contact Us
    cols.append(
        '<div class="w-full sm:w-1/2 lg:w-auto">'
        '<p class="text-lg font-semibold mb-3 text-white">Find Us</p>'
        '<iframe title="Orwell Removals &amp; Storage on Google Maps" '
        'src="https://www.google.com/maps?q=Old+Station+Works,+Main+Road,+Westerfield,+Ipswich+IP6+9AB&output=embed" '
        'class="block" style="border:0;width:215px;max-width:100%;height:200px;border-radius:10px;" '
        'allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>')
    for label, links in S.footer_columns():
        lis = "".join(f'<li><a class="text-white hover:text-orange" href="{h}">{esc(t)}</a></li>' for t, h in links)
        cols.append(f'''<div class="w-1/2 md:w-1/3 lg:w-auto lg:flex-1">
      <p class="text-lg font-semibold mb-3 text-white">{esc(label)}</p>
      <ul class="list-none p-0 m-0 space-y-1">{lis}</ul></div>''')
    # Only render verified social profiles (from S.SOCIAL); never fabricate links.
    _ICO = {"facebook": ("facebook", "#1877F2"), "instagram": ("instagram-color", ""),
            "linkedin": ("linkedin", "#0A66C2"), "twitter": ("twitter", "#000000"),
            "youtube": ("youtube", "#FF0000")}
    def _sa(label, u, ic, color):
        st = f'style="color:{color}" ' if color else ''
        return (f'<a href="{u}" aria-label="{esc(b["name"])} on {label.title()}" rel="noopener nofollow" target="_blank" '
                f'{st}class="hover:opacity-80 transition-opacity">{icon(ic, "w-5 h-5")}</a>')
    social = "".join(_sa(k, u, *_ICO.get(k, ("link", ""))) for k, u in S.SOCIAL.items() if u and k in _ICO)
    return f'''<footer id="colophon" class="bg-darkgrey relative text-white">
  <div class="w-full py-10 lg:py-20">
    <div class="container">
      <div class="flex flex-wrap gap-y-6 lg:gap-8 text-base lg:text-sm xl:text-base">{''.join(cols)}</div>
    </div>
  </div>
  <div class="py-4 xl:py-6 bg-white text-black">
    <div class="container">
      <div class="flex flex-col lg:flex-row gap-4 justify-between items-center font-semibold">
        <p class="m-0">&copy; 2026 {esc(b['name'])} | {esc(b['tagline'])} UK. <a class="text-black hover:text-orange" href="/privacy-policy/">Privacy Policy</a> &middot; <a class="text-black hover:text-orange" href="/terms-conditions/">Terms</a></p>
        <div class="flex items-center gap-4 text-darkgrey">{social}</div>
      </div>
    </div>
  </div>
</footer>'''

# ---------------------------------------------------------------- SECTIONS
def section(inner, bg="bg-white", pad="pt-8 lg:pt-16 pb-8 lg:pb-16", extra=""):
    return (f'<section class="relative {bg} w-full {pad} border-border {extra}">'
            f'<div class="container">{inner}</div></section>')

def prose(html_content, center=False, span="lg:col-span-8 lg:col-start-3"):
    al = "text-center" if center else "text-left"
    return (f'<div class="grid grid-cols-12 gap-y-4 lg:gap-8">'
            f'<div class="col-span-12 {span} text-black">'
            f'<div class="{al}">{html_content}</div></div></div>')

# Self-hosted promo videos (in /videos/). name/description are PLAIN text (escaped for HTML, raw for schema).
VIDEO_META = {
    "orwell-removals-promo-b": ("Orwell Removals & Storage — Ipswich & Suffolk Removals & Storage",
        "Meet the Orwell Removals team — the people, vehicles and care behind our Suffolk moves.", "PT1M13S"),
    "orwell-removals-promo-a": ("Orwell Removals & Storage — Ipswich & Suffolk Removals & Storage",
        "A look at Orwell Removals & Storage across Ipswich and Suffolk.", "PT1M"),
    "storage-container-promo-b": ("Secure Storage with Orwell Removals & Storage",
        "Our team loading and storing mobile storage containers securely at our Suffolk depot.", "PT29S"),
    "storage-container-promo-a": ("Secure Storage with Orwell Removals & Storage",
        "Mobile storage containers loaded and stored securely by the Orwell Removals team.", "PT33S"),
    "packing-paintings-promo": ("Packing & Crating Fine Art and Paintings",
        "How our specialists wrap, pack and custom-crate paintings and antiques for safe transport.", "PT2M48S"),
    "packing-mirror-promo": ("Packing & Protecting Mirrors",
        "Wrapping and crating a large mirror for a safe, damage-free move.", "PT1M48S"),
    "packing-plates-promo": ("Expert Packing of Fragile Crockery",
        "Our team carefully wrapping and boxing fragile plates and china ready for moving.", "PT1M10S"),
    "packing-books-promo": ("Packing Books & Heavy Items",
        "Packing books safely and efficiently into the right boxes for a move.", "PT1M59S"),
    "packing-sofa-promo": ("Protecting & Moving Sofas",
        "Wrapping and moving a sofa with full furniture protection.", "PT45S"),
    "packing-wine-glasses-promo": ("Wrapping & Protecting Furniture for Transport",
        "Our team wrapping furniture in protective Furni-Soft padding ready for a safe move.", "PT25S"),
}

def video_embed(slug, bg="bg-white", heading=True, aside=None):
    """Self-hosted promo video player + VideoObject JSON-LD. Files: /videos/<slug>.mp4 + .webp.
    aside: optional write-up HTML placed BESIDE the video (vertically centred so the
    text stays within the video's height; stacks above the video on mobile). When set,
    it replaces the centred heading/description (the description still feeds the JSON-LD)."""
    name, desc, dur = VIDEO_META[slug]
    base, poster, mp4 = S.SITE_URL, f"/videos/{slug}.webp", f"/videos/{slug}.mp4"
    schema = {"@context": "https://schema.org", "@type": "VideoObject", "name": name, "description": desc,
              "thumbnailUrl": [base + poster], "contentUrl": base + mp4, "uploadDate": "2026-06-01", "duration": dur}
    # Real poster dimensions set the player's width/height (no CLS) and let portrait
    # clips render in a sensibly capped frame instead of a huge 16:9 letterbox.
    vw, vh = _dims(os.path.join(S.ROOT, "videos", f"{slug}.webp"))
    vw, vh = (vw or 1280), (vh or 720)
    # Portrait clips: cap width via inline style (a Tailwind arbitrary class like
    # max-w-[210px] would need a separate build:css recompile, so it silently no-ops).
    portrait = vh > vw
    fig_cls = "rounded-xl overflow-hidden shadow-lg bg-black" + ("" if portrait else " max-w-4xl")
    fig_style = ' style="max-width:210px"' if portrait else ""
    video_tag = (f'<video class="w-full block" controls preload="none" playsinline poster="{poster}" width="{vw}" height="{vh}">'
                 f'<source src="{mp4}" type="video/mp4">Your browser doesn&rsquo;t support embedded video.</video>')
    schema_tag = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'
    if aside:
        # Video + write-up side by side. items-center keeps the (shorter) text within
        # the video's vertical bounds — neither above nor below it; stacks on mobile.
        fig = f'<figure class="{fig_cls} mx-auto lg:mx-0 shrink-0"{fig_style}>{video_tag}</figure>'
        row = (f'<div class="flex flex-col lg:flex-row lg:items-center gap-6 lg:gap-12">'
               f'{fig}<div class="flex-1 text-left">{aside}</div></div>{schema_tag}')
        return section('<div class="grid grid-cols-12"><div class="col-span-12 lg:col-span-10 lg:col-start-2 text-black">'
                       + row + '</div></div>', bg=bg)
    head = (f'<div class="text-center mb-5"><h2 class="relative leading-tight text-black">{esc(name)}</h2></div>'
            if heading else "")
    inner = (head +
        f'<figure class="{fig_cls} mx-auto"{fig_style}>{video_tag}</figure>'
        f'<p class="text-center text-base mt-4 max-w-2xl mx-auto">{esc(desc)}</p>'
        f'{schema_tag}')
    return section(prose(inner, span="lg:col-span-10 lg:col-start-2"), bg=bg)

CCARD_VARIANTS = {1: "ccard--accent", 2: "ccard--slate", 3: "ccard--outline"}

def content_card(inner_html, variant=1, bg="bg-beige", span="lg:col-span-10 lg:col-start-2",
                 photo=None, img_side="right", img_fit="cover"):
    """A prose row lifted into a styled card panel on its (cream) background.
    `variant` 1/2/3 rotates the card treatment so cream rows are never identical.
    Pass `photo=(filename, alt)` to make a two-column photo+text card (image on
    `img_side`). `img_fit="contain"` shows the whole image on a white panel (use for
    diagrams/size guides whose edges/labels must not be cropped)."""
    vcls = CCARD_VARIANTS.get(variant, "ccard--accent")
    if photo:
        fit = "object-contain" if img_fit == "contain" else "object-cover"
        mcls = "ccard-media ccard-media--contain" if img_fit == "contain" else "ccard-media"
        # size-guide/diagram images (contain mode) load eagerly so they always show
        media = (f'<div class="{mcls}">'
                 f'{img("images/photos/" + photo[0] + ".webp", photo[1], cls="w-full h-full " + fit, eager=(img_fit == "contain"))}</div>')
        text = f'<div class="ccard-text">{inner_html}</div>'
        # text always first in DOM (mobile stacks text-above-image); desktop side set via CSS order
        body = f'<div class="ccard-split ccard-split--{esc(img_side)}">{text}{media}</div>'
        extra = " ccard--has-media"
    else:
        body, extra = inner_html, ""
    return section(
        '<div class="grid grid-cols-12">'
        f'<div class="col-span-12 {span} text-black">'
        f'<div class="ccard {vcls}{extra}">{body}</div>'
        '</div></div>', bg=bg)

def photo_flanked_row(inner_html, photos, bg="bg-white", span="lg:col-span-8 lg:col-start-3"):
    """A flat prose row with two faded, topically-relevant photos bleeding in from
    the left and right edges (fading into white). Alternates with the logo-watermark
    rows so the page isn't a repeated logo. Side photos hide on mobile."""
    lp, rp = photos[0], photos[1]
    left = f'<div class="flank-side flank-side-l" aria-hidden="true">{photo_block(lp)}</div>'
    right = f'<div class="flank-side flank-side-r" aria-hidden="true">{photo_block(rp)}</div>'
    content = (f'<div class="container">'
               f'<div class="grid grid-cols-12"><div class="col-span-12 {span} text-black">'
               f'<div class="text-left">{inner_html}</div></div></div></div>')
    tone = " flank-cream" if bg == "bg-beige" else ""
    return (f'<section class="relative {bg} w-full pt-8 lg:pt-16 pb-8 lg:pb-16 border-border overflow-hidden flank-row{tone}">'
            f'{left}{right}{content}</section>')

def rich_prose(body_html, seed, photo_budget=12):
    """Split a long prose body at its <h2> headings into the site-standard, topic-matched
    media rows (tight text+image, alternating sides, logo watermark). Delegates to
    media_body so about/pricing match the service, blog & location pages."""
    return media_body(body_html, seed, used=set(), group=2)

# Orwell has no Trustindex/embedded-widget account — and we never show another firm's
# reviews. Surface an honest, on-site review prompt that links to the /reviews/ page
# (where the genuine Checkatrade / Google links live). No fabricated ratings or counts.
_STARS = ('<span class="text-star text-xl leading-none" aria-hidden="true">★★★★★</span>')

def review_card(cls=""):
    """Disabled: no third-party review snippets anywhere on the site."""
    return ""

def hero_review_row(bullets_html=""):
    """Hero panel: just the trust bullets — no review snippet/stars."""
    return f'<div class="mt-6">{bullets_html}</div>' if bullets_html else ""

_PHOTO_MAP = {p[0]: p for p in PHOTOS}
def resolve_photo(photo):
    """Accept a (slug, alt) tuple or a slug string and return a (slug, alt) tuple."""
    if isinstance(photo, (tuple, list)):
        return photo
    return _PHOTO_MAP.get(photo) or page_photos(photo, 1)[0]

def rubik_bg(photo):
    """3x3 rubik mosaic of ONE image that flies together on load — the home-hero background,
    reused on every page hero. Tiles carry data-tile (one image sliced 9×, so they're exempt
    from image de-dup and the audit's R9 duplicate-photo rule)."""
    p = resolve_photo(photo)
    rel = "images/photos/" + p[0] + ".webp"
    src = "/" + rel
    w, h = _dims(os.path.join(S.ROOT, rel))
    # Responsive tiles: serve the 800w variant to small screens and match the <head> LCP
    # preload exactly, so the hero image downloads ONCE (no full-size + 800 double fetch).
    s800 = rel[:-5] + "-800.webp"
    srcset = (f' srcset="/{s800} 800w, {src} {w}w" sizes="100vw"'
              if w and os.path.exists(os.path.join(S.ROOT, s800)) else "")
    wh = f' width="{w or 1500}" height="{h or 1000}"'
    pieces = ""
    for r in range(3):
        for c in range(3):
            altattr = (f'alt="{esc(p[1])}"' if (r == 0 and c == 0)
                       else 'alt="" role="presentation" aria-hidden="true"')
            fp = ' fetchpriority="high"' if (r == 0 and c == 0) else ""
            pieces += (f'<div class="piece" data-r="{r}" data-c="{c}">'
                       f'<img src="{src}"{srcset}{wh} {altattr} decoding="async" loading="eager"{fp} data-tile></div>')
    return (f'<div class="absolute inset-0 rubik-hero"><div class="rubik-grid" data-rubik '
            f'role="img" aria-label="{esc(p[1])}">{pieces}</div></div>')

def hero(h1, lead, photo, kicker=None, cta=True):
    """Unified page hero — mirrors the home hero exactly: a tall band (min-h 30/36rem) with a
    single cover photo and a translucent navy panel on the right carrying the kicker, H1 and
    lead. `cta=True` adds the quote + call buttons. Used by every page so all heros match home."""
    p = resolve_photo(photo)
    k = f'<span class="fp-kicker">{esc(kicker)}</span>' if kicker else ""
    b = S.BUSINESS
    cta_html = ""
    if cta:
        arrow = ('<svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.4" '
                 'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
        cta_html = (
            '<div class="mt-7 flex flex-wrap gap-3">'
            f'<a class="button-orange inline-flex items-center gap-2" href="/get-a-quote/">Get a Free Quote {arrow}</a>'
            f'<a class="button-outline-white inline-flex items-center gap-2" href="{b["phone_link"]}">'
            f'{icon("phone","w-5 h-5")} {esc(b["phone"])}</a>'
            '</div>')
    return (
        '<section class="relative w-full bg-darkgrey text-white overflow-hidden flex items-center '
        'min-h-[30rem] lg:min-h-[36rem]">'
        f'{rubik_bg(p)}'
        '<div class="container relative z-10 w-full py-[3.6rem] lg:py-[7.2rem]"><div class="grid grid-cols-12">'
        '<div class="col-span-12 lg:col-span-7 lg:col-start-6 hero-panel">'
        f'{k}<h1 class="text-4xl lg:text-5xl font-bold leading-tight">{h1}</h1>'
        + (f'<div class="mt-4 text-lg xl:text-xl text-white/90 normal-case max-w-xl">{lead}</div>' if lead else "")
        + f'{cta_html}'
        + '</div></div></div></section>')

def make_prose_styler(seed, photos=None, span="lg:col-span-10 lg:col-start-2"):
    """Returns styled(inner_html, bg) applying the storage blueprint to prose sections:
      - cream rows -> rotating cards (variants 1/2/3); every other card carries a
        topical photo, alternating left/right;
      - white prose rows -> alternating faded logo watermark / faded side photos.
    `photos`: list of (filename, alt) relevant to the page; defaults to page_photos(seed).
    Pass photos=[] to suppress imagery (text cards + logo watermarks only) — use this on
    off-topic pages (e.g. blog) where a removals photo wouldn't match the subject."""
    pool = photos if photos is not None else page_photos(seed, 12)
    st = {"card": 0, "white": 0, "mr": 0}
    used = {pool[0][0]} if pool else set()
    def styled(inner, bg):
        if pool and inner.count("<p") >= 2:   # site rule: 2+ paragraphs -> topic-matched split media rows
            st["mr"] += 1
            return media_rows(inner, f"{seed}-mr{st['mr']}", bg, used=used, group=2)
        if bg == "bg-beige":
            i = st["card"]; st["card"] += 1
            v = (i % 3) + 1
            if pool and i % 2 == 0:
                photo = pool[i % len(pool)]
                side = "left" if (i // 2) % 2 == 1 else "right"
                return content_card(inner, variant=v, bg=bg, photo=photo, img_side=side)
            return content_card(inner, variant=v, bg=bg)
        if bg == "bg-white":
            w = st["white"]; st["white"] += 1
            if pool and w % 2 == 1:
                a = pool[(2 * w) % len(pool)]; b = pool[(2 * w + 1) % len(pool)]
                return photo_flanked_row(inner, [a, b], bg=bg)
            return section(prose(inner, span=span), bg=bg, extra="logo-row overflow-hidden")
        return section(prose(inner, span=span), bg=bg)
    return styled

# Step-process sets — same 8-card design + same icon set, relabelled per topic.
PROC_STEPS_REMOVAL = [
    ("Home Survey", "On site, online or by phone", "home-survey-clipboard", "Home survey clipboard checklist icon"),
    ("Quotation", "", "quotation-price-clipboard", "Removals quotation price clipboard icon"),
    ("Quotation Acceptance", "", "quotation-acceptance-handshake", "Quotation acceptance handshake icon"),
    ("Packing Day", "24 hrs before", "packing-day-24-hours-clock", "Packing day 24 hours clock icon"),
    ("Move Day", "", "move-day-van-calendar", "Move day removal van and calendar icon"),
    ("Unloading at New Address", "", "unloading-at-new-address-box", "Unloading boxes at the new address icon"),
    ("Placing Furniture &amp; Flatpack", "(Optional extra)", "placing-furniture-flatpack-hand", "Placing furniture and flatpack assembly icon"),
    ("Happy Customers in New Home", "", "happy-customers-new-home-family", "Happy customers in their new home icon"),
]
PROC_STEPS_PACKING = [
    ("Home Survey", "On site, online or by phone", "home-survey-clipboard", "Home survey clipboard checklist icon"),
    ("Your Packing Quote", "", "quotation-price-clipboard", "Packing quotation price clipboard icon"),
    ("Booking Confirmed", "", "quotation-acceptance-handshake", "Packing booking confirmed handshake icon"),
    ("Materials Delivered", "Boxes, wrap &amp; tape", "unloading-at-new-address-box", "Packing materials and boxes delivered icon"),
    ("Packing Day", "", "packing-day-24-hours-clock", "Professional packing day icon"),
    ("Wrapped &amp; Labelled", "", "placing-furniture-flatpack-hand", "Belongings wrapped and labelled with care icon"),
    ("Loaded &amp; Transported", "", "move-day-van-calendar", "Loaded and transported in our van icon"),
    ("Unpacked &amp; Settled", "(Optional extra)", "happy-customers-new-home-family", "Unpacked and settled into the new home icon"),
]
PROC_STEPS_STORAGE = [
    ("Home Survey", "On site, online or by phone", "home-survey-clipboard", "Home survey clipboard checklist icon"),
    ("Your Storage Quote", "", "quotation-price-clipboard", "Storage quotation price clipboard icon"),
    ("Booking Confirmed", "", "quotation-acceptance-handshake", "Storage booking confirmed handshake icon"),
    ("We Pack &amp; Collect", "", "unloading-at-new-address-box", "We pack and collect your belongings icon"),
    ("Transport to Our Store", "", "move-day-van-calendar", "Transport to our secure store icon"),
    ("Secure Containerised Storage", "", "placing-furniture-flatpack-hand", "Securely stored in containerised units icon"),
    ("Access or Long-Term", "Short or long term", "packing-day-24-hours-clock", "Access or long-term storage duration icon"),
    ("Returned When Ready", "", "happy-customers-new-home-family", "Belongings returned to you when ready icon"),
]
_PROC_INTRO = {
    "removal": ("Whether you&rsquo;re moving locally or internationally, downsizing or expanding, trust the "
                "removal experts committed to making your move simple and stress-free."),
    "packing": ("From the first box to the last, our trained team protects everything you own &mdash; "
                "here&rsquo;s how our professional packing service works, step by step."),
    "storage": ("Clean, dry, secure containerised storage for as long as you need it &mdash; here&rsquo;s how "
                "storing your belongings with Orwell Removals & Storage works, step by step."),
}

def process_topic(name):
    """Map a service/page name to the topic word used in the step-process heading."""
    n = (name or "").lower()
    if "packing" in n: return "Packing"
    if "storage" in n: return "Storage"
    if "commercial" in n or "office" in n: return "Commercial Removal"
    if "international" in n: return "International Removal"
    if "european" in n: return "European Removal"
    if "man" in n and "van" in n: return "Man &amp; Van"
    return "Removal"

def step_process(bg="bg-beige", topic="Removal", heading=None, intro=None):
    """Shared chevron step-process section. `topic` tailors the heading + the 8 step
    labels to the page (Removal / Packing / Storage); the design is identical site-wide."""
    t = topic.lower()
    if "packing" in t:
        steps, ptype = PROC_STEPS_PACKING, "packing"
    elif "storage" in t:
        steps, ptype = PROC_STEPS_STORAGE, "storage"
    else:
        steps, ptype = PROC_STEPS_REMOVAL, "removal"
    heading = heading or f"Our Step-by-Step {topic} Process"
    intro = intro or _PROC_INTRO[ptype]
    cells = ""
    for i, (title, sub, slug, alt) in enumerate(steps):
        ico = img(f"images/process/orwell-removals-process-{slug}-icon.webp", alt, cls="")
        sub_html = f'<div class="oproc-sub">{sub}</div>' if sub else ""
        cells += (
            '<div class="oproc-step">'
            f'<div class="oproc-node">{ico}<span class="oproc-num">{i+1}</span></div>'
            f'<div class="oproc-card"><div class="oproc-title">{title}</div>{sub_html}</div>'
            '</div>')
    return section(
        f'<div class="text-center mb-9 lg:mb-14"><h2 class="relative leading-tight text-black">{heading}</h2>'
        f'<p class="text-lg xl:text-xl font-medium mt-2 max-w-3xl mx-auto">{intro}</p></div>'
        f'<div class="oproc"><div class="oproc-grid reveal-roll">{cells}</div></div>',
        bg=bg, extra="sec-glow")

def cta_band(heading, text_html, button_label, button_href, bg="bg-lightgrey", photos=None):
    """Centred heading + text + button, flanked by two contextual photos that
    fade into the section background on both sides (like the original site)."""
    if photos is None:
        photos = page_photos(heading, 2)
    end = "white" if "white" in bg else "lightgrey"   # fade colour = section background
    lp, rp = photos[0], photos[1]
    left = (f'<div class="hidden md:block absolute inset-y-0 left-0 w-[15%] lg:w-1/6" aria-hidden="true">'
            f'{photo_block(lp)}'
            f'<div class="absolute inset-0 bg-gradient-to-r from-{end}/10 via-{end}/75 to-{end}"></div></div>')
    right = (f'<div class="hidden md:block absolute inset-y-0 right-0 w-[15%] lg:w-1/6" aria-hidden="true">'
             f'{photo_block(rp)}'
             f'<div class="absolute inset-0 bg-gradient-to-l from-{end}/10 via-{end}/75 to-{end}"></div></div>')
    content = (
        '<div class="container relative z-10">'
        '<div class="max-w-4xl mx-auto text-center">'
        f'<h2 class="relative leading-tight text-black">{esc(heading)}</h2>'
        f'<div class="text-lg xl:text-xl font-medium mt-2">{text_html}</div>'
        f'<a href="{button_href}" class="button-orange mt-6 xl:mt-8 mx-auto inline-flex items-center gap-3">{esc(button_label)}</a>'
        '</div></div>')
    return (f'<section class="relative {bg} w-full overflow-hidden pt-10 lg:pt-20 pb-10 lg:pb-20 border-border">'
            f'{left}{right}{content}</section>')

def quote_bar(lead="Get a Free", rest="Home Removal Quote",
              subtext="Find out how much your home move will cost.",
              button_label="Get a Free Quote", button_href="/get-a-quote/"):
    """Slim slate CTA bar: split heading + subtext on the left, click-to-call
    number and orange quote button on the right (stacks centred on mobile)."""
    b = S.BUSINESS
    head = ('<div class="text-center lg:text-left">'
            f'<h2 class="text-white text-2xl lg:text-3xl mb-1"><span class="text-beige">{esc(lead)}</span> {esc(rest)}</h2>'
            f'<p class="text-white/90 font-medium mb-0 normal-case">{esc(subtext)}</p></div>')
    phone = (f'<a href="{b["phone_link"]}" class="inline-flex items-center gap-2 text-white font-bold text-lg xl:text-xl '
             f'hover:text-orange whitespace-nowrap" aria-label="Call Orwell Removals &amp; Storage on {b["phone"]}">'
             f'{icon("phone","w-5 h-5 text-beige")}<span>{b["phone"]}</span></a>')
    btn = f'<a href="{button_href}" class="button-orange whitespace-nowrap">{esc(button_label)}</a>'
    actions = f'<div class="flex flex-wrap items-center justify-center gap-x-7 gap-y-4 shrink-0">{phone}{btn}</div>'
    return ('<section class="bg-darkgrey w-full py-7 lg:py-9 border-border">'
            '<div class="container"><div class="flex flex-col lg:flex-row items-center lg:justify-between gap-6">'
            f'{head}{actions}</div></div></section>')

# Card rollover alternates creme (light → keep dark text) and grey (dark → white text). No orange/green.
CARD_HOVER = [
    ("card-hov-creme hover:bg-beige hover:border-black", ""),              # creme hover, dark text
    ("hover:bg-darkgrey hover:border-darkgrey", " group-hover:text-white"),    # grey hover, white text
]

# Simple line-art pictograms (currentColor) used beside card headings, like the old site.
PICTOGRAMS = {
    "house": '<path d="M12 3 2 11h3v9h6v-6h2v6h6v-9h3z"/>',
    "office": '<path d="M3 21V3h11v6h7v12H3zm2-2h4V5H5v14zm6 0h8v-8h-5v2h-3v6zM7 7h2V5H7zm0 4h2V9H7zm0 4h2v-2H7z"/>',
    "globe": '<path d="M12 2a10 10 0 100 20 10 10 0 000-20zm6.9 6h-2.9a15 15 0 00-1.3-3.6A8 8 0 0118.9 8zM12 4c.8 0 2 1.5 2.6 4H9.4C10 5.5 11.2 4 12 4zM4.3 14a8 8 0 010-4h3.1a18 18 0 000 4zm.8 2h2.9a15 15 0 001.3 3.6A8 8 0 015.1 16zM12 20c-.8 0-2-1.5-2.6-4h5.2C14 18.5 12.8 20 12 20zm.6-6H9.4a16 16 0 010-4h5.2a16 16 0 010 4zm2 2h2.9a8 8 0 01-4.2 3.6A15 15 0 0014.6 16zm.5-2a18 18 0 000-4h3.1a8 8 0 010 4z"/>',
    "van": '<path d="M2 6h12v9H2zm13 3h3.2l2.8 3v3h-6zM6 16a2 2 0 100 4 2 2 0 000-4zm10 0a2 2 0 100 4 2 2 0 000-4z"/>',
    "box": '<path d="M12 2l9 4v12l-9 4-9-4V6zm0 2.2L5.5 7 12 9.8 18.5 7zM5 8.6V17l6 2.7v-8.4zm14 0-6 2.7v8.4l6-2.7z"/>',
    "boxes": '<path d="M3 3h8v8H3zm10 5h8v13h-8zM3 13h8v8H3z"/>',
    "student": '<path d="M12 3 1 8l11 5 9-4.1V15h2V8zM5 12.7V16c0 1.7 3.1 3 7 3s7-1.3 7-3v-3.3l-7 3.2z"/>',
    "piano": '<path d="M3 4h18v16H3zm3 1v9h2V5zm4 0v9h2V5zm4 0v9h2V5z"/>',
    "antique": '<path d="M8 2h8v2a4 4 0 01-1.5 3.1A5 5 0 0118 12v6a3 3 0 01-3 3H9a3 3 0 01-3-3v-6a5 5 0 013.5-4.9A4 4 0 018 4z"/>',
    "glove": '<path d="M7 22a6 6 0 01-2-4.5V11a1.5 1.5 0 013 0V8a1.5 1.5 0 013 0V7a1.5 1.5 0 013 0v2a1.5 1.5 0 013 0v6a7 7 0 01-2 5z"/>',
    "pin": '<path d="M12 2a7 7 0 00-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 00-7-7zm0 9.5A2.5 2.5 0 1112 6.5a2.5 2.5 0 010 5z"/>',
    "doc": '<path d="M6 2h8l4 4v16H6zm8 1.5V7h3.5zM8 11h8v1.5H8zm0 3h8v1.5H8zm0 3h5v1.5H8z"/>',
    "spark": '<path d="M12 2l2.4 6.2L21 10l-6.6 1.8L12 18l-2.4-6.2L3 10l6.6-1.8z"/>',
    "pound": '<path d="M6 20v-1.8c1.2-.3 2-1.3 2-2.7V13H6.2v-1.6H8V9.4A4 4 0 0 1 15.8 8l-1.7.9A2 2 0 0 0 10 9.4v2h3.4V13H10v2.5c0 .9-.3 1.7-.9 2.3H18V20z"/>',
    "shield": '<path d="M12 2l8 3v6c0 5-3.4 9.3-8 11-4.6-1.7-8-6-8-11V5z"/>',
    "help": '<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 16.2a1.3 1.3 0 1 1 0-2.6 1.3 1.3 0 0 1 0 2.6zm1.7-6.3c-.7.5-.9.8-.9 1.4v.3h-1.7v-.4c0-1 .4-1.6 1.2-2.1.7-.5.9-.7.9-1.2 0-.6-.5-1-1.2-1-.7 0-1.2.4-1.5 1.1l-1.5-.7A3.1 3.1 0 0 1 11.9 7c1.8 0 3 1 3 2.5 0 1-.4 1.6-1.2 2.1z"/>',
    "clock": '<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm1 5h-2v6l5 3 1-1.7-4-2.3z"/>',
}

def _faq_icon(question):
    """Pick a topic pictogram for a FAQ from keywords in its question."""
    q = str(question).lower()
    table = [
        ("how much", "pound"), ("cost", "pound"), ("price", "pound"), ("pricing", "pound"),
        ("quote", "pound"), ("deposit", "pound"), ("£", "pound"), ("pay", "pound"),
        ("insur", "shield"), ("protect", "shield"), ("damage", "shield"), ("safe", "shield"),
        ("lapada", "shield"), ("checkatrade", "shield"), ("guarantee", "shield"),
        ("area", "pin"), ("where", "pin"), ("town", "pin"), ("postcode", "pin"),
        ("location", "pin"), ("travel", "pin"), ("distance", "pin"), ("nationwide", "pin"),
        ("pack", "box"), ("material", "box"), ("wrap", "box"), ("fragile", "box"), ("box", "box"),
        ("storage", "boxes"), ("store", "boxes"),
        ("advance", "clock"), ("how long", "clock"), ("when", "clock"), ("notice", "clock"),
        ("book", "clock"), ("same-day", "clock"), ("short-notice", "clock"), ("date", "clock"),
        ("time", "clock"), ("day", "clock"), ("timing", "clock"),
        ("piano", "piano"), ("antique", "antique"), ("valuable", "antique"), ("fine art", "antique"),
        ("student", "student"), ("man and van", "van"), ("clearance", "boxes"),
    ]
    for kw, name in table:
        if kw in q:
            return name
    return "help"

def _pictogram(title, href):
    key = (str(href) + " " + str(title)).lower()
    table = [("commercial", "office"), ("office", "office"), ("international", "globe"),
             ("european", "globe"), ("student", "student"), ("piano", "piano"),
             ("antique", "antique"), ("white-glove", "glove"), ("white glove", "glove"),
             ("man-and-van", "van"), ("man and van", "van"), ("contract-delivery", "van"),
             ("delivery", "van"), ("removal-services", "van"), ("storage", "boxes"),
             ("packing", "box"), ("materials", "box"), ("box shop", "box"),
             ("house-clearance", "boxes"), ("clearance", "boxes"), ("house", "house"),
             ("/locations/", "pin"), ("removals", "van")]
    name = "spark"
    for kw, ic in table:
        if kw in key:
            name = ic
            break
    if "/blog/" in key or (href and href.strip("/") and "/" not in href.strip("/") and "removal" not in key):
        # root-level slugs are blog posts
        pass
    return f'<svg viewBox="0 0 24 24" class="w-10 h-10" fill="currentColor" aria-hidden="true">{PICTOGRAMS.get(name, PICTOGRAMS["spark"])}</svg>'

def _seed_from_href(href):
    """Map a card's link to the seed its destination page uses for page_photos(),
    so the card image == the linked page's hero (i.e. matches what the card references)."""
    h = (href or "").strip("/")
    for pref in ("services/", "locations/", "helpful-tips/"):
        if h.startswith(pref):
            return h[len(pref):]
    return h  # blog posts live at root

def card_grid(cards, cols=3, heading=None, intro=None, bg="bg-white", bg_image=None, reveal=False, spark=False, variant=None):
    """cards: list of (title, href, body_html). Each card carries a full-bleed image =
    the hero of the page it links to. Padded to full rows (no orphans).
    reveal=True makes the cards fly in left→right on scroll (.reveal-lr + js/reveal.js).
    spark=True orbits a glowing sparkle around each (pictogram) card's border.
    variant="service" renders the bespoke Fox-Hub-style service cards (icon badge + index
    number + sliding navy overlay on hover) instead of the standard rollover card."""
    colcls = {2: "md:col-span-6", 3: "md:col-span-6 lg:col-span-4", 4: "md:col-span-6 lg:col-span-3"}[cols]
    cells = []
    for i, card in enumerate(cards):
        rv_cls = " reveal-lr" if reveal else ""
        rv_style = f' style="transition-delay:{i*90}ms"' if reveal else ""
        # Cards accept (title, href, body) or (title, href, body, photo). With a photo,
        # a 16:10 hero image tops the card (e.g. blog articles); without one, a brand
        # pictogram sits beside the heading. White card, brand border, hover fills a
        # rotating brand colour. Visible CTA is descriptive (never bare "Read more").
        title, href, body = card[0], card[1], card[2]
        photo = card[3] if len(card) > 3 else None
        hov_bg, hov_text = CARD_HOVER[i % len(CARD_HOVER)]
        snippet = re.sub(r"</?p[^>]*>", "", body, flags=re.I).strip()  # un-wrap a single <p>
        # Varied, descriptive CTA wording (never a bare/repeated "Read more"); each still names
        # the card so the anchor stays descriptive + unique per the SEO rules.
        _leads = ["Explore", "Discover", "Learn about", "More about", "See more on", "A closer look at"]
        cta = f'{_leads[i % len(_leads)]} {esc(title)}'
        if variant == "service":
            pic = _pictogram(title, href)
            cells.append(
                f'<div class="col-span-12 {colcls}{rv_cls}"{rv_style}>'
                f'<a href="{href}" class="svc-card group" aria-label="{esc(title)}">'
                f'<span class="svc-card-num" aria-hidden="true">{i+1:02d}</span>'
                f'<span class="svc-card-icon">{pic}</span>'
                f'<h3 class="svc-card-title">{esc(title)}</h3>'
                f'<p class="svc-card-text">{snippet}</p>'
                f'<span class="svc-card-link">{cta}'
                f'<span class="svc-card-arrow">{icon("chevron","h-3.5 w-3.5 -rotate-90 fill-current")}</span>'
                f'</span></a></div>')
            continue
        # orbiting sparkle (non-photo cards only — photo cards clip it); phase-offset per card
        spark_html = (f'<span class="card-spark" aria-hidden="true" style="animation-delay:-{i*0.6:.1f}s"></span>'
                      if (spark and not photo) else "")
        if photo:
            media = ('<div class="overflow-hidden" style="aspect-ratio:16/10;">'
                     + img("images/photos/" + photo[0] + ".webp", photo[1], cls="w-full h-full object-cover")
                     + '</div>')
            cells.append(
                f'<div class="col-span-12 {colcls}{rv_cls}"{rv_style}><a href="{href}" class="card-rollover group flex flex-col h-full bg-white border-2 border-darkgrey rounded-xl shadow-custom overflow-hidden transition {hov_bg}">'
                f'{media}'
                f'<div class="flex flex-col flex-1 p-6">'
                f'<h3 class="text-xl font-semibold text-black{hov_text}">{esc(title)}</h3>'
                f'<p class="mt-3 flex-1 text-darkgrey{hov_text} line-clamp-3 mb-0">{snippet}</p>'
                f'<span class="mt-4 font-bold uppercase text-blue{hov_text} inline-flex items-center gap-1">{cta} {icon("chevron","h-4 w-4 -rotate-90 fill-current")}</span>'
                f'</div></a></div>')
        else:
            pic = _pictogram(title, href)
            cells.append(
                f'<div class="col-span-12 {colcls}{rv_cls}"{rv_style}><a href="{href}" class="card-rollover relative group flex flex-col h-full bg-white border-2 border-darkgrey rounded-xl shadow-custom p-6 transition {hov_bg}">'
                f'<div class="flex items-start gap-4"><span class="ico-badge shrink-0 w-14 h-14">{pic}</span>'
                f'<h3 class="text-xl font-semibold text-black{hov_text}">{esc(title)}</h3></div>'
                f'<p class="mt-3 flex-1 text-darkgrey{hov_text} line-clamp-3 mb-0">{snippet}</p>'
                f'<span class="mt-4 font-bold uppercase text-blue{hov_text} inline-flex items-center gap-1">{cta} {icon("chevron","h-4 w-4 -rotate-90 fill-current")}</span>'
                f'{spark_html}</a></div>')
    head = ""
    if heading:
        head = f'<div class="text-center mb-8"><h2 class="relative leading-tight text-black">{esc(heading)}</h2>'
        head += (f'<div class="text-lg xl:text-xl font-medium mt-2 max-w-3xl mx-auto">{intro}</div>' if intro else "") + "</div>"
    grid = f'<div class="grid grid-cols-12 gap-6 lg:gap-8">{"".join(cells)}</div>'
    if bg_image:
        bgimg = img("images/photos/" + bg_image[0] + ".webp", bg_image[1], cls="w-full h-full object-cover")
        return (
            '<section class="relative bg-white w-full pt-8 lg:pt-16 pb-8 lg:pb-16 border-border overflow-hidden">'
            f'<div class="absolute inset-0">{bgimg}</div>'
            '<div class="absolute inset-0 cardbg-fade"></div>'
            f'<div class="container relative z-10">{head}{grid}</div></section>')
    return section(head + grid, bg=bg)

STORAGE_CTA_COLS = [
    ("Household Storage", "/services/storage/household-storage/",
     "Ideal for moving delays, downsizing, renovations or simply freeing up space. Flexible, affordable terms from a few days to long term."),
    ("Business Storage", "/services/storage/business-storage/",
     "Secure storage for stock, equipment, office furniture and business moves &mdash; fully managed, including packing and collection."),
    ("Secure Storage", "/services/storage/",
     "Clean, dry, alarmed containerised storage at our Westerfield base near Ipswich. Your belongings wrapped, logged and looked after."),
]

def storage_cta(bg_photo=("packed-boxes-wrapped-furniture",
                          "Packed boxes and wrapped furniture ready for secure storage with Orwell"), bg="bg-darkgrey"):
    """Storage promo CTA — three storage types over a faded slate photo, to drive
    visitors into storage. Site branding: slate background, white text with cream
    emphasis, cream brand buttons (no bright orange)."""
    cells = ""
    for title, href, desc in STORAGE_CTA_COLS:
        cells += (
            '<div class="col-span-12 md:col-span-4 flex flex-col items-center text-center">'
            f'<h3 class="text-xl xl:text-2xl font-bold uppercase text-white leading-tight">{esc(title)}</h3>'
            f'<p class="mt-3 text-white/95 text-base xl:text-lg flex-1">{desc}</p>'
            f'<a href="{href}" class="button-orange btn-white mt-6 w-full sm:w-auto justify-center text-center">Explore {esc(title)}</a>'
            '</div>')
    bgimg = img("images/photos/" + bg_photo[0] + ".webp", bg_photo[1], cls="w-full h-full object-cover")
    heading = ('Need <span class="text-beige">Long or Short-Term Storage</span> for '
               '<span class="text-beige">Your Home or Business</span>?')
    return (
        f'<section class="relative {bg} w-full overflow-hidden pt-12 lg:pt-20 pb-12 lg:pb-20 border-border">'
        f'<div class="absolute inset-0">{bgimg}</div>'
        '<div class="absolute inset-0 storage-cta-overlay"></div>'
        '<div class="container relative z-10">'
        f'<div class="text-center mb-9 lg:mb-12"><h2 class="storage-cta-head text-white leading-tight">{heading}</h2></div>'
        f'<div class="grid grid-cols-12 gap-8 lg:gap-12">{cells}</div>'
        '</div></section>')

def faq_block(faqs, heading="Frequently Asked Questions", bg="bg-lightgrey", fancy=True, extra=""):
    """faqs: list of (question, answer_html_or_text). Returns (html, schema_dict).
    fancy=True uses the bespoke card layout: a topic icon per FAQ + rollover effect."""
    items = []
    for q, a in faqs:
        if fancy:
            picto = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" class="w-6 h-6">'
                     f'{PICTOGRAMS.get(_faq_icon(q), PICTOGRAMS["help"])}</svg>')
            items.append(
                '<div class="faq-card reveal-lr" x-data="{open:false}" :class="open && \'is-open\'">'
                '<button type="button" class="faq-head" @click="open=!open" :aria-expanded="open">'
                f'<span class="faq-ico">{picto}</span>'
                f'<span class="faq-q">{esc(q)}</span>'
                f'<span class="faq-toggle" :class="open && \'is-open\'">{icon("chevron","w-5 h-5 fill-current")}</span>'
                '</button>'
                f'<div class="faq-body" x-show="open" x-cloak x-transition.duration.200ms>{a}</div>'
                '</div>')
        else:
            items.append(
                f'<div class="border-b border-border py-4" x-data="{{open:false}}">'
                f'<button type="button" class="w-full flex items-center justify-between text-left bg-transparent" @click="open=!open" :aria-expanded="open">'
                f'<span class="text-lg xl:text-xl font-semibold text-black">{esc(q)}</span>'
                f'<span :class="open?\'rotate-180\':\'\'" class="transition-transform">{icon("chevron","h-6 w-6 fill-current text-orange")}</span></button>'
                f'<div class="mt-3 text-darkgrey" x-show="open" x-cloak x-transition.duration.200ms>{a}</div></div>')
    span = "lg:col-span-10 lg:col-start-2" if fancy else "lg:col-span-8 lg:col-start-3"
    body = f'<div class="faq-list">{"".join(items)}</div>' if fancy else "".join(items)
    html_out = section(
        f'<div class="grid grid-cols-12"><div class="col-span-12 {span}">'
        f'<div class="text-center mb-6 lg:mb-9"><span class="faq-kicker">Frequently Asked</span>'
        f'<h2 class="relative leading-tight text-black">{esc(heading)}</h2></div>'
        f'{body}</div></div>', bg=bg, extra=extra)
    schema = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": _html.unescape(_strip_tags(a))}}
            for q, a in faqs]
    }
    return html_out, schema

def _strip_tags(t):
    import re
    return re.sub(r"<[^>]+>", "", str(t)).strip()

# ---------------------------------------------------------------- SCHEMA
def schema_localbusiness():
    b = S.BUSINESS
    return {
        "@context": "https://schema.org", "@type": "MovingCompany",
        "@id": S.SITE_URL + "/#business",
        "name": b["name"], "legalName": b["legal_name"], "url": S.SITE_URL,
        "telephone": b["phone"], "email": b["email"],
        "image": abs_url("images/brand/orwell-removals-logo.png"),
        "logo": abs_url("images/brand/orwell-removals-logo.png"),
        "address": {"@type": "PostalAddress", "streetAddress": b["street"],
                    "addressLocality": b["locality"], "addressRegion": b["region"],
                    "postalCode": b["postcode"], "addressCountry": "GB"},
        "geo": {"@type": "GeoCoordinates", "latitude": b["geo"]["lat"], "longitude": b["geo"]["lng"]},
        "areaServed": [{"@type": "AdministrativeArea", "name": a} for a in b["area_served"]],
        "openingHours": b["hours"],
        "sameAs": list(S.SOCIAL.values()),
    }

def schema_breadcrumb(trail):
    """trail: list of (name, path)."""
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(p)}
            for i, (n, p) in enumerate(trail)]
    }

# ---------------------------------------------------------------- PAGE
def _dedupe_images(html, seen=None):
    """RULE: no /images/photos/ image may appear twice on a page. Each repeat is
    swapped for an unused pool photo (correct alt + dimensions, same classes).
    Pass a shared `seen` set to chain de-dup across several HTML fragments."""
    if seen is None:
        seen = set()
    alt_by = {p[0]: p[1] for p in PHOTOS}
    pool = [p[0] for p in PHOTOS if p[0] != QUOTE_BAND_PHOTO]
    def repl(m):
        tag = m.group(0)
        if "data-tile" in tag:        # hero rubik mosaic — one image sliced 9×, never dedupe
            return tag
        stem = m.group(1).rsplit("/", 1)[-1].rsplit(".", 1)[0]
        if stem not in seen:
            seen.add(stem)
            return tag
        for cand in pool:
            if cand not in seen:
                seen.add(cand)
                cm = re.search(r'class="([^"]*)"', tag)
                cls = cm.group(1) if cm else ""
                eager = ('fetchpriority="high"' in tag) or ('loading="eager"' in tag)
                return img("images/photos/" + cand + ".webp", alt_by.get(cand, "Orwell Removals Ipswich move"), cls=cls, eager=eager)
        return tag
    return re.sub(r'<img\b[^>]*?\bsrc="(/images/photos/[^"]+)"[^>]*?>', repl, html)

def trust_reviews_row():
    """Disabled for Orwell: no embedded review widget account, and a sitewide identical
    band would create duplicate <h2>s. Genuine reviews live on the /reviews/ page
    (Checkatrade / Google / Three Best Rated). Returns nothing."""
    return ""

def blog_feed(page_path=None, n=3):
    """Per-page blog strip: shows the 3 blogs assigned to THIS page in data/blog_plan.py
    (relevant + unique per page; never duplicated on a page). Only includes blogs whose post
    has been rendered. Blog posts (not in the plan's page map) get no feed."""
    try:
        from blog_plan import PAGE_BLOGS, BY_SLUG
    except Exception:
        return ""
    slugs = PAGE_BLOGS.get(page_path or "", [])
    if not slugs:
        return ""
    bdir = os.path.join(S.ROOT, "data", "blog")
    cards, used = [], []
    for slug in slugs:
        if not os.path.exists(os.path.join(bdir, slug + ".json")):
            continue
        spec = BY_SLUG.get(slug)
        if not spec:
            continue
        photo = match_photo(spec["title"] + " " + spec.get("kw", ""), used=tuple(used)) or page_photos(slug, 1)[0]
        used.append(photo[0])
        cards.append((spec["title"], "/blog/" + slug + "/",
                      '<p><span class="text-blue font-semibold text-sm uppercase">' + esc(spec["category"]) + '</span></p>',
                      photo))
    if not cards:
        return ""
    return card_grid(cards, cols=3, heading="From Our Blog",
                     intro="Moving tips and local guides relevant to your move, from our Suffolk team.",
                     bg="bg-lightgrey", reveal=True)

def render_page(*, title, description, canonical_path, body, og_image=None,
                robots="index, follow", breadcrumb=None, extra_schema=None, active="", show_quote=True, dedupe=True, show_fabs=True,
                show_trust_reviews=True):
    # Hero pinning: if this page has a curated hero in the hero_map snapshot,
    # restore it — swap the eager hero <img> and point og/twitter/preload at it — so the
    # hero never drifts when the photo-rotation pool changes.
    _ov = OLD_HEROES.get(canonical_path)
    if _ov:
        _hsrc = "images/photos/" + _ov[0] + ".webp"
        if os.path.exists(os.path.join(S.ROOT, _hsrc)):
            _hero_img = img(_hsrc, _ov[1], cls="w-full h-full object-cover", eager=True)
            body, _hn = re.subn(r'<img\b[^>]*\bfetchpriority="high"[^>]*>', lambda m: _hero_img, body, count=1)
            if _hn:
                og_image = _hsrc
    _seen = set()
    body = _dedupe_images(body, _seen) if dedupe else body
    # Reviews row sits in-flow as ~row 5 (after the 4th top-level section) on every page
    # type. Location & About pages insert it manually at their own logical row 5 and pass
    # show_trust_reviews=False, so they skip this. The /reviews/ page never gets it.
    if show_trust_reviews and canonical_path != "/reviews/":
        _secs = [m.start() for m in re.finditer(r'<section\b', body)]
        _rv = trust_reviews_row()
        if len(_secs) >= 5:
            body = body[:_secs[4]] + _rv + "\n" + body[_secs[4]:]
        else:
            body = body + "\n" + _rv
    question = ""
    if show_quote:
        question = _dedupe_images(cta_band(
            "Have a Removals Question?",
            'Feel free to <a href="/contact-us/">contact us</a>, browse our '
            '<a href="/gallery/">gallery</a> or read our '
            '<a href="/frequently-asked-questions/">FAQs page</a> which is full of useful information.',
            "Get a Free Quote", "/get-a-quote/", bg="bg-white"), _seen)
    feed = _dedupe_images(blog_feed(canonical_path), _seen) if dedupe else blog_feed(canonical_path)
    schema = [schema_localbusiness()]
    if breadcrumb:
        schema.append(schema_breadcrumb(breadcrumb))
    if extra_schema:
        schema += extra_schema if isinstance(extra_schema, list) else [extra_schema]
    doc = [
        head_html(title, description, canonical_path, og_image=og_image, robots=robots, schema=schema),
        f'<body class="font-body bg-white text-black overflow-x-clip text-base xl:text-lg{(" page-" + active) if active else ""}">',
        '<div id="page" class="relative min-h-screen block" x-data="{menuOpen:false}">',
        header_html(active=active),
        '<div id="content" class="site-content font-normal text-black">',
        '<main id="main" class="site-main" role="main">',
        body,
        "</main></div>",
        feed,
        (quote_band() if show_quote else ""),
        question,
        footer_html(),
        "</div>",
        (fabs() if show_fabs else ""),
        # (Sticky floating reviews badge removed — the live review widget now sits in the hero.)
        # Alpine.js powers the menu, dropdowns, FAQ accordions and mobile toggle.
        f'<script defer src="/js/alpine.min.js?v={ASSET_VER}"></script>',
        # Photo-strip carousel (arrows + centre-emphasis); no-ops on pages without [data-carousel].
        f'<script defer src="/js/photo-carousel.js?v={ASSET_VER}"></script>',
        # Scroll-reveal: cards fly in left -> right when they enter the viewport.
        f'<script defer src="/js/reveal.js?v={ASSET_VER}"></script>',
        "</body></html>",
    ]
    return "\n".join(doc)

def write(path_rel, html_doc):
    out = os.path.join(S.ROOT, path_rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return out
