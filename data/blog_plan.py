# -*- coding: utf-8 -*-
"""Blog plan for Orwell Removals & Storage.

RULE (user): every content page shows EXACTLY 3 blog cards, relevant to that page, and no two
pages share the same 3 — so each blog belongs to exactly one page (total blogs = 3 x content
pages). Blog posts themselves don't carry the unique-3 feed (avoids infinite regression); they
link to related posts in the same category instead.

This module is the single source of truth for: which blogs exist, each blog's parent page,
title, category and image keyword. Blog BODY content lives in data/blog/<slug>.json (authored
separately). render_blog.py renders posts; engine.blog_feed(page_path) shows a page's 3 blogs.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import siteconfig as S

# (slug, title, category, image-keyword) tuples per parent page path.
# image-keyword steers the feed-card / hero photo via engine.match_photo().

def _town(slug, town):
    parent = "/locations/%s/" % slug
    key = slug.replace("-removals", "")
    return parent, [
        ("moving-to-%s-guide" % key, "Moving to %s: A Local Guide" % town, "Local Guides", "%s removals van" % town),
        ("%s-moving-day-checklist" % key, "%s Moving Day Checklist &amp; Tips" % town, "Moving Guides", "loading van boxes %s" % town),
        ("living-in-%s-area-guide" % key, "Living in %s: Areas &amp; Amenities" % town, "Local Guides", "%s house street" % town),
    ]

CORE = {
 "/": [
   ("moving-house-in-suffolk-guide", "Moving House in Suffolk: The Complete Guide", "Moving Guides", "removals lorry suffolk"),
   ("moving-day-tips-from-a-suffolk-team", "10 Moving Day Tips from a Suffolk Removals Team", "Moving Guides", "mover loading van driveway"),
   ("how-much-do-removals-cost-suffolk", "How Much Do Removals Cost in Suffolk?", "Pricing", "removals van street"),
 ],
 "/about-us/": [
   ("why-choose-a-family-run-removals-company", "Why Choose a Family-Run Removals Company", "Moving Guides", "orwell removals van home"),
   ("what-fully-covered-means-for-your-move", "What &lsquo;Fully Covered&rsquo; Really Means for Your Move", "Moving Guides", "wrapped furniture in van"),
   ("twenty-years-moving-suffolk", "Two Decades of Moving Suffolk: What We&rsquo;ve Learned", "Local Guides", "orwell removals lorry"),
 ],
 "/pricing/": [
   ("how-removals-pricing-works", "How Removals Pricing Works (No Hidden Extras)", "Pricing", "removals van driveway"),
   ("how-to-get-an-accurate-removals-quote", "How to Get an Accurate Removals Quote", "Pricing", "mover loading van"),
   ("ways-to-save-money-on-your-move", "Ways to Save Money on Your House Move", "Pricing", "packed boxes furniture"),
 ],
 "/frequently-asked-questions/": [
   ("first-time-mover-start-here", "First-Time Mover? Start Here", "Moving Guides", "loaded luton van street"),
   ("moving-day-what-to-expect", "Moving Day: What to Expect", "Moving Guides", "loading van boxes"),
   ("common-moving-mistakes-to-avoid", "Common Moving Mistakes to Avoid", "Moving Guides", "wrapped furniture boxes"),
 ],
 "/contact-us/": [
   ("how-to-book-your-move", "How to Book Your House Move", "Moving Guides", "orwell van customer driveway"),
   ("planning-your-move-first-steps", "Planning Your Move: The First Steps", "Moving Guides", "removals van suffolk home"),
   ("when-to-book-your-removals", "When Should You Book Your Removals?", "Moving Guides", "orwell removals lorry street"),
 ],
 "/get-a-quote/": [
   ("what-to-include-in-a-removals-enquiry", "What to Include When Asking for a Quote", "Pricing", "removals van driveway"),
   ("how-a-home-removals-survey-works", "How a Home Removals Survey Works", "Moving Guides", "mover loading van driveway"),
   ("understanding-your-removals-quote", "Understanding Your Removals Quote", "Pricing", "packed boxes wrapped furniture"),
 ],
 "/gallery/": [
   ("behind-the-scenes-of-a-house-move", "Behind the Scenes of a House Move", "Moving Guides", "orwell crew loading townhouse"),
   ("how-we-protect-your-belongings", "How We Protect Your Belongings on Moving Day", "Packing", "wrapped furniture strapped van"),
   ("a-day-with-a-removals-crew", "A Day in the Life of a Removals Crew", "Local Guides", "two orwell vans street"),
 ],
 "/reviews/": [
   ("what-makes-a-great-removals-experience", "What Makes a Great Removals Experience", "Moving Guides", "orwell van outside home"),
   ("questions-to-ask-before-booking-movers", "Questions to Ask Before Booking Movers", "Moving Guides", "removals van street"),
   ("how-to-have-a-smooth-house-move", "How to Have a Smooth, Stress-Free Move", "Moving Guides", "mover loading van driveway"),
 ],
 "/services/": [
   ("a-guide-to-our-removals-services", "A Guide to Our Removals &amp; Storage Services", "Moving Guides", "orwell lorry van home"),
   ("removals-packing-storage-together", "Removals, Packing &amp; Storage: How They Fit Together", "Storage", "van loaded boxes furniture"),
   ("choosing-the-right-moving-service", "Choosing the Right Moving Service for You", "Moving Guides", "removals van driveway"),
 ],
 "/locations/": [
   ("moving-across-suffolk-area-guide", "Moving Across Suffolk: An Area Guide", "Local Guides", "removals lorry suffolk street"),
   ("town-by-town-moving-tips-suffolk", "Town-by-Town Moving Tips for Suffolk", "Local Guides", "orwell van suffolk home"),
   ("choosing-where-to-live-in-suffolk", "Choosing Where to Live in Suffolk", "Local Guides", "suffolk house street"),
 ],
 "/locations/suffolk-removals/": [
   ("relocating-to-suffolk-newcomers-guide", "Relocating to Suffolk: A Newcomer&rsquo;s Guide", "Local Guides", "orwell removals lorry suffolk"),
   ("best-places-to-live-in-suffolk", "The Best Places to Live in Suffolk", "Local Guides", "suffolk home street"),
   ("moving-around-suffolk-what-to-know", "Moving Around Suffolk: What to Know", "Local Guides", "removals van suffolk"),
 ],
}

SERVICES = {
 "/services/home-removals/": [
   ("how-to-plan-a-stress-free-house-move", "How to Plan a Stress-Free House Move", "Moving Guides", "orwell crew loading house"),
   ("moving-house-checklist-8-weeks", "Moving House Checklist: 8 Weeks to Moving Day", "Moving Guides", "packed boxes wrapped furniture"),
   ("how-to-choose-a-removals-company", "How to Choose a Removals Company in Suffolk", "Moving Guides", "orwell removals van"),
 ],
 "/services/office-removals/": [
   ("how-to-plan-an-office-move", "How to Plan an Office Move with Minimal Downtime", "Business Moves", "orwell van packing moving storage"),
   ("office-relocation-checklist", "An Office Relocation Checklist for Suffolk Businesses", "Business Moves", "boxes loaded in van"),
   ("moving-your-business-it-and-files", "Moving Your Business: IT, Files &amp; Furniture", "Business Moves", "orwell boxes loaded van"),
 ],
 "/services/commercial-removals/": [
   ("relocating-a-shop-or-warehouse", "Relocating a Shop or Warehouse: A Practical Guide", "Business Moves", "orwell commercial shop move"),
   ("minimise-disruption-business-move", "How to Minimise Disruption During a Business Move", "Business Moves", "orwell box lorry street"),
   ("staging-a-commercial-move-with-storage", "Staging a Commercial Move with Storage", "Storage", "boxes loaded in van"),
 ],
 "/services/long-distance-removals/": [
   ("long-distance-moving-what-to-expect", "Long-Distance Moving from Suffolk: What to Expect", "Moving Guides", "orwell box lorry street"),
   ("how-to-prepare-for-a-long-distance-move", "How to Prepare for a Long-Distance Move", "Moving Guides", "loaded luton van"),
   ("packing-for-a-long-distance-move", "Packing for a Long-Distance Move", "Packing", "wrapped furniture in van"),
 ],
 "/services/man-and-van/": [
   ("man-and-van-vs-full-removal", "When to Choose Man &amp; Van vs a Full Removal", "Moving Guides", "orwell luton van road"),
   ("moving-a-single-item-guide", "Moving a Single Large Item: A Quick Guide", "Moving Guides", "mover loading van driveway"),
   ("student-and-small-flat-moving-tips", "Student &amp; Small-Flat Moving Tips", "Moving Guides", "luton van loading house"),
 ],
 "/services/piano-removals/": [
   ("how-to-prepare-a-piano-for-moving", "How to Prepare a Piano for Moving", "Pianos", "wrapped furniture strapped van"),
   ("why-use-specialist-piano-movers", "Why Use Specialist Piano Movers", "Pianos", "mover loading van driveway"),
   ("caring-for-your-piano-after-a-move", "Caring for Your Piano After a Move", "Pianos", "wrapped furniture in van"),
 ],
 "/services/packing-service/": [
   ("packing-tips-from-professional-movers", "Packing Tips from Professional Movers", "Packing", "wrapped packing materials"),
   ("how-to-pack-fragile-items-safely", "How to Pack Fragile Items Safely", "Packing", "packed boxes wrapped furniture"),
   ("the-right-packing-materials", "The Right Packing Materials for a Move", "Packing", "wrapped packing materials ready"),
 ],
 "/services/storage/": [
   ("when-do-you-need-removals-storage", "When Do You Need Removals Storage?", "Storage", "van loaded boxes furniture"),
   ("how-to-store-furniture-safely", "How to Store Furniture Safely", "Storage", "wrapped furniture loaded van"),
   ("decluttering-before-a-move", "Decluttering Before a Move with Storage", "Storage", "packed boxes wrapped furniture"),
 ],
 "/services/storage/household-storage/": [
   ("household-storage-when-it-helps", "Household Storage: When It Helps", "Storage", "wrapped furniture and boxes"),
   ("storing-belongings-during-a-renovation", "Storing Belongings During a Renovation", "Storage", "wrapped furniture in van"),
   ("downsizing-keep-store-or-let-go", "Downsizing: What to Keep, Store or Let Go", "Storage", "packed boxes wrapped furniture"),
 ],
 "/services/storage/business-storage/": [
   ("business-storage-for-stock-and-archives", "Business Storage for Stock &amp; Archives", "Business Moves", "orwell boxes loaded van"),
   ("using-storage-to-stage-an-office-move", "Using Storage to Stage an Office Move", "Business Moves", "boxes loaded in van"),
   ("seasonal-storage-for-suffolk-businesses", "Seasonal Storage for Suffolk Businesses", "Storage", "van loaded boxes furniture"),
 ],
}

def _build():
    pages = {}
    pages.update(CORE)
    pages.update(SERVICES)
    for slug, name in S.load_locations():
        sl = slug.strip("/").split("/")[-1]   # e.g. ipswich-removals
        parent, blogs = _town(sl, name)
        pages[parent] = blogs
    page_blogs, blogs, by_slug = {}, [], {}
    for parent, items in pages.items():
        slugs = []
        for slug, title, cat, kw in items:
            spec = {"slug": slug, "title": title, "category": cat, "kw": kw, "parent": parent}
            blogs.append(spec); by_slug[slug] = spec; slugs.append(slug)
        page_blogs[parent] = slugs
    return pages, page_blogs, blogs, by_slug

PAGES, PAGE_BLOGS, BLOGS, BY_SLUG = _build()

if __name__ == "__main__":
    print("content pages with a 3-blog feed:", len(PAGE_BLOGS))
    print("total blogs (3 x pages):", len(BLOGS))
    # uniqueness checks
    allslugs = [b["slug"] for b in BLOGS]
    assert len(allslugs) == len(set(allslugs)), "duplicate blog slug!"
    for p, sl in PAGE_BLOGS.items():
        assert len(sl) == len(set(sl)) == 3, "page %s not 3 unique blogs" % p
    print("OK: every page has 3 unique blogs; all slugs unique sitewide")
