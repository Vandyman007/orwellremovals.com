# -*- coding: utf-8 -*-
"""Build the Orwell Removals & Storage home page (index.html).
SEO bible: unique title/H1, primary keyword in H1 + first paragraph, LocalBusiness +
FAQPage schema, >=10 in-body internal links, E-E-A-T trust signals, alt+dims on images.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
from engine import esc, icon, img, section, card_grid, cta_band, faq_block

HERO_IMG = "images/photos/orwell-box-lorry-ipswich-street.webp"  # primary (OG + LCP preload)
HERO_SLIDES = [
    ("orwell-box-lorry-ipswich-street", "Orwell Removals box lorry on a residential street in Ipswich"),
    ("orwell-box-lorry-ipswich-street", "Orwell Removals lorries at the Westerfield depot near Ipswich"),
    ("orwell-van-on-customer-driveway", "An Orwell Removals van and lorry on a customer's driveway in Suffolk"),
]
_CHECK = ('<svg viewBox="0 0 24 24" class="w-5 h-5 shrink-0 text-green mt-1" fill="none" stroke="currentColor" '
          'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>')

def hero():
    bullets = ["Family-run Ipswich removals & storage since 2005",
               "Fully covered by Basil Fry, the removals-trade specialist",
               "Free, no-obligation quotes across the whole of Suffolk"]
    lis = "".join(f'<li class="flex items-start gap-2">{_CHECK}<span>{esc(t)}</span></li>' for t in bullets)
    bullets_ul = f'<ul class="space-y-2 text-base xl:text-lg list-none p-0">{lis}</ul>'
    # 3x3 Rubik mosaic of ONE hero image (shared engine builder: responsive tiles, assembles
    # on load via @keyframes pieceAssemble; assembled in the DOM so crawlers see the whole photo).
    return (
        '<section class="relative w-full bg-darkgrey text-white overflow-hidden flex items-center min-h-[30rem] lg:min-h-[36rem]">'
        f'{E.rubik_bg(HERO_SLIDES[0])}'
        '<div class="container relative z-10 w-full py-[3.6rem] lg:py-[7.2rem]"><div class="grid grid-cols-12"><div class="col-span-12 lg:col-span-7 lg:col-start-6 hero-panel">'
        '<h1 class="text-4xl lg:text-6xl font-bold leading-tight">Removals &amp; Storage in Ipswich</h1>'
        '<p class="mt-4 text-lg xl:text-xl max-w-xl">Looking for trusted removals and storage in Ipswich? Orwell Removals '
        '&amp; Storage is a family-run Suffolk team handling home and business moves, packing and secure storage &mdash; '
        'with the same friendly faces from your first call to the last box.</p>'
        f'{E.hero_review_row(bullets_ul)}'
        '</div></div></div></section>')

def intro():
    body = (
        '<h2 class="relative leading-tight text-black">Your Trusted Ipswich Removals &amp; Storage Team</h2>'
        '<p>Orwell Removals &amp; Storage is a trusted, <strong>family-run Ipswich removals company</strong> based at Old '
        'Station Works, Main Road, <a href="/locations/ipswich-removals/">Westerfield</a>, just north of Ipswich. We have '
        'been moving Suffolk households and businesses since 2005, and we cover the whole county &mdash; from '
        '<a href="/locations/felixstowe-removals/">Felixstowe</a> and '
        '<a href="/locations/woodbridge-removals/">Woodbridge</a> to '
        '<a href="/locations/bury-st-edmunds-removals/">Bury St Edmunds</a> and '
        '<a href="/locations/lowestoft-removals/">Lowestoft</a>. Every move is <strong>fully covered</strong> and '
        'handled by the same friendly local team, for complete peace of mind.</p>'
        '<p class="text-lg xl:text-xl font-medium">First impressions count &mdash; and when everything has to go right, '
        'Orwell Removals &amp; Storage is the Suffolk removals company to call.</p>')
    services_list = (
        '<p class="text-lg xl:text-xl font-medium mb-3">Our full range of services includes:</p>'
        '<ul class="tick-list reveal-swipe grid sm:grid-cols-2 gap-x-10 gap-y-1">'
        '<li><a href="/services/home-removals/">Home removals</a> and <a href="/services/office-removals/">office relocations</a></li>'
        '<li><a href="/services/commercial-removals/">Commercial removals</a> for businesses of every size</li>'
        '<li><a href="/services/long-distance-removals/">Long distance removals</a> across the UK</li>'
        '<li>Cost-effective <a href="/services/man-and-van/">man &amp; van</a> services</li>'
        '<li>Specialist <a href="/services/piano-removals/">piano removals</a></li>'
        '<li>Expert <a href="/services/packing-service/">packing</a> and clean, secure <a href="/services/storage/">storage</a></li>'
        '</ul>')
    inner = (
        '<div class="grid grid-cols-12 gap-y-8 lg:gap-12 items-start">'
        f'<div class="col-span-12 lg:col-span-7 text-black text-left">{body}</div>'
        f'<div class="col-span-12 lg:col-span-5 text-black text-left">{services_list}</div>'
        '</div>')
    return section(inner, bg="bg-white", extra="logo-row overflow-hidden")

def services():
    cards = [
        ("Home Removals", "/services/home-removals/",
         "<p>We pack, load and transport your belongings with real care, then place everything in your new home exactly where it needs to be.</p>"),
        ("Office Removals", "/services/office-removals/",
         "<p>Planned, out-of-hours office moves that keep your business running &mdash; IT, desks and files relocated with minimal downtime.</p>"),
        ("Commercial Removals", "/services/commercial-removals/",
         "<p>From shops to warehouses, we move stock, equipment and furniture efficiently with our modern Euro&nbsp;6 fleet.</p>"),
        ("Long Distance Removals", "/services/long-distance-removals/",
         "<p>Moving out of Suffolk? We handle long-distance UK relocations door to door, fully covered and carefully scheduled.</p>"),
        ("Man &amp; Van", "/services/man-and-van/",
         "<p>Need a few items moved quickly? Our cost-effective man &amp; van service brings the same care as a full move.</p>"),
        ("Piano Removals", "/services/piano-removals/",
         "<p>Upright or grand, our trained team moves pianos safely with the right equipment, padding and know-how.</p>"),
    ]
    return card_grid(cards, cols=3, heading="Our Removals &amp; Storage Services",
                     intro="From single items to full home and office moves, every job is handled by our trained, fully covered Ipswich team.",
                     bg="bg-lightgrey", reveal=True, variant="service")

def storage():
    cards = [
        ("Household Storage", "/services/storage/household-storage/",
         "<p>Clean, dry, alarmed storage for between moves, downsizing or renovations &mdash; flexible terms from a few days to long term.</p>"),
        ("Business Storage", "/services/storage/business-storage/",
         "<p>Secure storage for stock, equipment, archives and office furniture &mdash; fully managed, including packing and collection.</p>"),
        ("Secure Storage", "/services/storage/",
         "<p>Containerised storage at our Westerfield base near Ipswich, with your belongings wrapped, logged and looked after.</p>"),
    ]
    return card_grid(cards, cols=3, heading="Need Storage in Ipswich or Suffolk?",
                     intro="Our containerised storage is clean, dry and ultra-secure &mdash; for as long or as little as you need it.",
                     bg="bg-white",
                     bg_image=("packed-boxes-wrapped-furniture",
                               "Containerised storage units at the Orwell Removals & Storage store near Ipswich"),
                     reveal=True, spark=True)

def areas():
    towns = E.S.load_locations()[:8]
    pills = "".join(
        f'<a href="/{p}" class="px-5 py-2 rounded-full border border-border bg-white hover:border-orange hover:text-orange font-semibold">{esc(n)}</a>'
        for p, n in towns)
    return section(
        '<div class="grid grid-cols-12"><div class="col-span-12 lg:col-span-10 lg:col-start-2 text-center">'
        '<h2 class="relative leading-tight text-black">Areas We Cover Across Suffolk</h2>'
        '<p class="text-lg xl:text-xl font-medium mt-2">Based in Westerfield, we are perfectly placed to move homes and '
        'businesses right across <a href="/locations/suffolk-removals/">Suffolk</a>:</p>'
        f'<div class="flex flex-wrap gap-3 justify-center mt-6">{pills}</div>'
        '<p class="mt-6"><a class="font-bold uppercase text-black hover:text-orange inline-flex items-center gap-1" href="/locations/">'
        'See every town we cover ' + icon("chevron", "h-4 w-4 -rotate-90 fill-current") + '</a></p>'
        '</div></div>', bg="bg-white", extra="logo-row overflow-hidden")

FAQS = [
    ("How much do removals cost in Ipswich?",
     "<p>Removal costs depend on the size of your home, the distance, access and any packing or storage you need. "
     "A local two-bedroom move in and around Ipswich typically starts from a few hundred pounds. The most accurate "
     'way to find out is a free, no-obligation quote &mdash; <a href="/get-a-quote/">request yours here</a> or see our '
     '<a href="/pricing/">pricing page</a>.</p>'),
    ("Which areas of Suffolk do you cover?",
     '<p>We are based in <a href="/locations/ipswich-removals/">Westerfield, Ipswich</a> and cover the whole county, '
     'including <a href="/locations/felixstowe-removals/">Felixstowe</a>, '
     '<a href="/locations/woodbridge-removals/">Woodbridge</a>, '
     '<a href="/locations/bury-st-edmunds-removals/">Bury St Edmunds</a> and '
     '<a href="/locations/stowmarket-removals/">Stowmarket</a>. See <a href="/locations/">areas we cover</a> for your town.</p>'),
    ("Do you offer a packing service and materials?",
     '<p>Yes. Our team can take care of everything with a full <a href="/services/packing-service/">packing service</a>, '
     'or supply boxes and materials so you can pack at your own pace. Fragile and valuable items are wrapped and protected with care.</p>'),
    ("Are my belongings covered during the move?",
     "<p>Absolutely. Orwell Removals &amp; Storage is fully covered, with goods-in-transit and liability cover arranged "
     "through Basil Fry, the removals-trade specialist. Our modern Euro&nbsp;6 fleet and trained team keep your move clean, "
     "safe and efficient from start to finish.</p>"),
    ("Can you store my belongings between moves?",
     '<p>Yes &mdash; we offer clean, dry, secure containerised <a href="/services/storage/">storage</a> for both '
     '<a href="/services/storage/household-storage/">household</a> and '
     '<a href="/services/storage/business-storage/">business</a> needs, ideal when completion dates don&rsquo;t line up or while you renovate.</p>'),
]

def build():
    faq_html, faq_schema = faq_block(FAQS, heading="Common Removals & Storage Questions", bg="bg-white", fancy=True)
    body = "\n".join([
        hero(),
        intro(),
        E.quote_bar(),
        services(),
        storage(),
        E.standard_feature_panel(E.page_photos("home-feature-panel", 1)[0], reverse=False, bg="bg-beige"),
        areas(),
        E.step_process(bg="bg-beige"),
        E.trusted_by(),
        E.photo_strip(E.page_photos("home-gallery", 3),
                      heading="See Our Suffolk Movers in Action",
                      intro="Our trained, fully covered team on recent moves across Ipswich and Suffolk.", bg="bg-white"),
        cta_band("Interested in Our Services? Get In Touch for a Free Quote",
                 "Simply fill in our quick form, call us on 01473 411531 or email us and a friendly member of our team will be in touch.",
                 "Get a Free Quote", "/get-a-quote/", bg="bg-lightgrey"),
        faq_html,
    ])
    doc = E.render_page(
        title="Removals & Storage in Ipswich | Orwell Removals & Storage",
        description="Family-run removals and storage in Ipswich & Suffolk since 2005. Home, office & commercial moves, packing and secure storage. Fully covered. Free quotes.",
        canonical_path="/",
        body=body,
        og_image=HERO_IMG,
        breadcrumb=[("Home", "/")],
        extra_schema=[faq_schema],
        active="home",
    )
    out = E.write("index.html", doc)
    print("wrote", out, f"({len(doc):,} bytes)")

if __name__ == "__main__":
    build()
