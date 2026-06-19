# -*- coding: utf-8 -*-
"""Service pages for Orwell Removals & Storage — original content (NOT copied from any other site).
Services hub + 8 service pages + 2 storage sub-pages. Each indexable service page:
>=1000 words, unique title/desc/H1, keyword in H1 + first paragraph, MovingCompany + FAQPage
schema, >=10 in-body internal links, topic-matched images, "fully covered" (never insured).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
from engine import esc, icon, img, section, prose, card_grid, cta_band, faq_block

B = E.S.BUSINESS
PH = {p[0]: p for p in E.PHOTOS}
def _photo(slug): return PH.get(slug, E.PHOTOS[0])

# master service directory: slug -> (title, href, short desc) for related grids + hub
SVC = {
    "home-removals": ("Home Removals", "/services/home-removals/", "Careful, fully managed house moves of any size across Ipswich and Suffolk."),
    "office-removals": ("Office Removals", "/services/office-removals/", "Planned, low-downtime business moves, often out of hours."),
    "commercial-removals": ("Commercial Removals", "/services/commercial-removals/", "Stock, equipment and furniture moved with our Euro 6 fleet."),
    "long-distance-removals": ("Long Distance Removals", "/services/long-distance-removals/", "Door-to-door relocations out of Suffolk and across the UK."),
    "man-and-van": ("Man &amp; Van", "/services/man-and-van/", "Cost-effective help for smaller jobs and single items."),
    "piano-removals": ("Piano Removals", "/services/piano-removals/", "Uprights and grands moved safely by a trained team."),
    "packing-service": ("Packing Service", "/services/packing-service/", "Expert packing and quality materials for a faster, safer move."),
    "storage": ("Storage", "/services/storage/", "Clean, dry, secure containerised storage at our Westerfield base."),
    "household-storage": ("Household Storage", "/services/storage/household-storage/", "Flexible household storage between moves or while you renovate."),
    "business-storage": ("Business Storage", "/services/storage/business-storage/", "Secure, managed storage for stock, archives and equipment."),
}

def _hero(h1, lead, photo, kicker):
    return E.hero(h1, lead, _photo(photo), kicker=kicker, cta=True)

def _related(slugs, heading="Related Services"):
    cards = [SVC[s] for s in slugs]
    cards = [(t, h, f"<p>{d}</p>") for (t, h, d) in cards]
    return card_grid(cards, cols=len(cards) if len(cards) in (2, 3, 4) else 3,
                     heading=heading, intro="More ways our local team can help with your move.",
                     bg="bg-lightgrey", reveal=True, variant="service")

def _areas():
    towns = E.S.load_locations()
    pills = "".join(
        f'<a href="/{p}" class="px-4 py-2 rounded-full border border-border bg-white hover:border-orange hover:text-orange font-semibold text-sm">{esc(n)}</a>'
        for p, n in towns)
    return section(
        '<div class="grid grid-cols-12"><div class="col-span-12 lg:col-span-10 lg:col-start-2 text-center">'
        '<h2 class="relative leading-tight text-black">Where We Provide This Service</h2>'
        '<p class="text-lg xl:text-xl font-medium mt-2">Across the whole of '
        '<a href="/locations/suffolk-removals/">Suffolk</a>, from our base in '
        '<a href="/locations/ipswich-removals/">Westerfield, Ipswich</a>:</p>'
        f'<div class="flex flex-wrap gap-2 justify-center mt-6">{pills}</div></div></div>',
        bg="bg-white", extra="logo-row overflow-hidden")

# Storage pages should show STORAGE imagery (vaults, containers, warehouse, depot) — keep them
# to that sub-theme so a removals van never lands beside "secure container storage" copy.
_STORAGE_KW = ("vault", "container", "warehouse", "depot", "stored", "crate", "racking",
               "storage room", "storage area", "storage facility", "storage unit",
               "storage cage", "storage space", "storage building", "storage yard")
STORAGE_PREFER = set(p[0] for p in E.PHOTOS if any(k in p[1].lower() for k in _STORAGE_KW))

def service_page(s):
    h1 = s.get("h1") or (s["name"] + " in Ipswich &amp; Suffolk")
    # bias every image on the page toward this service's subject (e.g. "Packing Service Packing")
    topic = s["name"] + " " + s.get("topic", "")
    is_storage = "storage" in s["slug"]
    prefer = STORAGE_PREFER if is_storage else None
    # The hero image must match the page TITLE/subject (piano page -> piano, office -> office...).
    _hq = ("secure storage containers and vaults at the depot" if is_storage
           else s["name"] + " " + s["name"] + " " + s.get("topic", ""))
    _hm = E.match_photo(_hq, salt=s["slug"] + "-hero", prefer=prefer)
    hero_slug = _hm[0] if _hm else s["photo"]
    feat_photo = (E.match_photo(E._strip_tags(s.get("intro", "")) + " " + topic, salt=s["slug"] + "-feat", prefer=prefer)
                  or E.page_photos(s["slug"] + "-f", 1)[0])
    # Expanded body copy (long enough that each text block ~ matches its photo's height) lives in
    # data/service_bodies/<slug>.html when present; otherwise fall back to the inline bodyhtml.
    _bf = os.path.join(E.S.ROOT, "data", "service_bodies", s["slug"] + ".html")
    bodyhtml = open(_bf, encoding="utf-8").read().strip() if os.path.exists(_bf) else s["bodyhtml"]
    body = "\n".join([
        _hero(h1, s["lead"], hero_slug, s["kicker"]),
        section(prose(s["intro"]), bg="bg-white", extra="logo-row overflow-hidden"),
        E.media_rows(bodyhtml, seed=s["slug"], bg="bg-beige", topic=topic, prefer=prefer),
        E.wolves_feature_panel(feat_photo, reverse=True, bg="bg-white", name=s["name"]),
        E.step_process(bg="bg-lightgrey", topic=s.get("topic", "Removal")),
        _related(s["related"]),
        E.trusted_by("bg-white"),
        _areas(),
    ])
    faq_html, faq_schema = faq_block(s["faqs"], heading=s["faqheading"], bg="bg-beige")
    body += "\n" + faq_html
    body += "\n" + cta_band(s["ctah"], s["ctat"], "Get a Free Quote", "/get-a-quote/", bg="bg-white")
    doc = E.render_page(title=s["title"], description=s["desc"], canonical_path=s["canon"],
                        body=body, og_image="images/photos/" + hero_slug + ".webp",
                        breadcrumb=[("Home", "/"), ("Services", "/services/"), (s["name"], s["canon"])],
                        extra_schema=[faq_schema], active="services")
    return E.write(s["canon"].strip("/") + "/index.html", doc)

# ---------------------------------------------------------------- service specs
SERVICES = [
{
 "slug": "home-removals", "name": "Home Removals", "canon": "/services/home-removals/",
 "title": "Home Removals in Ipswich & Suffolk | Orwell",
 "desc": "Careful home removals in Ipswich and across Suffolk from family-run Orwell Removals & Storage. Packing, dismantling and storage. Fully covered. Free quotes.",
 "photo": "orwell-crew-loading-townhouse", "kicker": "Home moves done properly",
 "topic": "Removal", "related": ["packing-service", "storage", "man-and-van"],
 "lead": "Trusted home removals in Ipswich and across Suffolk &mdash; packed, moved and placed with care by our family-run team.",
 "intro": (
   '<h2 class="relative leading-tight text-black">Reliable Home Removals in Ipswich</h2>'
   '<p>When you need dependable <strong>home removals in Ipswich</strong>, Orwell Removals &amp; Storage takes the weight '
   'off your shoulders &mdash; literally. We have been moving Suffolk families since 2005, from first-time buyers leaving '
   'a flat to households downsizing after decades in the same home. Whatever the size of your move, the same friendly, '
   'uniformed team looks after it from the first box to the last, and every move is <strong>fully covered</strong> through '
   'Basil Fry, the removals-trade specialist.</p>'),
 "bodyhtml": (
   '<h2>Everything Handled, Start to Finish</h2>'
   '<p>A good house move is all in the preparation. We start with a free survey &mdash; in person or by a quick video '
   'walk-round &mdash; so we understand exactly what is moving and can give you a clear, fixed quote with no surprises. '
   'On the day, we protect your floors and doorways, blanket-wrap your furniture, and load everything methodically so it '
   'travels safely and comes off the van in the right order at the other end.</p>'
   '<h3>Packing and dismantling</h3>'
   '<p>You can pack yourself to keep costs down, or let us take care of it with our full '
   '<a href="/services/packing-service/">packing service</a> and quality materials. Our crew will dismantle beds, '
   'wardrobes and flat-pack furniture and rebuild it at your new home, so you are not left with an allen key and a '
   'headache on moving night.</p>'
   '<h3>When dates don&rsquo;t line up</h3>'
   '<p>Completion dates slip &mdash; it happens to almost everyone at some point. If there is a gap between moving out '
   'and moving in, our clean, dry <a href="/services/storage/">storage</a> at our Westerfield base bridges it, so a '
   'delayed chain never leaves you stranded with a van full of belongings and nowhere to go.</p>'
   '<h3>Local knowledge that saves you money</h3>'
   '<p>Because we are based in <a href="/locations/ipswich-removals/">Ipswich</a> and move across '
   '<a href="/locations/suffolk-removals/">Suffolk</a> every day, we know the narrow lanes of '
   '<a href="/locations/woodbridge-removals/">Woodbridge</a>, the terraces of '
   '<a href="/locations/felixstowe-removals/">Felixstowe</a> and the parking quirks of central Ipswich. That experience '
   'means we plan access properly and rarely lose time on the day &mdash; which keeps your move efficient and your '
   'quote keen. See our <a href="/pricing/">pricing</a> for how it all works.</p>'),
 "faqheading": "Home Removals — Common Questions",
 "faqs": [
   ("How much do home removals in Ipswich cost?",
    '<p>It depends on the size of your home, the distance, access and any packing or storage you need. The most accurate '
    'way to find out is a free quote &mdash; <a href="/get-a-quote/">request one here</a> or see our '
    '<a href="/pricing/">pricing page</a>.</p>'),
   ("Do you pack for me?",
    '<p>If you like. Many customers pack their own boxes and leave the furniture and breakables to us, while others '
    'choose our full <a href="/services/packing-service/">packing service</a> and don&rsquo;t lift a finger.</p>'),
   ("Are my belongings covered?",
    "<p>Yes &mdash; every move is fully covered, with goods-in-transit and public liability protection through Basil Fry, "
    "the removals-trade specialist.</p>"),
   ("Can you store my things if my move is delayed?",
    '<p>Absolutely. Our <a href="/services/storage/">secure storage</a> is ideal for bridging a gap between completion '
    'dates &mdash; just let us know and we&rsquo;ll arrange it.</p>'),
 ],
 "ctah": "Planning a House Move in Suffolk?",
 "ctat": "Tell us about your move and we&rsquo;ll give you a clear, no-obligation quote. Call 01473 411531 or request a quote online.",
},
{
 "slug": "office-removals", "name": "Office Removals", "canon": "/services/office-removals/",
 "title": "Office Removals in Ipswich & Suffolk | Orwell",
 "desc": "Office removals in Ipswich and Suffolk with minimal downtime. Planned, out-of-hours business moves from family-run Orwell Removals & Storage. Free quote.",
 "photo": "orwell-van-packing-moving-storage", "kicker": "Minimal downtime",
 "topic": "Commercial Removal", "related": ["commercial-removals", "storage", "packing-service"],
 "lead": "Office removals in Ipswich planned around your business &mdash; so you&rsquo;re up and running fast, with minimal downtime.",
 "intro": (
   '<h2 class="relative leading-tight text-black">Office Removals in Ipswich, Planned Around You</h2>'
   '<p>A smooth <strong>office removal in Ipswich</strong> comes down to planning, and that is exactly what we do best. '
   'Orwell Removals &amp; Storage relocates offices and workplaces across Suffolk with as little disruption to your '
   'business as possible &mdash; often in the evenings or over a weekend, so your team logs off in one office and back '
   'on in the next. Every move is <strong>fully covered</strong>, and managed by one point of contact from survey to '
   'sign-off.</p>'),
 "bodyhtml": (
   '<h2>A Business Move Without the Headache</h2>'
   '<p>We begin with a site survey and a simple plan: what moves, when, in what order, and how it is labelled so it lands '
   'in the right place at the new address. Desks, pedestals, storage and meeting-room furniture are wrapped and moved '
   'methodically, and we work to your timetable rather than ours.</p>'
   '<h3>IT, files and the things that matter</h3>'
   '<p>Computers, monitors and server kit are handled with care and can be crated where needed. Filing and archives are '
   'kept in order and, if you are short of space at the new site, our <a href="/services/storage/business-storage/">'
   'business storage</a> keeps overflow secure and accessible. Sensitive documents stay with you or are moved exactly '
   'as you instruct.</p>'
   '<h3>Out of hours to protect your trading</h3>'
   '<p>For many businesses the cost of downtime dwarfs the cost of the move, so we routinely work evenings, weekends and '
   'quiet periods. Our modern <strong>Euro&nbsp;6 fleet</strong> and experienced crews mean we move quickly without '
   'cutting corners. Bigger relocation? Our <a href="/services/commercial-removals/">commercial removals</a> team '
   'handles shops, warehouses and larger sites too.</p>'
   '<h3>Across Suffolk and beyond</h3>'
   '<p>From offices in central <a href="/locations/ipswich-removals/">Ipswich</a> to business parks around '
   '<a href="/locations/bury-st-edmunds-removals/">Bury St Edmunds</a> and '
   '<a href="/locations/stowmarket-removals/">Stowmarket</a>, we cover the county &mdash; and we handle '
   '<a href="/services/long-distance-removals/">longer-distance</a> business relocations when you are moving further '
   'afield.</p>'),
 "faqheading": "Office Removals — Common Questions",
 "faqs": [
   ("Can you move our office out of hours?",
    "<p>Yes &mdash; evenings and weekends are our speciality for business moves, so your team experiences as little "
    "downtime as possible.</p>"),
   ("Do you move IT equipment?",
    "<p>We do. Computers, monitors and server equipment are handled carefully and crated where needed. We&rsquo;ll plan "
    "the IT move with you so nothing critical is left to chance.</p>"),
   ("Can you store equipment or files during the move?",
    '<p>Yes &mdash; our <a href="/services/storage/business-storage/">business storage</a> is ideal for overflow, '
    'archives or staged moves.</p>'),
   ("How do you keep downtime to a minimum?",
    "<p>With a clear plan, labelled crates, the right crew size and a move scheduled around your trading hours. One "
    "coordinator manages it all from start to finish.</p>"),
 ],
 "ctah": "Relocating Your Office or Workplace?",
 "ctat": "Let&rsquo;s plan a move around your business. Call 01473 411531 or request a free, no-obligation quote.",
},
{
 "slug": "commercial-removals", "name": "Commercial Removals", "canon": "/services/commercial-removals/",
 "title": "Commercial Removals in Ipswich & Suffolk | Orwell",
 "desc": "Commercial removals in Ipswich and Suffolk — shops, warehouses and business premises moved efficiently by Orwell Removals & Storage. Euro 6 fleet. Free quote.",
 "photo": "orwell-commercial-shop-move", "kicker": "Any size, any sector",
 "topic": "Commercial Removal", "related": ["office-removals", "storage", "long-distance-removals"],
 "lead": "Commercial removals in Ipswich and Suffolk &mdash; shops, warehouses and premises moved efficiently, with minimal disruption to trade.",
 "intro": (
   '<h2 class="relative leading-tight text-black">Commercial Removals Across Suffolk</h2>'
   '<p>From a single shop fit-out to a full warehouse relocation, our <strong>commercial removals in Ipswich</strong> '
   'and across Suffolk keep your business moving. Orwell Removals &amp; Storage has the crews, the equipment and the '
   'modern <strong>Euro&nbsp;6 fleet</strong> to shift stock, fixtures, equipment and furniture quickly and safely '
   '&mdash; and every job is <strong>fully covered</strong> for peace of mind.</p>'),
 "bodyhtml": (
   '<h2>Built for Business Moves of Every Size</h2>'
   '<p>Commercial moves are rarely just &ldquo;furniture from A to B&rdquo;. There is stock to inventory, equipment to '
   'protect, and a deadline that usually can&rsquo;t slip. We survey the site, agree a plan and a timetable, and bring '
   'the right number of people and vehicles so the job is done in the window you have.</p>'
   '<h3>Stock, fixtures and equipment</h3>'
   '<p>We move shelving, display units, retail stock, catering and gym equipment, machinery and more. Fragile or '
   'high-value items are wrapped, padded and crated as needed, and we can phase a move so part of your operation keeps '
   'running while the rest relocates.</p>'
   '<h3>Storage and staged relocations</h3>'
   '<p>Not everything always needs to arrive at once. Our <a href="/services/storage/business-storage/">business '
   'storage</a> lets you stage a move, hold overflow stock or store fixtures between sites &mdash; clean, dry and '
   'secure at our Westerfield base.</p>'
   '<h3>Local, and further afield</h3>'
   '<p>We cover commercial premises throughout <a href="/locations/suffolk-removals/">Suffolk</a> &mdash; from '
   '<a href="/locations/felixstowe-removals/">Felixstowe</a>&rsquo;s port businesses to high streets in '
   '<a href="/locations/sudbury-removals/">Sudbury</a> &mdash; and handle '
   '<a href="/services/long-distance-removals/">long-distance</a> business relocations too. For smaller workplaces, see '
   'our <a href="/services/office-removals/">office removals</a>.</p>'),
 "faqheading": "Commercial Removals — Common Questions",
 "faqs": [
   ("What kinds of business do you move?",
    "<p>Shops, offices, warehouses, gyms, cafes and more. If it needs moving carefully and on schedule, we can help "
    "&mdash; tell us about your premises and we&rsquo;ll plan it.</p>"),
   ("Can you phase the move to keep us trading?",
    "<p>Yes. We often stage commercial moves so part of your operation keeps running while the rest relocates, and we "
    "work outside your busy hours where it helps.</p>"),
   ("Do you handle heavy or specialist equipment?",
    "<p>We do, with the right crew and equipment. Let us know what&rsquo;s involved at survey stage so we plan the "
    "lifting and protection properly.</p>"),
   ("Is our stock covered in transit?",
    "<p>Yes &mdash; every commercial move is fully covered, with goods-in-transit and public liability protection "
    "through Basil Fry, the removals-trade specialist.</p>"),
 ],
 "ctah": "Moving Your Business Premises?",
 "ctat": "Tell us what&rsquo;s involved and we&rsquo;ll plan an efficient move. Call 01473 411531 or request a free quote.",
},
{
 "slug": "long-distance-removals", "name": "Long Distance Removals", "canon": "/services/long-distance-removals/",
 "title": "Long Distance Removals from Suffolk | Orwell",
 "desc": "Long distance removals from Ipswich and Suffolk to anywhere in the UK. Door-to-door, fully covered, carefully scheduled by Orwell Removals & Storage. Free quote.",
 "photo": "orwell-lorry-packing-moving-storage", "kicker": "Door to door, UK-wide",
 "topic": "Removal", "related": ["home-removals", "packing-service", "storage"],
 "lead": "Long distance removals from Suffolk to anywhere in the UK &mdash; door to door, fully covered and carefully scheduled.",
 "intro": (
   '<h2 class="relative leading-tight text-black">Long Distance Removals from Suffolk</h2>'
   '<p>Moving out of the county? Our <strong>long distance removals from Suffolk</strong> take the stress out of a big '
   'relocation. Whether you are heading to London, the Midlands, the West Country or the North, Orwell Removals &amp; '
   'Storage plans a smooth door-to-door move with one dedicated team and one clear, fixed quote &mdash; and every mile '
   'is <strong>fully covered</strong>.</p>'),
 "bodyhtml": (
   '<h2>One Team, the Whole Way</h2>'
   '<p>Long-distance moves reward good planning. We survey your home, agree timings that work with your completion and '
   'travel, and load the van in a logical order so the unload at the far end is quick and calm. The same crew that packs '
   'your home sees it safely into your new one &mdash; no handovers, no strangers, no surprises.</p>'
   '<h3>Packing for the distance</h3>'
   '<p>Items travel further on a long-distance move, so packing matters even more. Our '
   '<a href="/services/packing-service/">packing service</a> protects everything properly for the journey, and we '
   'blanket-wrap and secure furniture so nothing shifts on the motorway.</p>'
   '<h3>Flexible timing and storage</h3>'
   '<p>Long chains and long distances don&rsquo;t always align. If your new place isn&rsquo;t ready, our '
   '<a href="/services/storage/">secure storage</a> holds your belongings until it is, and we&rsquo;ll deliver when the '
   'time is right. We&rsquo;ll talk you through the options when we quote.</p>'
   '<h3>Starting from Suffolk</h3>'
   '<p>We move people out of <a href="/locations/ipswich-removals/">Ipswich</a>, '
   '<a href="/locations/bury-st-edmunds-removals/">Bury St Edmunds</a>, '
   '<a href="/locations/lowestoft-removals/">Lowestoft</a> and right across '
   '<a href="/locations/suffolk-removals/">Suffolk</a> to destinations all over the country. Staying local instead? Our '
   '<a href="/services/home-removals/">home removals</a> cover moves within the county.</p>'),
 "faqheading": "Long Distance Removals — Common Questions",
 "faqs": [
   ("Do you move anywhere in the UK?",
    "<p>Yes &mdash; we carry out door-to-door long-distance removals from Suffolk to anywhere in mainland Britain.</p>"),
   ("Will the same team do the whole move?",
    "<p>Wherever possible, yes. The crew that loads your home travels with it and unloads at the other end, so nothing "
    "is lost in handovers.</p>"),
   ("Can you store our belongings if there&rsquo;s a delay?",
    '<p>Yes &mdash; our <a href="/services/storage/">storage</a> can hold everything securely until your new home is '
    'ready, then we deliver when it suits you.</p>'),
   ("Is a long-distance move covered?",
    "<p>Every move is fully covered, with goods-in-transit and public liability protection through Basil Fry, the "
    "removals-trade specialist &mdash; for the whole journey.</p>"),
 ],
 "ctah": "Moving Out of Suffolk?",
 "ctat": "Let&rsquo;s plan your long-distance move door to door. Call 01473 411531 or request a free, no-obligation quote.",
},
{
 "slug": "man-and-van", "name": "Man & Van", "canon": "/services/man-and-van/",
 "title": "Man & Van in Ipswich & Suffolk | Orwell Removals",
 "desc": "Reliable man and van service in Ipswich and Suffolk for small moves, single items and quick jobs. The care of a full removal, at a lower cost. Free quote.",
 "photo": "orwell-luton-van-ipswich-road", "kicker": "Small jobs, big care",
 "topic": "Man &amp; Van", "related": ["home-removals", "packing-service", "storage"],
 "lead": "A reliable man and van in Ipswich for smaller moves and single items &mdash; the care of a full removal, at a lower cost.",
 "intro": (
   '<h2 class="relative leading-tight text-black">Man &amp; Van in Ipswich &amp; Suffolk</h2>'
   '<p>Not every job needs a full removal crew. Our <strong>man and van service in Ipswich</strong> is the '
   'cost-effective way to move a few items, a small flat or a single piece of furniture &mdash; with exactly the same '
   'care, equipment and <strong>fully covered</strong> protection as our larger moves. It is the friendly, flexible '
   'option when you just need a reliable pair of hands and a clean van.</p>'),
 "bodyhtml": (
   '<h2>Flexible Help When You Need It</h2>'
   '<p>Moving out of a flat, shifting furniture to a relative, clearing a room or collecting a marketplace purchase? Our '
   'man and van service handles it without the cost of a full removal. We bring blankets, straps and trolleys, protect '
   'your items and your property, and get the job done efficiently.</p>'
   '<h3>What we can help with</h3>'
   '<p>Single items and small furniture, studio and one-bed moves, student moves, eBay and marketplace collections, '
   'tip runs of unwanted furniture, and those awkward jobs that are too big for the car but too small for a lorry. If '
   'you are not sure whether you need a man and van or a full <a href="/services/home-removals/">home removal</a>, just '
   'ask and we&rsquo;ll advise honestly.</p>'
   '<h3>Add packing or storage</h3>'
   '<p>Short of time? We can supply boxes or add our <a href="/services/packing-service/">packing service</a>. Need '
   'somewhere to put things for a while? Our <a href="/services/storage/">storage</a> is available by the week or the '
   'month, however long you need.</p>'
   '<h3>Across the county</h3>'
   '<p>Our man and van covers <a href="/locations/ipswich-removals/">Ipswich</a> and the wider county, including '
   '<a href="/locations/felixstowe-removals/">Felixstowe</a>, <a href="/locations/woodbridge-removals/">Woodbridge</a> '
   'and <a href="/locations/stowmarket-removals/">Stowmarket</a>. See <a href="/pricing/">how pricing works</a> for a '
   'guide.</p>'),
 "faqheading": "Man & Van — Common Questions",
 "faqs": [
   ("Is a man and van cheaper than a full removal?",
    '<p>For smaller jobs, yes &mdash; you only pay for the time and van you need. For a whole house, a full '
    '<a href="/services/home-removals/">home removal</a> is usually the better value. We&rsquo;ll advise honestly.</p>'),
   ("Can you move a single large item?",
    "<p>Of course &mdash; a sofa, a fridge, a wardrobe or a single awkward item is exactly what our man and van is for.</p>"),
   ("Do you bring blankets and trolleys?",
    "<p>Yes. We bring transit blankets, straps and trolleys as standard, and protect your items and property just as we "
    "would on a full move.</p>"),
   ("Are man-and-van jobs covered?",
    "<p>Yes &mdash; the same full cover applies, with goods-in-transit and public liability protection through Basil "
    "Fry, the removals-trade specialist.</p>"),
 ],
 "ctah": "Need a Reliable Man &amp; Van?",
 "ctat": "Tell us what you need moving and we&rsquo;ll give you a quick, fair price. Call 01473 411531 or request a quote.",
},
{
 "slug": "piano-removals", "name": "Piano Removals", "canon": "/services/piano-removals/",
 "title": "Piano Removals in Ipswich & Suffolk | Orwell",
 "desc": "Specialist piano removals in Ipswich and Suffolk. Uprights and grands moved safely by a trained Orwell Removals & Storage team. Fully covered. Free quote.",
 "photo": "mover-loading-van-on-driveway", "kicker": "Specialist, careful handling",
 "topic": "Removal", "related": ["home-removals", "man-and-van", "storage"],
 "lead": "Specialist piano removals in Ipswich and Suffolk &mdash; uprights and grands moved safely by a trained, experienced team.",
 "intro": (
   '<h2 class="relative leading-tight text-black">Specialist Piano Removals in Ipswich</h2>'
   '<p>A piano is heavy, valuable and often deeply sentimental, which is why <strong>piano removals in Ipswich</strong> '
   'are a job for an experienced team rather than a couple of willing friends. Orwell Removals &amp; Storage moves '
   'uprights and grands safely across Suffolk, with the right equipment, padding and know-how &mdash; and every move is '
   '<strong>fully covered</strong>.</p>'),
 "bodyhtml": (
   '<h2>The Right Way to Move a Piano</h2>'
   '<p>Pianos are awkward, top-heavy and easily damaged if handled poorly &mdash; and they can damage your home and your '
   'back too. Our trained crew uses proper piano trolleys, padding and straps, and plans the route through your home '
   'before anything moves, so doorways, corners and stairs are managed safely.</p>'
   '<h3>Uprights, grands and digitals</h3>'
   '<p>From a compact upright in a terrace to a baby grand up a flight of stairs, we assess each piano and bring the '
   'right approach and equipment. We protect the casework, secure the lid and keys, and move it steadily &mdash; no '
   'rushing, no shortcuts.</p>'
   '<h3>Part of a bigger move, or on its own</h3>'
   '<p>We move pianos as part of a full <a href="/services/home-removals/">home removal</a> or as a standalone job if '
   'the piano is all that&rsquo;s moving. If it needs to go into store for a while, our '
   '<a href="/services/storage/">clean, dry storage</a> keeps it safe (pianos prefer a stable environment to a damp '
   'garage).</p>'
   '<h3>Across Suffolk</h3>'
   '<p>We carry out piano moves throughout <a href="/locations/suffolk-removals/">Suffolk</a>, from '
   '<a href="/locations/ipswich-removals/">Ipswich</a> to <a href="/locations/bury-st-edmunds-removals/">Bury St '
   'Edmunds</a>. For smaller single items, our <a href="/services/man-and-van/">man &amp; van</a> service may suit.</p>'),
 "faqheading": "Piano Removals — Common Questions",
 "faqs": [
   ("Can you move an upright and a grand piano?",
    "<p>Yes &mdash; we move uprights, baby grands and grands, with the right trolleys, padding and trained crew for each.</p>"),
   ("Can you move a piano up or down stairs?",
    "<p>In most cases, yes. We assess the access at quote stage and plan the route and equipment carefully before "
    "moving day.</p>"),
   ("Will you move just the piano?",
    "<p>Of course. We&rsquo;re happy to move a piano on its own, or as part of a larger house move.</p>"),
   ("Is my piano covered during the move?",
    "<p>Yes &mdash; every move is fully covered, with goods-in-transit and public liability protection through Basil "
    "Fry, the removals-trade specialist.</p>"),
 ],
 "ctah": "Need a Piano Moved Safely?",
 "ctat": "Tell us about your piano and where it&rsquo;s going. Call 01473 411531 or request a free, no-obligation quote.",
},
{
 "slug": "packing-service", "name": "Packing Service", "canon": "/services/packing-service/",
 "title": "Packing Service in Ipswich & Suffolk | Orwell",
 "desc": "Professional packing service in Ipswich and Suffolk. Let Orwell Removals & Storage pack your home with quality materials, or buy boxes and pack yourself. Free quote.",
 "photo": "wrapped-packing-materials-ready", "kicker": "Packed properly, moved safely",
 "topic": "Packing", "related": ["home-removals", "storage", "long-distance-removals"],
 "lead": "A professional packing service in Ipswich and Suffolk &mdash; quality materials, careful hands and a faster, safer move.",
 "intro": (
   '<h2 class="relative leading-tight text-black">Professional Packing Service in Ipswich</h2>'
   '<p>Packing is the most time-consuming part of any move, and the part that decides whether your belongings arrive '
   'intact. Our <strong>packing service in Ipswich</strong> takes it off your hands entirely &mdash; or supplies the '
   'materials so you can pack at your own pace. Either way, everything is wrapped properly so it travels safely, and '
   'your whole move stays <strong>fully covered</strong>.</p>'),
 "bodyhtml": (
   '<h2>Let Us Pack, or Pack It Yourself</h2>'
   '<p>Our trained team can pack your entire home quickly and methodically, room by room, labelling as we go so the '
   'unpack is just as easy. We use quality boxes, bubble wrap, packing paper, wardrobe cartons and tape &mdash; the '
   'right material for each item rather than a one-size-fits-all approach.</p>'
   '<h3>Fragile and valuable items</h3>'
   '<p>Glassware, china, pictures, mirrors and electronics get extra attention, wrapped and cushioned so they survive '
   'the journey. For especially delicate or high-value pieces we can crate or double-box, and we&rsquo;ll always flag '
   'anything we think needs special care.</p>'
   '<h3>Materials to buy, and unpacking too</h3>'
   '<p>Prefer to pack yourself? We can supply strong, removal-grade boxes and materials so you are not relying on '
   'flimsy supermarket cartons. And if you&rsquo;d like a hand at the other end, we can unpack and take the empty boxes '
   'away, so you settle in faster.</p>'
   '<h3>Part of your move</h3>'
   '<p>Packing works hand in hand with our <a href="/services/home-removals/">home removals</a> and '
   '<a href="/services/long-distance-removals/">long-distance moves</a>, and pairs neatly with '
   '<a href="/services/storage/">storage</a> if your belongings need to wait. We pack homes throughout '
   '<a href="/locations/suffolk-removals/">Suffolk</a>, from <a href="/locations/ipswich-removals/">Ipswich</a> '
   'outwards.</p>'),
 "faqheading": "Packing Service — Common Questions",
 "faqs": [
   ("Can you pack my whole house?",
    "<p>Yes &mdash; our team can pack everything, room by room, labelled and ready to move. Or we can pack just the "
    "fragile items and leave the rest to you.</p>"),
   ("Can I buy packing materials from you?",
    "<p>Yes. We supply strong, removal-grade boxes, paper, bubble wrap, tape and wardrobe cartons so you can pack at "
    "your own pace.</p>"),
   ("Do you unpack as well?",
    "<p>We can. Ask about our unpacking option and we&rsquo;ll help you settle in and take the empty boxes away.</p>"),
   ("Are self-packed boxes covered?",
    "<p>Cover applies to your move &mdash; we&rsquo;ll explain how it works for self-packed boxes versus items we pack "
    "ourselves at quote stage, so you know exactly where you stand.</p>"),
 ],
 "ctah": "Want a Faster, Safer Move?",
 "ctat": "Let us take the packing off your hands. Call 01473 411531 or request a free, no-obligation quote.",
},
{
 "slug": "storage", "name": "Storage", "canon": "/services/storage/",
 "title": "Secure Storage in Ipswich & Suffolk | Orwell",
 "desc": "Clean, dry, secure storage in Ipswich at Orwell Removals & Storage's Westerfield base. Household and business storage, short or long term. Free quote.",
 "photo": "van-loaded-boxes-wrapped-furniture", "kicker": "Clean, dry & secure",
 "topic": "Storage", "related": ["household-storage", "business-storage", "home-removals"],
 "lead": "Clean, dry, secure storage in Ipswich &mdash; for between moves, downsizing, renovations or simply freeing up space.",
 "intro": (
   '<h2 class="relative leading-tight text-black">Secure Storage in Ipswich &amp; Suffolk</h2>'
   '<p>Sometimes the move and the move-in don&rsquo;t happen on the same day &mdash; and sometimes you just need space. '
   'Our <strong>secure storage in Ipswich</strong>, at our Westerfield base, gives you a clean, dry, well-protected '
   'place for your belongings for as long or as little as you need. Whether it is a few boxes or a whole household, '
   'everything is wrapped, logged and looked after.</p>'),
 "bodyhtml": (
   '<h2>Storage That Works Around Your Move</h2>'
   '<p>Storage is most useful exactly when moving gets complicated: a completion date slips, a renovation overruns, '
   'you&rsquo;re downsizing and not ready to part with things, or you&rsquo;re moving abroad and need belongings held. '
   'We can collect, store and redeliver, so storage fits seamlessly into your move rather than becoming another chore.</p>'
   '<h3>Clean, dry and protected</h3>'
   '<p>Your belongings are wrapped and stored carefully at our Westerfield premises, kept clean and dry &mdash; the '
   'right environment for furniture, boxes and even a <a href="/services/piano-removals/">piano</a>, which much prefers '
   'stable storage to a damp garage. We keep an inventory so we know exactly what we&rsquo;re holding for you.</p>'
   '<h3>Household and business</h3>'
   '<p>We store for homes and businesses alike. For families, see our '
   '<a href="/services/storage/household-storage/">household storage</a>; for stock, archives and equipment, our '
   '<a href="/services/storage/business-storage/">business storage</a> keeps your operation tidy and your overflow '
   'secure.</p>'
   '<h3>Short term or long term</h3>'
   '<p>Store by the week or the month, for a few days between moves or for the long haul. Combine it with our '
   '<a href="/services/home-removals/">home removals</a> and <a href="/services/packing-service/">packing</a> for a '
   'move that&rsquo;s handled end to end. We store for customers right across '
   '<a href="/locations/suffolk-removals/">Suffolk</a>.</p>'),
 "faqheading": "Storage — Common Questions",
 "faqs": [
   ("How long can I store my belongings?",
    "<p>As long or as little as you like &mdash; by the week or the month, for a few days between moves or for the long "
    "term. There&rsquo;s no pressure to commit to a fixed period.</p>"),
   ("Is the storage clean and dry?",
    "<p>Yes &mdash; your belongings are wrapped and kept clean and dry at our Westerfield base, in the right "
    "environment for furniture and boxes.</p>"),
   ("Can you collect and deliver my things?",
    '<p>We can. We&rsquo;ll collect, store and redeliver as part of your move &mdash; combine it with our '
    '<a href="/services/home-removals/">removals</a> and <a href="/services/packing-service/">packing</a>.</p>'),
   ("Is stored property covered?",
    "<p>We&rsquo;ll explain the cover for stored goods when you enquire, so you know exactly how your belongings are "
    "protected while they&rsquo;re with us.</p>"),
 ],
 "ctah": "Need Storage in Ipswich or Suffolk?",
 "ctat": "Tell us what you need to store and for how long. Call 01473 411531 or request a free, no-obligation quote.",
},
{
 "slug": "household-storage", "name": "Household Storage", "canon": "/services/storage/household-storage/",
 "title": "Household Storage in Ipswich & Suffolk | Orwell",
 "desc": "Flexible household storage in Ipswich for between moves, downsizing or renovations. Clean, dry, secure storage from Orwell Removals & Storage. Free quote.",
 "photo": "wrapped-furniture-and-boxes", "kicker": "Flexible household storage",
 "topic": "Storage", "related": ["storage", "business-storage", "home-removals"],
 "lead": "Flexible household storage in Ipswich &mdash; clean, dry and secure space for your home&rsquo;s belongings, for as long as you need.",
 "intro": (
   '<h2 class="relative leading-tight text-black">Household Storage in Ipswich</h2>'
   '<p>Life doesn&rsquo;t always run to the property market&rsquo;s timetable. Our <strong>household storage in '
   'Ipswich</strong> gives families a clean, dry, secure place to keep furniture and boxes between moves, while '
   'downsizing, during a renovation or simply when the house needs breathing space. Everything is wrapped, logged and '
   'looked after at our Westerfield base.</p>'),
 "bodyhtml": (
   '<h2>When Household Storage Helps</h2>'
   '<p>The classic moment is a chain that doesn&rsquo;t complete on the same day &mdash; you have to be out, but you '
   'can&rsquo;t get in. Storage bridges that gap. It&rsquo;s just as useful when you&rsquo;re downsizing and not ready '
   'to let things go, renovating and need rooms cleared, or heading overseas and want belongings kept safely at home.</p>'
   '<h3>Looked after, not just left</h3>'
   '<p>Your furniture is wrapped and stored carefully, kept clean and dry &mdash; not piled in a damp lock-up. We keep '
   'an inventory of what we&rsquo;re holding, so retrieving an item or planning your redelivery is straightforward.</p>'
   '<h3>Collected, stored, redelivered</h3>'
   '<p>Because storage usually goes hand in hand with a move, we can collect with our '
   '<a href="/services/home-removals/">home removals</a> team, store for as long as you need, and redeliver when '
   'you&rsquo;re ready. Add <a href="/services/packing-service/">packing</a> and the whole thing is handled for you.</p>'
   '<h3>Flexible terms across Suffolk</h3>'
   '<p>Store by the week or the month, with no pressure to commit to a long contract. We help households throughout '
   '<a href="/locations/suffolk-removals/">Suffolk</a>, from <a href="/locations/ipswich-removals/">Ipswich</a> to '
   '<a href="/locations/woodbridge-removals/">Woodbridge</a>. For stock and equipment instead, see our '
   '<a href="/services/storage/business-storage/">business storage</a>.</p>'),
 "faqheading": "Household Storage — Common Questions",
 "faqs": [
   ("Is household storage good for a delayed completion?",
    "<p>Ideal for it. If you have to move out before you can move in, we&rsquo;ll store everything and redeliver the "
    "moment your new home is ready.</p>"),
   ("How much can I store?",
    "<p>From a few boxes to a whole household. Tell us roughly what you have and we&rsquo;ll advise on space and cost.</p>"),
   ("Can I access my belongings while they&rsquo;re stored?",
    "<p>Just let us know what you need and when &mdash; we keep an inventory so retrieving items is straightforward.</p>"),
   ("Do I need a long contract?",
    "<p>No &mdash; store by the week or the month, for as long or as little as you need.</p>"),
 ],
 "ctah": "Need Household Storage?",
 "ctat": "Tell us what you need to store and for how long. Call 01473 411531 or request a free, no-obligation quote.",
},
{
 "slug": "business-storage", "name": "Business Storage", "canon": "/services/storage/business-storage/",
 "title": "Business Storage in Ipswich & Suffolk | Orwell",
 "desc": "Secure business storage in Ipswich for stock, archives, equipment and office furniture. Fully managed storage from Orwell Removals & Storage. Free quote.",
 "photo": "orwell-boxes-loaded-in-van", "kicker": "Secure, managed storage",
 "topic": "Storage", "related": ["storage", "household-storage", "commercial-removals"],
 "lead": "Secure business storage in Ipswich for stock, archives, equipment and office furniture &mdash; fully managed, and easy to access.",
 "intro": (
   '<h2 class="relative leading-tight text-black">Business Storage in Ipswich</h2>'
   '<p>Growing businesses run out of space, and moving businesses need somewhere to stage. Our <strong>business storage '
   'in Ipswich</strong> gives you clean, dry, secure room for stock, archives, equipment and office furniture at our '
   'Westerfield base &mdash; fully managed, properly logged and ready when you need it.</p>'),
 "bodyhtml": (
   '<h2>Storage That Keeps Your Business Tidy</h2>'
   '<p>Whether you&rsquo;re overflowing with seasonal stock, clearing an office, archiving paperwork you must keep, or '
   'staging a relocation, business storage takes the pressure off your premises. We can collect, store and redeliver, '
   'so it works around your operation rather than disrupting it.</p>'
   '<h3>Stock, archives and equipment</h3>'
   '<p>From retail stock and display fixtures to filing, IT equipment and surplus furniture, we store it carefully and '
   'keep an inventory so you always know what&rsquo;s held. It&rsquo;s a tidy, cost-effective alternative to renting '
   'extra floor space you only need part of the year.</p>'
   '<h3>Part of a business move</h3>'
   '<p>Business storage pairs naturally with our <a href="/services/commercial-removals/">commercial removals</a> and '
   '<a href="/services/office-removals/">office removals</a> &mdash; stage a move, hold overflow between sites, or keep '
   'archives off-site without losing access to them.</p>'
   '<h3>Flexible, local and secure</h3>'
   '<p>Store by the week or the month with terms that flex as your needs change. We support businesses throughout '
   '<a href="/locations/suffolk-removals/">Suffolk</a>, from <a href="/locations/ipswich-removals/">Ipswich</a> to '
   '<a href="/locations/bury-st-edmunds-removals/">Bury St Edmunds</a>. For home storage instead, see our '
   '<a href="/services/storage/household-storage/">household storage</a>.</p>'),
 "faqheading": "Business Storage — Common Questions",
 "faqs": [
   ("What can I store?",
    "<p>Stock, archives, IT equipment, display fixtures, office furniture and more &mdash; clean, dry and securely "
    "stored, with an inventory of what we hold.</p>"),
   ("Can you store during an office move?",
    '<p>Yes &mdash; business storage is ideal for staging a <a href="/services/office-removals/">move</a>, holding '
    'overflow or keeping archives off-site with easy access.</p>'),
   ("Are the terms flexible?",
    "<p>Yes &mdash; store by the week or the month, and scale up or down as your business needs change.</p>"),
   ("Can you collect and redeliver?",
    "<p>We can &mdash; we&rsquo;ll collect, store and redeliver as part of your move or whenever you need it.</p>"),
 ],
 "ctah": "Need Secure Business Storage?",
 "ctat": "Tell us what you need to store and we&rsquo;ll keep it safe. Call 01473 411531 or request a free quote.",
},
]

# ---------------------------------------------------------------- services hub
def services_hub():
    cards = [(SVC[s][0], SVC[s][1], f"<p>{SVC[s][2]}</p>")
             for s in ["home-removals", "office-removals", "commercial-removals", "long-distance-removals",
                       "man-and-van", "piano-removals", "packing-service", "storage"]]
    body = "\n".join([
        _hero("Our Removals &amp; Storage Services",
              "One local, family-run team for your whole move &mdash; removals, packing and storage across Ipswich and Suffolk.",
              "orwell-lorry-van-outside-home", "Removals, packing & storage"),
        section(prose(
            '<h2 class="relative leading-tight text-black">Removals &amp; Storage Services Across Suffolk</h2>'
            '<p>Orwell Removals &amp; Storage offers a complete range of <strong>removals and storage services in '
            'Ipswich</strong> and across Suffolk. From a single item with our '
            '<a href="/services/man-and-van/">man &amp; van</a> to a full <a href="/services/home-removals/">home '
            'removal</a>, an <a href="/services/office-removals/">office relocation</a> or clean, secure '
            '<a href="/services/storage/">storage</a>, every job is handled by the same friendly team and every move is '
            '<strong>fully covered</strong>. Whatever you need moving, we make it simple.</p>'),
            bg="bg-white", extra="logo-row overflow-hidden"),
        card_grid(cards, cols=4, heading="What We Do", bg="bg-lightgrey", reveal=True, variant="service",
                  intro="Pick a service to learn more, or "
                        '<a href="/get-a-quote/">get a free quote</a> for your move.'),
        E.step_process(bg="bg-beige"),
        E.trusted_by("bg-white"),
        _areas(),
    ])
    faqs = [
        ("What services do you offer?",
         '<p>Home, office and commercial removals, long-distance moves, man &amp; van, piano removals, professional '
         'packing and secure storage &mdash; all from one local, family-run team. Explore each above.</p>'),
        ("Do you cover my area?",
         '<p>We cover the whole of <a href="/locations/suffolk-removals/">Suffolk</a> from our Westerfield base near '
         '<a href="/locations/ipswich-removals/">Ipswich</a>, plus long-distance moves UK-wide.</p>'),
        ("How do I get a quote?",
         '<p>Call 01473 411531, email us, or <a href="/get-a-quote/">use our quick quote form</a>. Quotes and surveys '
         'are free, with no obligation.</p>'),
        ("Are your moves covered?",
         "<p>Yes &mdash; every move is fully covered, with goods-in-transit and public liability protection through "
         "Basil Fry, the removals-trade specialist.</p>"),
    ]
    faq_html, faq_schema = faq_block(faqs, heading="Our Services — Common Questions", bg="bg-lightgrey")
    body += "\n" + faq_html
    body += "\n" + cta_band("Ready to Get Moving?",
                            "Tell us what you need and we&rsquo;ll give you a clear, no-obligation quote. Call 01473 411531 or request a quote online.",
                            "Get a Free Quote", "/get-a-quote/", bg="bg-white")
    doc = E.render_page(
        title="Removals & Storage Services in Ipswich | Orwell",
        description="Removals and storage services in Ipswich & Suffolk from family-run Orwell: home, office & commercial moves, long distance, man & van, piano, packing, storage.",
        canonical_path="/services/", body=body,
        og_image="images/photos/orwell-lorry-van-outside-home.webp",
        breadcrumb=[("Home", "/"), ("Services", "/services/")],
        extra_schema=[faq_schema], active="services")
    return E.write("services/index.html", doc)

def build():
    print("wrote", os.path.relpath(services_hub(), E.S.ROOT))
    for s in SERVICES:
        print("wrote", os.path.relpath(service_page(s), E.S.ROOT))

if __name__ == "__main__":
    build()
