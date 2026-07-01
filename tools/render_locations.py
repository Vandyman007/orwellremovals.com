# -*- coding: utf-8 -*-
"""Suffolk location pages for Orwell Removals & Storage — /locations/ index, the Suffolk
county hub, and 16 town pages. Town-specific prose is authored in data/locations/<slug>.json
(original, NOT copied). Each town page: >=1500 words, unique title/desc/H1, keyword in H1 +
first paragraph, MovingCompany + Breadcrumb + FAQPage schema, an embedded area map,
>=10 in-body internal links, "fully covered" (never insured).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
from engine import esc, icon, img, section, prose, card_grid, cta_band, faq_block, map_embed

B = E.S.BUSINESS
PH = {p[0]: p for p in E.PHOTOS}
def _photo(slug): return PH.get(slug, E.PHOTOS[0])
LOCDIR = os.path.join(E.S.ROOT, "data", "locations")

# slug -> (Town, postcode, hero photo, [nearby slugs])
TOWNS = {
 "ipswich-removals": ("Ipswich", "IP1", "orwell-van-outside-suffolk-home", ["woodbridge-removals", "felixstowe-removals", "stowmarket-removals", "hadleigh-removals"]),
 "felixstowe-removals": ("Felixstowe", "IP11", "orwell-luton-van-ipswich-road", ["ipswich-removals", "woodbridge-removals", "saxmundham-removals"]),
 "woodbridge-removals": ("Woodbridge", "IP12", "orwell-van-period-suffolk-house", ["ipswich-removals", "framlingham-removals", "saxmundham-removals", "felixstowe-removals"]),
 "stowmarket-removals": ("Stowmarket", "IP14", "orwell-box-lorry-residential-street", ["needham-market-removals", "ipswich-removals", "bury-st-edmunds-removals"]),
 "bury-st-edmunds-removals": ("Bury St Edmunds", "IP33", "orwell-lorry-house-driveway", ["stowmarket-removals", "newmarket-removals", "sudbury-removals", "haverhill-removals"]),
 "sudbury-removals": ("Sudbury", "CO10", "orwell-van-brick-suffolk-house", ["hadleigh-removals", "bury-st-edmunds-removals", "haverhill-removals"]),
 "newmarket-removals": ("Newmarket", "CB8", "orwell-lorry-gravel-driveway", ["bury-st-edmunds-removals", "haverhill-removals"]),
 "haverhill-removals": ("Haverhill", "CB9", "orwell-van-modern-driveway", ["newmarket-removals", "sudbury-removals", "bury-st-edmunds-removals"]),
 "lowestoft-removals": ("Lowestoft", "NR32", "removal-lorry-suffolk-street", ["beccles-removals", "southwold-removals"]),
 "beccles-removals": ("Beccles", "NR34", "orwell-van-outside-modern-home", ["lowestoft-removals", "southwold-removals", "saxmundham-removals"]),
 "southwold-removals": ("Southwold", "IP18", "orwell-lorry-outside-suffolk-house", ["lowestoft-removals", "beccles-removals", "aldeburgh-removals"]),
 "aldeburgh-removals": ("Aldeburgh", "IP15", "orwell-lorry-period-suffolk-house", ["saxmundham-removals", "woodbridge-removals", "southwold-removals"]),
 "framlingham-removals": ("Framlingham", "IP13", "orwell-van-on-customer-driveway", ["woodbridge-removals", "saxmundham-removals", "ipswich-removals"]),
 "hadleigh-removals": ("Hadleigh", "IP7", "two-orwell-vans-residential-street", ["ipswich-removals", "sudbury-removals", "needham-market-removals"]),
 "needham-market-removals": ("Needham Market", "IP6", "orwell-crew-loading-townhouse", ["stowmarket-removals", "ipswich-removals", "hadleigh-removals"]),
 "saxmundham-removals": ("Saxmundham", "IP17", "orwell-lorry-van-outside-home", ["aldeburgh-removals", "woodbridge-removals", "framlingham-removals", "beccles-removals"]),
}
ORDER = ["ipswich-removals", "felixstowe-removals", "woodbridge-removals", "stowmarket-removals",
         "bury-st-edmunds-removals", "sudbury-removals", "newmarket-removals", "haverhill-removals",
         "lowestoft-removals", "beccles-removals", "southwold-removals", "aldeburgh-removals",
         "framlingham-removals", "hadleigh-removals", "needham-market-removals", "saxmundham-removals"]

def _services_in(town):
    items = [
        ("home removals", "/services/home-removals/"), ("office removals", "/services/office-removals/"),
        ("commercial removals", "/services/commercial-removals/"), ("long distance removals", "/services/long-distance-removals/"),
        ("man &amp; van", "/services/man-and-van/"), ("piano removals", "/services/piano-removals/"),
        ("packing", "/services/packing-service/"), ("storage", "/services/storage/"),
    ]
    lis = "".join(f'<li><a href="{h}">{t.capitalize() if not t[0].isupper() else t}</a></li>' for t, h in items)
    return (
        f'<h2 class="relative leading-tight text-black">Our Removals &amp; Storage Services in {esc(town)}</h2>'
        f'<p>Wherever you&rsquo;re moving in {esc(town)} or the surrounding villages, our family-run team offers the full '
        f'range of services &mdash; and every job is <strong>fully covered</strong>:</p>'
        f'<ul class="tick-list grid sm:grid-cols-2 gap-x-10 gap-y-1">{lis}</ul>'
        f'<p>Not sure what you need? <a href="/get-a-quote/">Request a free quote</a>, see how our '
        f'<a href="/pricing/">pricing</a> works, or <a href="/contact-us/">contact the team</a> for a friendly chat '
        f'about your {esc(town)} move.</p>')

def _related_towns(nearby, town):
    cards = []
    for s in nearby:
        if s in TOWNS:
            tn = TOWNS[s][0]
            cards.append((f"Removals in {tn}", "/" + s.replace("-removals", "/").join(["locations/", ""]) if False else f"/locations/{s}/",
                          f"<p>Moving to or from {tn}? We cover it too &mdash; with the same careful, fully covered service.</p>"))
    return card_grid(cards, cols=len(cards) if len(cards) in (2, 3, 4) else 3,
                     heading=f"Nearby Towns We Cover", bg="bg-lightgrey", reveal=True,
                     intro=f"Orwell Removals &amp; Storage covers the whole county &mdash; here are some areas near {esc(town)}.")

SHARED_FAQS = [
    ("Are my belongings covered during the move?",
     "<p>Yes &mdash; every move is fully covered, with goods-in-transit and public liability protection arranged through "
     "Basil Fry, the removals-trade specialist.</p>"),
    ("How much will my move cost?",
     '<p>It depends on the size of your home, the distance, access and any packing or storage you need. The best way to '
     'find out is a free, no-obligation quote &mdash; <a href="/get-a-quote/">request one here</a> or see our '
     '<a href="/pricing/">pricing page</a>.</p>'),
    ("Can you store my belongings between moves?",
     '<p>Yes &mdash; our clean, dry <a href="/services/storage/">secure storage</a> at our Westerfield base is ideal for '
     'bridging a gap between completion dates, downsizing or renovating.</p>'),
]

def town_page(slug):
    town, pc, photo, nearby = TOWNS[slug]
    d = json.load(open(os.path.join(LOCDIR, slug + ".json"), encoding="utf-8"))
    body_inner = "".join(f'<h2>{esc(s["h"])}</h2>{s["p"]}' for s in d["sections"])
    intro = f'<h2 class="relative leading-tight text-black">Your Local {esc(town)} Removals Company</h2>{d["intro"]}'
    body = "\n".join([
        E.hero(f"Removals in {esc(town)}",
               f"Trusted, fully covered removals in {esc(town)} from a family-run Ipswich team &mdash; homes and "
               "businesses, packed, moved and stored with care.",
               _photo(photo), kicker=f"Suffolk &middot; {esc(pc)}", cta=True),
        section(prose(intro), bg="bg-white", extra="logo-row overflow-hidden"),
        E.media_rows(body_inner, seed=slug, bg="bg-beige", topic=town + " removals storage"),
        section(prose(_services_in(town)), bg="bg-white", extra="logo-row overflow-hidden"),
        section('<h2 class="relative leading-tight text-black text-center mb-6">' + esc(town) + ' &amp; the Surrounding Area</h2>'
                + map_embed(town + ", Suffolk, UK", "Map of " + town + ", Suffolk", zoom=12), bg="bg-lightgrey"),
        E.standard_feature_panel(E.page_photos(slug + "-f", 1)[0], reverse=True, bg="bg-white", name=town),
        E.step_process(bg="bg-beige"),
        _related_towns(nearby, town),
        E.trusted_by("bg-white"),
    ])
    faqs = [(esc(q) if False else q, a) for q, a in d["faqs"]] + SHARED_FAQS
    faq_html, faq_schema = faq_block(faqs, heading=f"Removals in {esc(town)} — FAQs", bg="bg-lightgrey")
    body += "\n" + faq_html
    body += "\n" + cta_band(f"Moving in or around {esc(town)}?",
                            f"Tell us about your {esc(town)} move and we&rsquo;ll give you a clear, no-obligation quote. Call 01473 411531 or request a quote online.",
                            "Get a Free Quote", "/get-a-quote/", bg="bg-white")
    doc = E.render_page(
        title=f"Removals in {town} | Orwell Removals & Storage",
        description=f"Trusted removals in {town}, Suffolk from family-run Orwell Removals & Storage. Home, office & commercial moves, packing and storage. Fully covered. Free quote.",
        canonical_path=f"/locations/{slug}/", body=body,
        og_image="images/photos/" + _photo(photo)[0] + ".webp",
        breadcrumb=[("Home", "/"), ("Locations", "/locations/"), (town, f"/locations/{slug}/")],
        extra_schema=[faq_schema], active="locations")
    return E.write(f"locations/{slug}/index.html", doc)

# ---------------------------------------------------------------- county hub
def county_hub():
    town_cards = [(f"Removals in {TOWNS[s][0]}", f"/locations/{s}/",
                   f"<p>{TOWNS[s][0]} ({TOWNS[s][1]}) and the surrounding area.</p>") for s in ORDER]
    body = "\n".join([
        E.hero("Removals in Suffolk",
               "Family-run removals and storage across the whole of Suffolk &mdash; from the coast to the county "
               "border, every move fully covered.",
               _photo("orwell-box-lorry-ipswich-street"), kicker="The whole county", cta=True),
        section(prose(
            '<h2 class="relative leading-tight text-black">Your Suffolk Removals &amp; Storage Company</h2>'
            '<p>For dependable <strong>removals in Suffolk</strong>, Orwell Removals &amp; Storage has covered the county '
            'from our base at Old Station Works in <a href="/locations/ipswich-removals/">Westerfield, Ipswich</a> since '
            '2005. We&rsquo;re a genuinely local, family-run team &mdash; the same friendly faces from your first call to '
            'the last box &mdash; and every move is <strong>fully covered</strong> through Basil Fry, the removals-trade '
            'specialist. From a single item to a full home or business relocation, we make moving in Suffolk simple.</p>'
            '<p>Suffolk is a wonderfully varied county to move around: the busy county town of Ipswich, the historic '
            'streets of <a href="/locations/bury-st-edmunds-removals/">Bury St Edmunds</a>, the port town of '
            '<a href="/locations/felixstowe-removals/">Felixstowe</a>, riverside <a href="/locations/woodbridge-removals/">'
            'Woodbridge</a> and the Heritage Coast around <a href="/locations/aldeburgh-removals/">Aldeburgh</a> and '
            '<a href="/locations/southwold-removals/">Southwold</a>. Each has its own character, its own access quirks '
            'and its own mix of period cottages, terraces and new-build estates &mdash; and after two decades on the road '
            'we know them well.</p>'), bg="bg-white", extra="logo-row overflow-hidden"),
        card_grid(town_cards, cols=4, heading="Towns We Cover Across Suffolk", reveal=True,
                  intro="Choose your town for local detail, or "
                        '<a href="/get-a-quote/">get a free quote</a> for your move.', bg="bg-lightgrey"),
        section(prose(
            '<h2 class="relative leading-tight text-black">One Local Team for Your Whole Move</h2>'
            '<p>Across every Suffolk town we offer the same complete service: '
            '<a href="/services/home-removals/">home</a>, <a href="/services/office-removals/">office</a> and '
            '<a href="/services/commercial-removals/">commercial removals</a>, '
            '<a href="/services/long-distance-removals/">long-distance moves</a> when you&rsquo;re leaving the county, a '
            'cost-effective <a href="/services/man-and-van/">man &amp; van</a>, specialist '
            '<a href="/services/piano-removals/">piano removals</a>, professional '
            '<a href="/services/packing-service/">packing</a> and clean, secure '
            '<a href="/services/storage/">storage</a>. Whatever your postcode, you get the same care and the same '
            'honest, fixed pricing.</p>'
            '<p>Because we&rsquo;re based in the county rather than run from a distant call centre, we understand the '
            'practical side of moving here &mdash; the narrow lanes of the coastal towns, the parking around historic '
            'market squares, and the A12 and A14 links that tie the county together. That local knowledge keeps your '
            'move efficient and your quote keen.</p>'), bg="bg-white", extra="logo-row overflow-hidden"),
        section(prose(
            '<h2 class="relative leading-tight text-black">Moving Into, Out Of, or Within Suffolk</h2>'
            '<p>Plenty of our work is people moving home within the county &mdash; first-time buyers, growing families '
            'trading up, and downsizers releasing space after many happy years. Just as often we&rsquo;re welcoming '
            'people into Suffolk from London and further afield, drawn by the coast, the countryside and the slower pace. '
            'And when a job, a family or a fresh start takes you out of the county, our '
            '<a href="/services/long-distance-removals/">long-distance removals</a> see you door to door, anywhere in '
            'the UK.</p>'
            '<p>Whatever direction your move takes, the approach is the same: a free survey and an honest, fixed quote; '
            'careful packing and protection; a punctual, uniformed crew; and clean, secure '
            '<a href="/services/storage/">storage</a> on hand if your dates don&rsquo;t quite line up. It&rsquo;s the '
            'unflustered, fully covered service that has kept Suffolk families and businesses coming back to us since '
            '2005 &mdash; and recommending us to their neighbours.</p>'), bg="bg-beige"),
        section('<h2 class="relative leading-tight text-black text-center mb-6">Covering the Whole of Suffolk</h2>'
                + map_embed("Suffolk, UK", "Map of Suffolk", zoom=9), bg="bg-lightgrey"),
        E.trusted_by("bg-white"),
        E.step_process(bg="bg-beige"),
    ])
    faqs = [
        ("Do you cover the whole of Suffolk?",
         '<p>Yes &mdash; from our Westerfield base we cover the entire county, including Ipswich, Bury St Edmunds, '
         'Felixstowe, Lowestoft, Woodbridge and every town in between. We also handle '
         '<a href="/services/long-distance-removals/">long-distance moves</a> out of the county.</p>'),
        ("Are you a local company?",
         "<p>Very much so &mdash; we&rsquo;re a family-run Suffolk firm trading since 2005, with the same team looking "
         "after your move from first enquiry to final box.</p>"),
    ] + SHARED_FAQS
    faq_html, faq_schema = faq_block(faqs, heading="Suffolk Removals — Common Questions", bg="bg-lightgrey")
    body += "\n" + faq_html
    body += "\n" + cta_band("Moving Anywhere in Suffolk?",
                            "Wherever you are in the county, we&rsquo;ll give you a clear, no-obligation quote. Call 01473 411531 or request one online.",
                            "Get a Free Quote", "/get-a-quote/", bg="bg-white")
    doc = E.render_page(
        title="Removals in Suffolk | Orwell Removals & Storage",
        description="Family-run removals and storage across the whole of Suffolk since 2005. Home, office & commercial moves, packing and storage, fully covered. Free quotes.",
        canonical_path="/locations/suffolk-removals/", body=body,
        og_image="images/photos/orwell-box-lorry-ipswich-street.webp",
        breadcrumb=[("Home", "/"), ("Locations", "/locations/"), ("Suffolk", "/locations/suffolk-removals/")],
        extra_schema=[faq_schema], active="locations")
    return E.write("locations/suffolk-removals/index.html", doc)

# ---------------------------------------------------------------- /locations/ index
def locations_index():
    cards = [(f"Removals in {TOWNS[s][0]}", f"/locations/{s}/",
              f"<p>{TOWNS[s][0]} ({TOWNS[s][1]}) &mdash; local, fully covered removals and storage.</p>") for s in ORDER]
    body = "\n".join([
        E.hero("Areas We Cover in Suffolk",
               "Find local removals and storage in your Suffolk town &mdash; family-run, fully covered, and trusted "
               "since 2005.",
               _photo("orwell-lorry-van-outside-home"), kicker="Areas we cover", cta=True),
        section(prose(
            '<h2 class="relative leading-tight text-black">Local Removals Across Suffolk</h2>'
            '<p>Orwell Removals &amp; Storage covers the whole of <a href="/locations/suffolk-removals/">Suffolk</a> from '
            'our base in <a href="/locations/ipswich-removals/">Westerfield, Ipswich</a>. Choose your town below for '
            'local detail, or <a href="/get-a-quote/">get a free quote</a> for your move &mdash; every job is '
            '<strong>fully covered</strong> and handled by the same friendly local team.</p>'), bg="bg-white"),
        card_grid(cards, cols=4, heading="Suffolk Towns We Cover", reveal=True,
                  intro='Don&rsquo;t see your village? We cover the surrounding areas too &mdash; just '
                        '<a href="/contact-us/">ask</a>.', bg="bg-lightgrey"),
        E.trusted_by("bg-white"),
    ])
    faqs = [
        ("Which Suffolk towns do you cover?",
         '<p>We cover the whole county from our Westerfield base &mdash; including '
         '<a href="/locations/ipswich-removals/">Ipswich</a>, '
         '<a href="/locations/felixstowe-removals/">Felixstowe</a>, '
         '<a href="/locations/woodbridge-removals/">Woodbridge</a>, '
         '<a href="/locations/bury-st-edmunds-removals/">Bury St Edmunds</a> and '
         '<a href="/locations/lowestoft-removals/">Lowestoft</a> &mdash; plus the villages in between.</p>'),
        ("What if my village isn&rsquo;t listed?",
         '<p>We almost certainly still cover it. Our town pages are just a guide &mdash; we move people across the whole '
         'of <a href="/locations/suffolk-removals/">Suffolk</a> and surrounding areas. Just '
         '<a href="/contact-us/">ask</a>.</p>'),
    ] + SHARED_FAQS
    faq_html, faq_schema = faq_block(faqs, heading="Areas We Cover — Common Questions", bg="bg-lightgrey")
    body += "\n" + faq_html
    body += "\n" + cta_band("Moving in Suffolk?",
                            "Tell us your town and we&rsquo;ll give you a clear, no-obligation quote.",
                            "Get a Free Quote", "/get-a-quote/", bg="bg-white")
    doc = E.render_page(
        title="Areas We Cover in Suffolk | Orwell Removals & Storage",
        description="Areas we cover for removals and storage across Suffolk — Ipswich, Felixstowe, Woodbridge, Bury St Edmunds, Lowestoft and more. Family-run, fully covered.",
        canonical_path="/locations/", body=body,
        og_image="images/photos/orwell-lorry-van-outside-home.webp",
        breadcrumb=[("Home", "/"), ("Locations", "/locations/")],
        extra_schema=[faq_schema], active="locations")
    return E.write("locations/index.html", doc)

def build():
    print("wrote", os.path.relpath(locations_index(), E.S.ROOT))
    print("wrote", os.path.relpath(county_hub(), E.S.ROOT))
    for s in ORDER:
        print("wrote", os.path.relpath(town_page(s), E.S.ROOT))

if __name__ == "__main__":
    build()
