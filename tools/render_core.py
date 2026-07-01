# -*- coding: utf-8 -*-
"""Core pages for Orwell Removals & Storage — original content (NOT copied from any other site).
about-us, pricing, FAQs, contact, get-a-quote, gallery, reviews, privacy, terms, 404.
SEO bible: unique title/desc/H1, keyword in H1 + first paragraph, LocalBusiness + FAQPage
schema, >=10 in-body internal links, E-E-A-T, alt+dims on images, "fully covered" (never insured).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
from engine import esc, icon, img, section, prose, card_grid, cta_band, faq_block, map_embed

B = E.S.BUSINESS
PH = {p[0]: p for p in E.PHOTOS}  # slug -> (slug, alt)

def _photo(slug):
    return PH.get(slug, E.PHOTOS[0])

# ---------------------------------------------------------------- shared bits
def page_hero(h1, lead_html, photo_slug, kicker=None, cta=True):
    return E.hero(h1, lead_html, _photo(photo_slug), kicker=kicker, cta=cta)

def services_cards(reveal=True):
    cards = [
        ("Home Removals", "/services/home-removals/", "<p>Careful, fully managed house moves of any size across Ipswich and Suffolk.</p>"),
        ("Office Removals", "/services/office-removals/", "<p>Planned, low-downtime business relocations, often out of hours.</p>"),
        ("Commercial Removals", "/services/commercial-removals/", "<p>Stock, equipment and furniture moved with our modern Euro&nbsp;6 fleet.</p>"),
        ("Long Distance Removals", "/services/long-distance-removals/", "<p>Door-to-door relocations out of Suffolk and across the UK.</p>"),
        ("Man &amp; Van", "/services/man-and-van/", "<p>Cost-effective help for smaller jobs and single items.</p>"),
        ("Piano Removals", "/services/piano-removals/", "<p>Upright and grand pianos moved safely by a trained team.</p>"),
        ("Packing Service", "/services/packing-service/", "<p>Professional packing and quality materials for a faster, safer move.</p>"),
        ("Storage", "/services/storage/", "<p>Clean, dry, secure containerised storage at our Westerfield base.</p>"),
    ]
    return card_grid(cards, cols=4, heading="What We Do",
                     intro="One local team for your whole move &mdash; removals, packing and storage across Suffolk.",
                     bg="bg-lightgrey", reveal=reveal, variant="service")

def areas_block():
    towns = E.S.load_locations()
    pills = "".join(
        f'<a href="/{p}" class="px-4 py-2 rounded-full border border-border bg-white hover:border-orange hover:text-orange font-semibold text-sm">{esc(n)}</a>'
        for p, n in towns)
    return section(
        '<div class="grid grid-cols-12"><div class="col-span-12 lg:col-span-10 lg:col-start-2 text-center">'
        '<h2 class="relative leading-tight text-black">Areas We Cover Across Suffolk</h2>'
        '<p class="text-lg xl:text-xl font-medium mt-2">From our base in '
        '<a href="/locations/ipswich-removals/">Westerfield, Ipswich</a> we move homes and businesses right across '
        '<a href="/locations/suffolk-removals/">Suffolk</a>:</p>'
        f'<div class="flex flex-wrap gap-2 justify-center mt-6">{pills}</div></div></div>',
        bg="bg-white", extra="logo-row overflow-hidden")

# ---------------------------------------------------------------- forms
def _input(name, placeholder, typ="text", required=False, half=True):
    req = ' required aria-required="true"' if required else ""
    col = "md:col-span-6" if half else "md:col-span-12"
    return (f'<div class="col-span-12 {col}"><input class="w-full" type="{typ}" name="{name}" '
            f'placeholder="{esc(placeholder)}" aria-label="{esc(placeholder.rstrip(chr(42)))}"{req}></div>')

def _select(name, label, options):
    opts = '<option value="" selected disabled>' + esc(label) + '</option>' + "".join(
        f'<option value="{esc(o)}">{esc(o)}</option>' for o in options)
    return (f'<div class="col-span-12 md:col-span-6"><select class="w-full" name="{name}" aria-label="{esc(label)}">{opts}</select></div>')

def quote_form():
    pills = "".join(
        f'<label class="eopt"><input type="checkbox" name="services" value="{esc(v)}"><span class="eopt-tick"></span><span>{esc(v)}</span></label>'
        for v in ["Home removal", "Office / commercial", "Packing", "Storage", "Man & van", "Piano"])
    arrow = ('<svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.4" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
    return (
        f'<form class="enquiry-form" method="post" action="{E.FORM_ENDPOINT}" novalidate>'
        '<div class="grid grid-cols-12 gap-4">'
        + _input("first_name", "First Name*", required=True)
        + _input("last_name", "Last Name*", required=True)
        + _input("email", "Email*", typ="email", required=True)
        + _input("phone", "Phone", typ="tel")
        + _input("move_from", "Moving from (town / postcode)")
        + _input("move_to", "Moving to (town / postcode)")
        + _select("property", "Property size", ["Studio / 1 bed", "2 bed", "3 bed", "4 bed", "5+ bed", "Office / commercial"])
        + _input("move_date", "Preferred date", typ="date")
        + '<div class="col-span-12"><span class="block font-semibold mb-2 text-black normal-case">What do you need? '
          '<span class="text-blue">(tick any)</span></span>'
          f'<div class="flex flex-wrap gap-3">{pills}</div></div>'
        + '<div class="col-span-12"><textarea class="w-full" name="message" rows="4" '
          'placeholder="Anything else we should know? (access, parking, special items)" aria-label="Message"></textarea></div>'
        + '<div class="col-span-12 hidden" aria-hidden="true"><label>Leave blank<input type="text" name="company" tabindex="-1" autocomplete="off"></label></div>'
        + '<div class="col-span-12"><button type="submit" class="button-orange w-full justify-center inline-flex items-center gap-2">Send My Enquiry ' + arrow + '</button>'
          '<p class="mt-3 text-xs text-darkgrey mb-0 normal-case">By submitting this form you agree to our '
          '<a href="/privacy-policy/">privacy policy</a>. We&rsquo;ll only use your details to respond to your enquiry.</p></div>'
        '</div></form>')

def contact_form():
    arrow = ('<svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.4" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
    return (
        f'<form class="enquiry-form" method="post" action="{E.FORM_ENDPOINT}" novalidate>'
        '<div class="grid grid-cols-12 gap-4">'
        + _input("first_name", "First Name*", required=True)
        + _input("last_name", "Last Name*", required=True)
        + _input("email", "Email*", typ="email", required=True)
        + _input("phone", "Phone", typ="tel")
        + '<div class="col-span-12"><textarea class="w-full" name="message" rows="5" '
          'placeholder="How can we help?" aria-label="Message" required aria-required="true"></textarea></div>'
        + '<div class="col-span-12 hidden" aria-hidden="true"><label>Leave blank<input type="text" name="company" tabindex="-1" autocomplete="off"></label></div>'
        + '<div class="col-span-12"><button type="submit" class="button-orange w-full justify-center inline-flex items-center gap-2">Send Message ' + arrow + '</button>'
          '<p class="mt-3 text-xs text-darkgrey mb-0 normal-case">By submitting this form you agree to our '
          '<a href="/privacy-policy/">privacy policy</a>.</p></div>'
        '</div></form>')

# ================================================================ ABOUT US
def about_us():
    body = "\n".join([
        page_hero(
            "About Orwell Removals &amp; Storage",
            "A family-run removals company in Ipswich, moving Suffolk homes and businesses with care since 2005.",
            "orwell-lorry-van-outside-home", kicker="Family-run since 2005"),
        section(prose(
            '<h2 class="relative leading-tight text-black">A Family-Run Removals Company in Ipswich</h2>'
            '<p>Orwell Removals &amp; Storage is a <strong>family-run removals company in Ipswich</strong>, based at Old '
            'Station Works on Main Road in <a href="/locations/ipswich-removals/">Westerfield</a>, just north of the town. '
            'We have been moving people and businesses across <a href="/locations/suffolk-removals/">Suffolk</a> since '
            '2005 &mdash; long enough to know that no two moves are the same, and that the difference between a stressful '
            'day and a smooth one usually comes down to preparation, communication and genuine care.</p>'
            '<p>We are not a national chain or a faceless call centre. When you ring us you speak to the same people who '
            'will plan your move, and very often the same faces who turn up on the day. That continuity matters: it means '
            'nothing gets lost in handovers, and you always know who you are dealing with from your first enquiry to the '
            'last box carried in. First impressions count, and we work hard to make a good one every time.</p>'
        ), bg="bg-white", extra="logo-row overflow-hidden"),
        E.media_rows(
            '<h2>Nearly Two Decades on the Road in Suffolk</h2>'
            '<p>What started as a small local operation has grown, year by year, into a trusted name for removals and '
            'storage right across the county. We have carried families into their first homes, helped people downsize after '
            'a lifetime in one house, and kept businesses running through office and shop relocations. Along the way we have '
            'invested in the things that make moves safer and smoother &mdash; a modern, low-emission <strong>Euro&nbsp;6 '
            'fleet</strong>, proper transit blankets and protective wrap, and a clean, dry storage facility at our '
            'Westerfield base.</p>'
            '<h3>The way we like to work</h3>'
            '<p>Every move begins with a proper conversation and, for larger jobs, a free survey so we can give you an '
            'honest, accurate quote with no surprises on the day. We turn up on time, protect your floors and doorways, '
            'wrap your furniture properly, and place everything where you want it at the other end. If something needs '
            'dismantling and rebuilding, we will sort it. If completion dates slip, our <a href="/services/storage/">storage</a> '
            'bridges the gap. It is removals done the way we would want our own families looked after.</p>',
            seed="about-story", bg="bg-beige", topic="removals storage van lorry Suffolk"),
        services_cards(reveal=True),
        section(prose(
            '<h2 class="relative leading-tight text-black">Why People Choose Orwell</h2>'
            '<p>Plenty of firms can put a van outside your house. What sets us apart is the care and the cover behind it. '
            'Every move is <strong>fully covered</strong> &mdash; goods-in-transit and public liability protection is '
            'arranged through <strong>Basil Fry</strong>, the specialist insurer for the removals trade &mdash; so your '
            'belongings are protected from the moment we load them. Our crews are trained and uniformed, our vehicles are '
            'clean and modern, and we are proud to have worked alongside organisations such as <strong>Ipswich Borough '
            'Council</strong> over the years.</p>'
            '<p>We cover the whole of Suffolk, including '
            '<a href="/locations/felixstowe-removals/">Felixstowe</a>, '
            '<a href="/locations/woodbridge-removals/">Woodbridge</a>, '
            '<a href="/locations/bury-st-edmunds-removals/">Bury St Edmunds</a>, '
            '<a href="/locations/stowmarket-removals/">Stowmarket</a> and '
            '<a href="/locations/lowestoft-removals/">Lowestoft</a> &mdash; and we travel '
            '<a href="/services/long-distance-removals/">across the UK</a> when your move takes you further afield. '
            'Whether it is a single item with our <a href="/services/man-and-van/">man &amp; van</a> service or a full '
            '<a href="/services/home-removals/">home removal</a> with <a href="/services/packing-service/">packing</a>, '
            'you get the same attention to detail.</p>'
        ), bg="bg-white", extra="logo-row overflow-hidden"),
        E.trusted_by(),
        areas_block(),
        E.standard_feature_panel(E.page_photos("about-feature", 1)[0], reverse=True, bg="bg-beige"),
    ])
    faqs = [
        ("How long has Orwell Removals &amp; Storage been trading?",
         "<p>We have been moving Suffolk homes and businesses since 2005 &mdash; nearly two decades of local experience, "
         "based at Old Station Works in Westerfield, Ipswich.</p>"),
        ("Are you a local, family-run company?",
         '<p>Yes. We are a genuinely local, family-run firm. You deal with the same people throughout, from your first '
         'call to moving day &mdash; not a national call centre. See our <a href="/locations/">areas we cover</a>.</p>'),
        ("Are my belongings covered during the move?",
         "<p>Absolutely. Every move is fully covered, with goods-in-transit and public liability protection arranged "
         "through Basil Fry, the removals-trade specialist. We&rsquo;ll happily talk you through the cover at quote stage.</p>"),
        ("Do you only do house moves?",
         '<p>Not at all. As well as <a href="/services/home-removals/">home removals</a> we handle '
         '<a href="/services/office-removals/">office</a> and <a href="/services/commercial-removals/">commercial</a> '
         'moves, <a href="/services/piano-removals/">pianos</a>, <a href="/services/packing-service/">packing</a> and '
         '<a href="/services/storage/">storage</a>.</p>'),
        ("Which areas do you cover?",
         '<p>The whole of Suffolk and beyond. Popular areas include <a href="/locations/ipswich-removals/">Ipswich</a>, '
         '<a href="/locations/felixstowe-removals/">Felixstowe</a> and '
         '<a href="/locations/bury-st-edmunds-removals/">Bury St Edmunds</a> &mdash; and we cover '
         '<a href="/services/long-distance-removals/">long-distance UK moves</a> too.</p>'),
    ]
    faq_html, faq_schema = faq_block(faqs, heading="About Orwell — Common Questions", bg="bg-lightgrey")
    body += "\n" + faq_html
    body += "\n" + cta_band("Ready to Plan Your Move?",
                            "Tell us what you&rsquo;re moving and we&rsquo;ll give you a clear, no-obligation quote. Call us on 01473 411531 or request a quote online.",
                            "Get a Free Quote", "/get-a-quote/", bg="bg-white")
    doc = E.render_page(
        title="About Us | Orwell Removals & Storage, Ipswich",
        description="Orwell Removals & Storage is a family-run Ipswich removals company moving Suffolk homes and businesses since 2005. Euro 6 fleet, secure storage, fully covered.",
        canonical_path="/about-us/", body=body,
        og_image="images/photos/orwell-lorry-van-outside-home.webp",
        breadcrumb=[("Home", "/"), ("About Us", "/about-us/")],
        extra_schema=[faq_schema], active="about")
    return E.write("about-us/index.html", doc)

# ================================================================ PRICING
def pricing():
    body = "\n".join([
        page_hero(
            "Removals Pricing in Ipswich &amp; Suffolk",
            "Clear, honest removals pricing with no hidden extras &mdash; here&rsquo;s exactly how we work it out.",
            "orwell-box-lorry-residential-street", kicker="Transparent quotes"),
        section(prose(
            '<h2 class="relative leading-tight text-black">How Our Removals Pricing Works</h2>'
            '<p>Honest <strong>removals pricing in Ipswich and Suffolk</strong> starts with understanding your move. '
            'Rather than a one-size-fits-all figure, we build every quote around what you actually need &mdash; the size '
            'of your home, how far you&rsquo;re going, how easy the access is and whether you&rsquo;d like us to handle '
            'the <a href="/services/packing-service/">packing</a> or <a href="/services/storage/">storage</a> too. The '
            'result is a clear, fixed quote with no hidden extras bolted on at the end.</p>'
            '<p>For most moves we offer a free survey &mdash; in person or by a quick video walk-round &mdash; so we can '
            'see what&rsquo;s involved and price it accurately. It only takes a few minutes and it&rsquo;s the surest way '
            'to avoid surprises on moving day. Prefer to keep it simple? Call us on '
            f'<a href="{B["phone_link"]}">{B["phone"]}</a> for a friendly chat and a ballpark figure.</p>'
        ), bg="bg-white", extra="logo-row overflow-hidden"),
        E.media_rows(
            '<h2>What Affects the Cost of Your Move</h2>'
            '<p>A handful of practical things shape the price of any removal. Knowing them up front helps you understand '
            'your quote &mdash; and often helps you keep the cost down.</p>'
            '<h3>The volume and type of your belongings</h3>'
            '<p>More furniture and boxes means more time, more vehicle space and sometimes a larger crew. Bulky or '
            'delicate items &mdash; wardrobes, American fridges, <a href="/services/piano-removals/">pianos</a> &mdash; '
            'need extra hands and equipment, so they affect the figure.</p>'
            '<h3>Distance and access</h3>'
            '<p>A local move within Ipswich is very different from a '
            '<a href="/services/long-distance-removals/">long-distance relocation</a> across the UK. Access matters too: '
            'narrow lanes, flats with stairs, long carries from the door to the van and tricky parking all add time.</p>'
            '<h3>Packing, dismantling and storage</h3>'
            '<p>You can pack yourself to save money, or let our team take care of it with a full '
            '<a href="/services/packing-service/">packing service</a> and quality materials. If completion dates don&rsquo;t '
            'line up, our <a href="/services/storage/">secure storage</a> bridges the gap. Each of these is optional and '
            'priced separately, so you only pay for what you choose.</p>'
            '<h3>Timing</h3>'
            '<p>Fridays, month-ends and bank holidays are the busiest times for movers everywhere. If your dates are '
            'flexible, a mid-week or mid-month move can sometimes be more cost-effective.</p>',
            seed="pricing-factors", bg="bg-beige", topic="removals van lorry boxes"),
        section(prose(
            '<h2 class="relative leading-tight text-black">What&rsquo;s Included as Standard</h2>'
            '<p>Every Orwell quote includes the things that should never be &ldquo;extras&rdquo;: a trained, uniformed '
            'crew, a clean modern <strong>Euro&nbsp;6</strong> vehicle, transit blankets and protective wrap for your '
            'furniture, floor and doorway protection, and careful loading and placing at the other end. Every move is '
            '<strong>fully covered</strong> &mdash; goods-in-transit and public liability protection through Basil Fry, '
            'the removals-trade specialist &mdash; for genuine peace of mind.</p>'
            '<h3>Deposits and payment</h3>'
            '<p>To confirm your date we ask for a small booking deposit, with the balance due on or before completion of '
            'the move. We accept payment by debit/credit card and bank transfer. We&rsquo;ll set everything out clearly in '
            'your written quote, and our <a href="/terms-conditions/">terms and conditions</a> explain the details.</p>'
            '<h3>Why we don&rsquo;t publish a fixed price list</h3>'
            '<p>Because an honest price depends on your specific move, a generic &ldquo;two-bedroom move = &pound;X&rdquo; '
            'figure would either over-charge some customers or under-quote others and lead to extras on the day. We&rsquo;d '
            'rather give you an accurate, no-obligation quote built around your home. '
            '<a href="/get-a-quote/">Request yours here</a> &mdash; it&rsquo;s free and there&rsquo;s no pressure.</p>'
        ), bg="bg-white", extra="logo-row overflow-hidden"),
        services_cards(reveal=True),
        E.trusted_by("bg-lightgrey"),
        areas_block(),
    ])
    faqs = [
        ("How much does a removal in Ipswich cost?",
         '<p>It depends on the size of your home, the distance, access and any packing or storage you need. The most '
         'accurate way to find out is a free, no-obligation quote &mdash; <a href="/get-a-quote/">request one here</a> '
         'or call us on ' + f'<a href="{B["phone_link"]}">{B["phone"]}</a>.</p>'),
        ("Do you charge for a quote or survey?",
         "<p>No. Quotes and surveys are completely free and carry no obligation, whether we visit in person or do a quick "
         "video walk-round.</p>"),
        ("Is there a deposit, and how do I pay?",
         '<p>We ask for a small booking deposit to hold your date, with the balance due on or before completion. We accept '
         'card and bank transfer. Full details are in your written quote and our <a href="/terms-conditions/">terms</a>.</p>'),
        ("Are there any hidden extras?",
         "<p>No. Your written quote sets out exactly what&rsquo;s included. The only things that change the price are "
         "things you ask for &mdash; like added packing or storage &mdash; and we&rsquo;ll always confirm those with you first.</p>"),
        ("Can I save money by packing myself?",
         '<p>Yes. Many customers pack their own boxes and leave the furniture and fragile items to us. We can supply '
         'materials, or take care of everything with our <a href="/services/packing-service/">full packing service</a>.</p>'),
    ]
    faq_html, faq_schema = faq_block(faqs, heading="Pricing — Common Questions", bg="bg-beige")
    body += "\n" + faq_html
    body += "\n" + cta_band("Get a Clear, No-Obligation Quote",
                            "Tell us about your move and we&rsquo;ll give you an honest, fixed price &mdash; no hidden extras.",
                            "Get a Free Quote", "/get-a-quote/", bg="bg-white")
    doc = E.render_page(
        title="Removals Pricing in Ipswich & Suffolk | Orwell",
        description="How Orwell Removals & Storage prices a move in Ipswich & Suffolk: clear, fixed quotes, no hidden extras and free surveys. See what affects the cost.",
        canonical_path="/pricing/", body=body,
        og_image="images/photos/orwell-box-lorry-residential-street.webp",
        breadcrumb=[("Home", "/"), ("Pricing", "/pricing/")],
        extra_schema=[faq_schema], active="pricing")
    return E.write("pricing/index.html", doc)

# ================================================================ FAQ
def faq_page():
    faqs = [
        ("How do I get a removals quote?",
         '<p>Call us on ' + f'<a href="{B["phone_link"]}">{B["phone"]}</a>, email '
         f'<a href="mailto:{B["email"]}">{B["email"]}</a>, or '
         '<a href="/get-a-quote/">fill in our quick quote form</a>. For larger moves we&rsquo;ll arrange a free survey '
         'in person or by video so we can give you an accurate, fixed price.</p>'),
        ("How far in advance should I book?",
         "<p>The sooner the better, especially for Fridays, weekends and month-ends. Two to four weeks&rsquo; notice is "
         "ideal, but we&rsquo;ll always do our best to help with shorter notice &mdash; just ask.</p>"),
        ("Which areas do you cover?",
         '<p>We&rsquo;re based in Westerfield, Ipswich and cover the whole of '
         '<a href="/locations/suffolk-removals/">Suffolk</a> &mdash; including '
         '<a href="/locations/felixstowe-removals/">Felixstowe</a>, '
         '<a href="/locations/woodbridge-removals/">Woodbridge</a> and '
         '<a href="/locations/bury-st-edmunds-removals/">Bury St Edmunds</a> &mdash; plus '
         '<a href="/services/long-distance-removals/">long-distance moves</a> across the UK.</p>'),
        ("Are my belongings covered during the move?",
         "<p>Yes. Every move is fully covered, with goods-in-transit and public liability protection arranged through "
         "Basil Fry, the removals-trade specialist. We&rsquo;ll explain the cover at quote stage.</p>"),
        ("Do you provide packing and materials?",
         '<p>We do. Choose our full <a href="/services/packing-service/">packing service</a> and let our team wrap and '
         'box everything, or buy materials from us and pack at your own pace. Fragile and valuable items are always '
         'wrapped with extra care.</p>'),
        ("Can you move pianos and other heavy items?",
         '<p>Yes &mdash; we offer specialist <a href="/services/piano-removals/">piano removals</a> for uprights and '
         'grands, and we&rsquo;re equipped for other heavy or awkward items like safes, large appliances and gym '
         'equipment. Let us know at quote stage.</p>'),
        ("Do you offer storage?",
         '<p>We do. Our <a href="/services/storage/">clean, dry, secure storage</a> at our Westerfield base is ideal for '
         'between moves, downsizing or renovations &mdash; for both <a href="/services/storage/household-storage/">'
         'household</a> and <a href="/services/storage/business-storage/">business</a> needs.</p>'),
        ("What if my completion date moves?",
         "<p>It happens often, and we&rsquo;re used to it. Our storage can bridge any gap between moving out and moving "
         "in, so a slipped completion date doesn&rsquo;t leave you stuck.</p>"),
        ("Will you dismantle and reassemble furniture?",
         "<p>Yes. Our crew can take down beds, wardrobes and flat-pack furniture and rebuild them at your new home. Just "
         "flag any items at quote stage so we allow time and bring the right tools.</p>"),
        ("Do you move offices and businesses?",
         '<p>We do &mdash; <a href="/services/office-removals/">office</a> and '
         '<a href="/services/commercial-removals/">commercial relocations</a>, often planned out of hours to keep your '
         'downtime to a minimum.</p>'),
        ("What about parking and access on moving day?",
         "<p>Good access saves time and money. If parking is tight, a permit or suspended bay may help &mdash; we&rsquo;ll "
         "talk this through when we quote, and we&rsquo;re experienced with narrow lanes, flats and long carries.</p>"),
        ("How should I prepare for moving day?",
         '<p>Label boxes by room, keep essentials and valuables with you, defrost the freezer, and make sure walkways are '
         'clear. If you&rsquo;d rather not lift a finger, our <a href="/services/packing-service/">packing service</a> '
         'takes care of it all.</p>'),
        ("How do I pay, and is there a deposit?",
         '<p>A small booking deposit secures your date, with the balance due on or before completion. We accept card and '
         'bank transfer. See our <a href="/pricing/">pricing page</a> for how it all works.</p>'),
        ("Can you help with a single item or a small job?",
         '<p>Of course. Our cost-effective <a href="/services/man-and-van/">man &amp; van</a> service is perfect for '
         'single items, small flats and quick jobs around Ipswich and Suffolk.</p>'),
        ("What if I need to cancel or change my booking?",
         '<p>Just let us know as early as you can and we&rsquo;ll do our best to accommodate changes. Our '
         '<a href="/terms-conditions/">terms and conditions</a> set out how deposits and cancellations work.</p>'),
    ]
    body = page_hero(
        "Frequently Asked Questions",
        "Everything you need to know about moving with Orwell Removals &amp; Storage &mdash; quotes, cover, packing, storage and more.",
        "orwell-luton-van-ipswich-road", kicker="Helpful answers")
    body += "\n" + section(prose(
        '<h2 class="relative leading-tight text-black">Your Removals &amp; Storage Questions, Answered</h2>'
        '<p>Below are the questions we&rsquo;re asked most often about <strong>removals and storage in Ipswich and '
        'Suffolk</strong>. If your question isn&rsquo;t here, <a href="/contact-us/">get in touch</a> &mdash; we&rsquo;re '
        'always happy to help, and there&rsquo;s no such thing as a silly question when it comes to your move.</p>'),
        bg="bg-white")
    faq_html, faq_schema = faq_block(faqs, heading="Removals &amp; Storage FAQs", bg="bg-lightgrey")
    body += "\n" + faq_html
    body += "\n" + cta_band("Still Have a Question?",
                            "We&rsquo;re a friendly local team and happy to talk through your move. Call 01473 411531 or drop us a message.",
                            "Contact Us", "/contact-us/", bg="bg-white")
    doc = E.render_page(
        title="Removals & Storage FAQs | Orwell Removals, Ipswich",
        description="Answers to common questions about removals and storage in Ipswich & Suffolk — quotes, cover, packing, pianos, storage, deposits and moving day.",
        canonical_path="/frequently-asked-questions/", body=body,
        og_image="images/photos/orwell-luton-van-ipswich-road.webp",
        breadcrumb=[("Home", "/"), ("FAQs", "/frequently-asked-questions/")],
        extra_schema=[faq_schema], active="faq")
    return E.write("frequently-asked-questions/index.html", doc)

# ================================================================ CONTACT
def contact_us():
    rows = "".join([
        f'<li><a class="qcontact" href="{B["phone_link"]}"><span class="qcontact-ico">{icon("phone","w-5 h-5")}</span>'
        f'<span class="qcontact-t"><span class="qcontact-k">Call us</span><span class="qcontact-v">{B["phone"]}</span></span></a></li>',
        f'<li><a class="qcontact" href="mailto:{B["email"]}"><span class="qcontact-ico">{icon("mail","w-5 h-5")}</span>'
        f'<span class="qcontact-t"><span class="qcontact-k">Sales &amp; quotes</span><span class="qcontact-v">{B["email"]}</span></span></a></li>',
        f'<li><a class="qcontact" href="mailto:{B["email_info"]}"><span class="qcontact-ico">{icon("mail","w-5 h-5")}</span>'
        f'<span class="qcontact-t"><span class="qcontact-k">General enquiries</span><span class="qcontact-v">{B["email_info"]}</span></span></a></li>',
    ])
    details = (
        '<div class="text-black">'
        '<h2 class="relative leading-tight text-black">Get in Touch</h2>'
        '<p class="text-lg">We&rsquo;re a friendly, local team and we&rsquo;re always happy to help with your move. '
        'Call, email or send the form and we&rsquo;ll come straight back to you &mdash; usually the same working day.</p>'
        f'<ul class="qcontacts list-none p-0 m-0">{rows}</ul>'
        '<div class="mt-6"><p class="font-semibold mb-1 text-black uppercase text-sm tracking-wide">Visit us</p>'
        f'<address class="not-italic leading-relaxed text-darkgrey">{esc(B["street"])}<br>{esc(B["locality"])}, {esc(B["region"])} {esc(B["postcode"])}</address>'
        '<p class="mt-3 mb-0 font-semibold text-black uppercase text-sm tracking-wide">Opening hours</p>'
        '<p class="text-darkgrey mb-0">Monday&ndash;Friday 8am&ndash;6pm &middot; Saturday 9am&ndash;1pm</p></div>'
        '</div>')
    form_card = ('<div class="enquiry-card bg-white rounded-2xl shadow-2xl p-6 lg:p-9 text-black border border-border">'
                 '<h2 class="text-xl xl:text-2xl font-bold text-black leading-tight mb-1">Send Us a Message</h2>'
                 '<p class="text-darkgrey text-sm normal-case mb-5">We&rsquo;ll reply by phone or email, whichever you prefer.</p>'
                 + contact_form() + '</div>')
    body = "\n".join([
        page_hero("Contact Orwell Removals &amp; Storage",
                  "Call, email or message our Ipswich team &mdash; we&rsquo;re here to help with your move and storage.",
                  "orwell-removals-storage-signage", kicker="We&rsquo;re here to help", cta=False),
        section('<div class="grid grid-cols-12 gap-8 lg:gap-12 items-start">'
                f'<div class="col-span-12 lg:col-span-5">{details}</div>'
                f'<div class="col-span-12 lg:col-span-7">{form_card}</div>'
                '</div>', bg="bg-white"),
        section('<h2 class="relative leading-tight text-black text-center mb-6">Find Us in Westerfield, Ipswich</h2>'
                + map_embed("Old Station Works, Main Road, Westerfield, Ipswich IP6 9AB",
                            "Orwell Removals & Storage, Westerfield, Ipswich", zoom=13),
                bg="bg-lightgrey"),
    ])
    doc = E.render_page(
        title="Contact Us | Orwell Removals & Storage, Ipswich",
        description="Contact Orwell Removals & Storage in Ipswich. Call 01473 411531, email us or send a message for a free removals and storage quote across Suffolk.",
        canonical_path="/contact-us/", body=body,
        og_image="images/photos/orwell-removals-storage-signage.webp",
        breadcrumb=[("Home", "/"), ("Contact Us", "/contact-us/")],
        active="contact", show_quote=False)
    return E.write("contact-us/index.html", doc)

# ================================================================ GET A QUOTE
def get_a_quote():
    bullets = ["Free, no-obligation quote", "Friendly, family-run local team", "Fully covered &mdash; Basil Fry protection",
               "Same working-day response", "In-person or video survey"]
    lis = "".join(f'<li class="flex items-start gap-2"><span class="text-green mt-1">{icon("check-bold","w-5 h-5")}</span><span>{esc(t)}</span></li>' for t in bullets)
    info = ('<div class="text-black">'
            '<h2 class="relative leading-tight text-black">Tell Us About Your Move</h2>'
            '<p class="text-lg">Fill in as much as you can and we&rsquo;ll come back with a clear, fixed quote &mdash; no '
            'pressure and no hidden extras. Prefer to talk? Call us on '
            f'<a href="{B["phone_link"]}">{B["phone"]}</a> or email '
            f'<a href="mailto:{B["email"]}">{B["email"]}</a>.</p>'
            f'<ul class="space-y-2 text-base xl:text-lg list-none p-0 mt-5">{lis}</ul>'
            '<p class="mt-6 text-darkgrey">Not sure what you need yet? Read about our '
            '<a href="/services/home-removals/">home removals</a>, '
            '<a href="/services/packing-service/">packing</a> and '
            '<a href="/services/storage/">storage</a>, or see how our '
            '<a href="/pricing/">pricing</a> works.</p></div>')
    form_card = ('<div class="enquiry-card bg-white rounded-2xl shadow-2xl p-6 lg:p-9 text-black border border-border">'
                 '<h2 class="text-xl xl:text-2xl font-bold text-black leading-tight mb-1">Request Your Free Quote</h2>'
                 '<p class="text-darkgrey text-sm normal-case mb-5">Fast response &mdash; usually the same working day.</p>'
                 + quote_form() + '</div>')
    body = "\n".join([
        page_hero("Get a Free Removals Quote",
                  "A clear, no-obligation quote for your move across Ipswich and Suffolk &mdash; in just a few minutes.",
                  "orwell-van-on-customer-driveway", kicker="Free &amp; no-obligation", cta=False),
        section('<div class="grid grid-cols-12 gap-8 lg:gap-12 items-start">'
                f'<div class="col-span-12 lg:col-span-5">{info}</div>'
                f'<div class="col-span-12 lg:col-span-7">{form_card}</div>'
                '</div>', bg="bg-white"),
    ])
    doc = E.render_page(
        title="Get a Free Removals Quote | Orwell, Ipswich",
        description="Get a free, no-obligation removals and storage quote from Orwell Removals & Storage in Ipswich. Clear fixed prices across Suffolk. Fast same-day response.",
        canonical_path="/get-a-quote/", body=body,
        og_image="images/photos/orwell-van-on-customer-driveway.webp",
        breadcrumb=[("Home", "/"), ("Get a Quote", "/get-a-quote/")],
        active="quote", show_quote=False)
    return E.write("get-a-quote/index.html", doc)

# ================================================================ GALLERY
def gallery():
    hero_slug = "orwell-box-lorry-ipswich-street"
    _all = [p for p in E.PHOTOS if p[0] != hero_slug]  # exclude the hero so it isn't shown twice
    # The library now holds 260+ photos — show a curated, evenly-spread 48 so the page stays
    # light while still spanning vans, lorries, loading, packing, storage and houses.
    N = 48
    pics = ([_all[int(i * len(_all) / N)] for i in range(N)] if len(_all) > N else _all)
    body = "\n".join([
        page_hero("Our Work in Pictures",
                  "Real Orwell Removals &amp; Storage moves &mdash; our team, vans and storage across Ipswich and Suffolk.",
                  hero_slug, kicker="Gallery"),
        section(prose(
            '<p class="text-lg text-center">A look at recent removals and storage work across '
            '<a href="/locations/suffolk-removals/">Suffolk</a>. Like what you see? '
            '<a href="/get-a-quote/">Get a free quote</a> or explore our '
            '<a href="/services/">services</a>.</p>', center=True), bg="bg-white"),
        E.photo_gallery(pics, heading="Recent Moves &amp; Our Fleet",
                        intro="Home and business moves, packing and secure storage &mdash; handled with care.", bg="bg-lightgrey"),
        section('<div class="text-center max-w-2xl mx-auto">'
                '<h2 class="relative leading-tight text-black">Like What You See?</h2>'
                '<p class="text-lg">Let our friendly Ipswich team take care of your move from start to finish &mdash; '
                '<a href="/services/home-removals/">home</a>, <a href="/services/office-removals/">office</a> or '
                '<a href="/services/commercial-removals/">commercial</a>.</p>'
                '<a class="button-orange mt-4 inline-flex" href="/get-a-quote/">Get a Free Quote</a></div>', bg="bg-white"),
    ])
    doc = E.render_page(
        title="Gallery | Orwell Removals & Storage, Ipswich",
        description="See Orwell Removals & Storage in action across Ipswich and Suffolk — our team, vans, packing and secure storage. Family-run removals since 2005.",
        canonical_path="/gallery/", body=body,
        og_image="images/photos/orwell-box-lorry-ipswich-street.webp",
        breadcrumb=[("Home", "/"), ("Gallery", "/gallery/")],
        active="gallery", show_quote=False)
    return E.write("gallery/index.html", doc)

# ================================================================ REVIEWS
def reviews():
    g_search = "https://www.google.com/search?q=Orwell+Removals+and+Storage+Ipswich+reviews"
    values = [
        ("Care with your belongings", "Proper wrapping, transit blankets and a crew who treat your things like their own."),
        ("Clear communication", "The same friendly people from your first call to the last box &mdash; no call centres."),
        ("On time, no fuss", "We turn up when we say we will and get on with the job, carefully."),
        ("Honest, fixed quotes", "A clear price with no hidden extras &mdash; you know where you stand."),
    ]
    cards = "".join(
        f'<div class="bg-white rounded-xl border border-border shadow-custom p-6">'
        f'<h3 class="text-lg font-semibold text-black">{esc(t)}</h3>'
        f'<p class="mt-2 text-darkgrey mb-0">{d}</p></div>' for t, d in values)
    body = "\n".join([
        page_hero("Customer Reviews",
                  "What people across Ipswich and Suffolk value about moving with Orwell Removals &amp; Storage.",
                  "orwell-van-outside-modern-home", kicker="What our customers value"),
        section(prose(
            '<h2 class="relative leading-tight text-black">Reviews You Can Trust</h2>'
            '<p>We&rsquo;d always rather you heard it from real customers than from us. The best place to read genuine, '
            'unedited feedback &mdash; and to leave your own after a move &mdash; is on Google, where reviews are tied to '
            'real accounts. We don&rsquo;t publish hand-picked quotes here; we&rsquo;d simply encourage you to look us up '
            'and see what people say. When you&rsquo;re ready, <a href="/get-a-quote/">get a free quote</a> or '
            '<a href="/contact-us/">contact our team</a>.</p>'), bg="bg-white"),
        section('<h2 class="relative leading-tight text-black text-center mb-8">What Customers Tell Us Matters Most</h2>'
                f'<div class="grid grid-cols-1 sm:grid-cols-2 gap-5">{cards}</div>', bg="bg-lightgrey"),
        section(
            '<div class="text-center max-w-2xl mx-auto">'
            '<h2 class="relative leading-tight text-black">Leave Us a Review</h2>'
            '<p class="text-lg">Recently moved with us? It only takes a minute and it really helps other local people '
            'choose with confidence. Thank you.</p>'
            f'<a href="{g_search}" target="_blank" rel="noopener" class="button-orange mt-4 inline-flex">Find us on Google</a></div>',
            bg="bg-white"),
    ])
    doc = E.render_page(
        title="Customer Reviews | Orwell Removals & Storage",
        description="Read genuine customer reviews of Orwell Removals & Storage on Google, and see what Ipswich and Suffolk movers value most about our family-run service.",
        canonical_path="/reviews/", body=body,
        og_image="images/photos/orwell-van-outside-modern-home.webp",
        breadcrumb=[("Home", "/"), ("Reviews", "/reviews/")],
        active="reviews", show_quote=False)
    return E.write("reviews/index.html", doc)

# ================================================================ LEGAL
def _legal(slug, title, desc, h1, intro, sections):
    secs = "".join(f'<h2 class="relative leading-tight text-black mt-8">{esc(t)}</h2>{b}' for t, b in sections)
    body = section(prose(f'<h1 class="text-3xl 2xl:text-4xl">{esc(h1)}</h1>'
                         f'<p class="text-darkgrey">{intro}</p>{secs}'), bg="bg-white")
    doc = E.render_page(title=title, description=desc, canonical_path=f"/{slug}/", body=body,
                        breadcrumb=[("Home", "/"), (h1, f"/{slug}/")], active="", show_quote=False)
    return E.write(f"{slug}/index.html", doc)

def privacy_policy():
    s = [
        ("Who we are", f'<p>Orwell Removals &amp; Storage (&ldquo;we&rdquo;, &ldquo;us&rdquo;) is a removals and storage '
         f'company based at {esc(B["street"])}, {esc(B["locality"])}, {esc(B["region"])} {esc(B["postcode"])}. We are the '
         f'data controller for the personal information you give us. Contact us at '
         f'<a href="mailto:{B["email_info"]}">{B["email_info"]}</a> or {B["phone"]}.</p>'),
        ("What we collect", "<p>When you request a quote or contact us we collect the details you provide &mdash; typically "
         "your name, contact details, the addresses involved in your move and any notes about what you need moved. If you "
         "go on to book, we keep the information needed to carry out and account for your move.</p>"),
        ("How and why we use it (lawful basis)", "<p>We use your information to respond to your enquiry, prepare a quote, "
         "carry out your move and meet our legal and accounting obligations. Our lawful bases are your consent (when you "
         "contact us), the performance of a contract (when you book), and our legitimate interests in running the business. "
         "We do not sell your data or use it for unrelated marketing without your consent.</p>"),
        ("How long we keep it", "<p>We keep enquiry information only as long as needed to deal with your enquiry, and "
         "booking and financial records for as long as the law requires (for example for tax purposes). When information "
         "is no longer needed it is securely deleted or destroyed.</p>"),
        ("Sharing your information", "<p>We only share your information where necessary &mdash; for example with our "
         "insurer or payment providers &mdash; and we never sell it. Any third parties who process data on our behalf are "
         "required to keep it secure and use it only for the agreed purpose.</p>"),
        ("Your rights", "<p>Under UK GDPR and the Data Protection Act 2018 you have the right to access your data, to have "
         "it corrected or erased, to restrict or object to processing, and to data portability. To exercise any of these, "
         f'email <a href="mailto:{B["email_info"]}">{B["email_info"]}</a>. You also have the right to complain to the '
         "Information Commissioner&rsquo;s Office (ICO) at ico.org.uk.</p>"),
        ("Cookies", "<p>Our website uses only the minimal cookies needed to function and, where enabled, privacy-respecting "
         "analytics to understand how the site is used. You can control cookies through your browser settings.</p>"),
    ]
    return _legal("privacy-policy", "Privacy Policy | Orwell Removals & Storage",
                  "How Orwell Removals & Storage collects, uses and protects your personal data under UK GDPR and the Data Protection Act 2018.",
                  "Privacy Policy",
                  "Your privacy matters to us. This policy explains what personal information we collect, how we use it and the rights you have under UK data-protection law.",
                  s)

def terms_conditions():
    s = [
        ("Quotations", "<p>Quotes are based on the information you give us and, where applicable, our survey. If the work "
         "or volume differs materially on the day &mdash; for example significantly more items or much harder access than "
         "described &mdash; the price may be adjusted, and we will always discuss this with you first.</p>"),
        ("Booking and deposits", "<p>A booking deposit confirms your date. The balance is due on or before completion of "
         "the move unless otherwise agreed in writing. We accept payment by debit/credit card and bank transfer.</p>"),
        ("Cover and liability", "<p>Every move is fully covered, with goods-in-transit and public liability protection "
         "arranged through Basil Fry, the removals-trade specialist. Cover levels and any conditions are explained at quote "
         "stage; please ask if you would like specific items noted.</p>"),
        ("Your responsibilities", "<p>Please ensure items are ready as agreed, that we have suitable access and parking, "
         "and that you tell us about anything fragile, valuable or unusually heavy in advance. We are not able to transport "
         "hazardous goods, and we recommend you keep cash, jewellery and important documents with you.</p>"),
        ("Cancellations and changes", "<p>If you need to cancel or change your booking, please tell us as early as "
         "possible and we will do our best to help. Deposits and any cancellation terms are set out in your written quote.</p>"),
        ("Claims", "<p>In the unlikely event of loss or damage, please tell us as soon as possible so we can put things "
         "right. Notify us in writing within a reasonable period and we will guide you through the process.</p>"),
    ]
    return _legal("terms-conditions", "Terms & Conditions | Orwell Removals & Storage",
                  "The terms and conditions for removals and storage services provided by Orwell Removals & Storage in Ipswich and across Suffolk.",
                  "Terms & Conditions",
                  "These terms set out how we work together on your move. If anything is unclear, just ask &mdash; we are always happy to explain.",
                  s)

# ================================================================ 404
def not_found():
    inner = (
        '<div class="text-center max-w-2xl mx-auto py-10 lg:py-16">'
        '<p class="fp-kicker">Error 404</p>'
        '<h1 class="text-4xl lg:text-5xl font-bold text-black leading-tight">We couldn&rsquo;t find that page</h1>'
        '<p class="mt-4 text-lg xl:text-xl text-darkgrey">The page you were looking for may have moved. Let&rsquo;s get '
        'you back on track &mdash; here are some helpful places to go:</p>'
        '<div class="flex flex-wrap gap-3 justify-center mt-6">'
        '<a href="/" class="button-orange">Home</a>'
        '<a href="/services/" class="button">Our Services</a>'
        '<a href="/locations/" class="button">Areas We Cover</a>'
        '<a href="/get-a-quote/" class="button">Get a Quote</a>'
        '<a href="/contact-us/" class="button">Contact Us</a>'
        '</div>'
        f'<p class="mt-8 text-darkgrey">Or call us on <a href="{B["phone_link"]}">{B["phone"]}</a> &mdash; '
        'we&rsquo;re happy to help.</p></div>')
    doc = E.render_page(
        title="Page Not Found | Orwell Removals & Storage",
        description="Sorry, we couldn't find that page. Find Orwell Removals & Storage services, areas covered and contact details, or get a free removals quote.",
        canonical_path="/404.html", body=section(inner, bg="bg-white"),
        robots="noindex, follow", active="", show_quote=False, show_fabs=False)
    return E.write("404.html", doc)

# ================================================================ BUILD
def thank_you():
    """Confirmation page the /api/quote function 303-redirects to after a successful send. Noindex."""
    body = "\n".join([
        page_hero("Thank You &mdash; We&rsquo;ve Got Your Enquiry",
                  "Your message is on its way to our team. We&rsquo;ll be in touch shortly &mdash; usually the same working day.",
                  "orwell-van-on-customer-driveway", kicker="Enquiry received", cta=False),
        section(prose(
            '<h2 class="relative leading-tight text-black">What Happens Next</h2>'
            '<p>Thanks for getting in touch with <strong>Orwell Removals &amp; Storage</strong>. A friendly member of our '
            'family-run team has received your enquiry and will get back to you as soon as we can &mdash; usually within a '
            'few working hours. For larger moves we&rsquo;ll arrange a free, no-obligation survey at a time that suits you.</p>'
            f'<p>Need to reach us sooner? Call <a href="{B["phone_link"]}">{B["phone"]}</a> or email '
            f'<a href="mailto:{B["email"]}">{B["email"]}</a> &mdash; we&rsquo;re always happy to talk through your move.</p>'
            '<p>While you wait, you might find these useful:</p>'
            '<ul><li><a href="/services/">Our removals &amp; storage services</a></li>'
            '<li><a href="/pricing/">How our pricing works</a></li>'
            '<li><a href="/blog/">Moving tips &amp; Suffolk guides</a></li></ul>'
            '<p><a class="button-orange mt-2 inline-flex" href="/">Back to the homepage</a></p>'),
            bg="bg-white"),
    ])
    doc = E.render_page(
        title="Thank You | Orwell Removals & Storage",
        description="Thanks for your enquiry. The Orwell Removals & Storage team will be in touch shortly about your move across Ipswich and Suffolk.",
        canonical_path="/thank-you/", body=body,
        og_image="images/photos/orwell-van-on-customer-driveway.webp",
        robots="noindex, follow",
        breadcrumb=[("Home", "/"), ("Thank You", "/thank-you/")],
        active="", show_quote=False)
    return E.write("thank-you/index.html", doc)

def build():
    outs = [about_us(), pricing(), faq_page(), contact_us(), get_a_quote(),
            gallery(), reviews(), privacy_policy(), terms_conditions(), thank_you(), not_found()]
    for o in outs:
        print("wrote", os.path.relpath(o, E.S.ROOT))

if __name__ == "__main__":
    build()
