# -*- coding: utf-8 -*-
"""Site-wide configuration for Orwell Removals & Storage static build.
Single source of truth for contact details, navigation, footer, services and locations.
Read by tools/engine.py and the render scripts. Cloned from the Wolves config and
rebranded for Orwell (Ipswich / Suffolk removals + storage; NOT BAR; no calculators).
"""
import os, re

SITE_URL = "https://orwellremovals.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BUSINESS = {
    "name": "Orwell Removals & Storage",
    "legal_name": "Orwell Removals & Storage",
    "tagline": "First Impressions Count — Removals & Storage in Ipswich & Suffolk",
    "phone": "01473 411531",
    "phone_link": "tel:+441473411531",
    "mobile": "",
    "mobile_link": "",
    "whatsapp": "",
    "whatsapp_link": "",
    "email": "sales@orwellremovals.com",      # primary / quotes
    "email_info": "info@orwellremovals.com",   # general enquiries
    "street": "Old Station Works, Main Road, Westerfield",
    "locality": "Ipswich",
    "region": "Suffolk",
    "postcode": "IP6 9AB",
    "area_served": ["Ipswich", "Suffolk", "Bury St Edmunds", "Felixstowe",
                    "Woodbridge", "Stowmarket", "Sudbury", "Lowestoft"],
    "geo": {"lat": "52.0853", "lng": "1.1662"},  # Westerfield, Ipswich (approx)
    "founded": "2005",  # "Moving goods since 2005" — real founding year (old live site)
    "hours": "Mo-Fr 08:00-18:00, Sa 09:00-13:00",
}

# No verified public social profiles to link yet — leave empty rather than fabricate.
SOCIAL = {}

# Real, verifiable trust signals only — never invent (E-E-A-T + GDPR). NOT a BAR member.
# No third-party review/rating references on the site (per brief): no Checkatrade / "rated" badges.
ACCREDITATIONS = ["Fully covered (Basil Fry)", "Euro 6 fleet", "Family-run since 2005"]
TRUSTED_BY = ["Ipswich Borough Council"]

# ---- Services (slug, label) — order/labels mirror the main menu ----
SERVICES = [
    ("services/home-removals/", "Home Removals"),
    ("services/office-removals/", "Office Removals"),
    ("services/commercial-removals/", "Commercial Removals"),
    ("services/long-distance-removals/", "Long Distance Removals"),
    ("services/man-and-van/", "Man & Van"),
    ("services/piano-removals/", "Piano Removals"),
    ("services/packing-service/", "Packing Service"),
    ("services/storage/", "Storage"),
]
STORAGE = [
    ("services/storage/", "Storage"),
    ("services/storage/household-storage/", "Household Storage"),
    ("services/storage/business-storage/", "Business Storage"),
]
COUNTY_HUBS = [
    ("locations/suffolk-removals/", "Suffolk"),
]

# ---- Suffolk towns (Suffolk-only build). (path, name) ----
_LOCATIONS = [
    ("locations/ipswich-removals/", "Ipswich"),
    ("locations/bury-st-edmunds-removals/", "Bury St Edmunds"),
    ("locations/felixstowe-removals/", "Felixstowe"),
    ("locations/lowestoft-removals/", "Lowestoft"),
    ("locations/woodbridge-removals/", "Woodbridge"),
    ("locations/stowmarket-removals/", "Stowmarket"),
    ("locations/sudbury-removals/", "Sudbury"),
    ("locations/newmarket-removals/", "Newmarket"),
    ("locations/haverhill-removals/", "Haverhill"),
    ("locations/beccles-removals/", "Beccles"),
    ("locations/aldeburgh-removals/", "Aldeburgh"),
    ("locations/framlingham-removals/", "Framlingham"),
    ("locations/hadleigh-removals/", "Hadleigh"),
    ("locations/needham-market-removals/", "Needham Market"),
    ("locations/saxmundham-removals/", "Saxmundham"),
    ("locations/southwold-removals/", "Southwold"),
]

def _name_from_loc_slug(slug):
    s = slug.strip("/").split("/")[-1]
    s = s.replace("removals-", "").replace("-removals", "")
    return s.replace("-", " ").title()

def load_locations():
    """All Suffolk town /locations/ URLs → [(path, name)] (excludes the county hub)."""
    return list(_LOCATIONS)

# ---- Footer columns (label, [(text, href)]) ----
def footer_columns():
    return [
        ("Our Services", [
            ("Home Removals", "/services/home-removals/"),
            ("Office Removals", "/services/office-removals/"),
            ("Commercial Removals", "/services/commercial-removals/"),
            ("Long Distance Removals", "/services/long-distance-removals/"),
            ("Man & Van", "/services/man-and-van/"),
            ("Piano Removals", "/services/piano-removals/"),
        ]),
        ("Packing & Storage", [
            ("Packing Service", "/services/packing-service/"),
            ("Storage", "/services/storage/"),
            ("Household Storage", "/services/storage/household-storage/"),
            ("Business Storage", "/services/storage/business-storage/"),
        ]),
        ("Useful Links", [
            ("Pricing", "/pricing/"),
            ("Blog", "/blog/"),
            ("FAQs", "/frequently-asked-questions/"),
            ("Gallery", "/gallery/"),
            ("Reviews", "/reviews/"),
            ("About Us", "/about-us/"),
        ]),
        ("Areas We Cover", [
            ("Suffolk", "/locations/suffolk-removals/"),
            ("Ipswich", "/locations/ipswich-removals/"),
            ("Bury St Edmunds", "/locations/bury-st-edmunds-removals/"),
            ("Felixstowe", "/locations/felixstowe-removals/"),
            ("Woodbridge", "/locations/woodbridge-removals/"),
        ]),
    ]
