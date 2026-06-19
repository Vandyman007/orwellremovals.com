#!/usr/bin/env python3
"""Rename wolves-photo-NNN.webp -> short descriptive SEO slugs (3-6 words).
Validates word-count (3-6) + uniqueness + file existence before touching anything.
Updates INDEX.csv new_name column, then regenerates INDEX.html."""
import csv, sys, subprocess
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "_photo-library"
CSV = LIB / "INDEX.csv"

# number -> 3-6 word kebab slug (no extension)
NAMES = {
 "001":"elegant-lounge-before-house-removals",
 "002":"loading-mirror-into-removal-van",
 "003":"lapada-approved-service-provider-badge",
 "004":"lapada-art-antiques-dealers-badge",
 "005":"antique-drawing-room-fine-art-removals",
 "006":"trustyourmove-home-moving-member-badge",
 "007":"fine-art-room-antiques-removals",
 "008":"moving-made-easy-fleet-banner",
 "009":"wolves-removals-storage-info-leaflet",
 "010":"wolves-removals-wolf-head-logo",
 "011":"wolves-removals-grey-emblem-logo",
 "012":"wooden-crate-packed-wrapped-antiques",
 "013":"loading-wooden-crate-into-lorry",
 "014":"empty-period-drawing-room-sea-view",
 "015":"empty-lounge-fireplace-before-removals",
 "016":"empty-period-dining-room-chandelier",
 "017":"wolves-removals-van-fleet-countryside",
 "018":"wolves-removal-lorry-fleet-field",
 "019":"fleet-of-removal-vans-sussex",
 "020":"removal-vans-and-lorries-parked-field",
 "021":"storage-containers-and-lorry-field",
 "022":"row-of-mobile-storage-containers",
 "023":"wolves-self-storage-containers-field",
 "024":"wolves-storage-units-countryside-field",
 "025":"storage-containers-lined-up-field",
 "026":"removal-lorry-fleet-sussex-countryside",
 "027":"wolves-removals-truck-fleet-field",
 "028":"storage-warehouse-containers-with-forklift",
 "029":"container-storage-warehouse-interior",
 "030":"wolves-clipboard-in-storage-warehouse",
 "031":"forklift-moving-storage-crate-warehouse",
 "032":"removal-van-outside-storage-warehouse",
 "033":"packing-wrapped-furniture-house-clearance",
 "034":"classical-sculpture-fine-art-removals",
 "035":"antique-relief-sculptures-fine-art",
 "036":"outdoor-garden-statues-sculpture-removals",
 "037":"wrapping-furniture-with-protective-packing",
 "038":"loading-wooden-crates-into-van",
 "039":"carrying-export-crate-to-van",
 "040":"loading-box-into-removal-van",
 "041":"handling-wrapped-furniture-storage-barn",
 "042":"loading-wrapped-furniture-onto-lorry",
 "043":"team-preparing-dining-table-move",
 "044":"carrying-box-through-storage-warehouse",
 "045":"wrapping-armchair-in-living-room",
 "046":"packing-books-into-moving-boxes",
 "047":"aerial-removal-van-house-driveway",
 "048":"carrying-wrapped-item-storage-warehouse",
 "049":"wrapping-table-top-protective-cover",
 "050":"packing-furniture-boxes-home-removals",
 "051":"wrapping-living-room-furniture-removals",
 "052":"wrapping-wooden-dining-table-cover",
 "053":"secure-container-storage-warehouse-interior",
 "054":"removal-van-beside-storage-containers",
 "055":"removal-van-inside-storage-facility",
 "056":"storage-warehouse-aisle-wooden-containers",
 "057":"forklift-stacking-storage-containers-warehouse",
 "059":"carrying-wardrobe-into-house-hallway",
 "060":"building-wooden-export-crate-fine-art",
 "061":"carrying-export-crate-outside-townhouse",
 "062":"carrying-packed-item-into-property",
 "063":"movers-with-fragile-mirror-crate",
 "064":"large-flat-wooden-export-crate",
 "065":"handling-gilt-framed-antique-painting",
 "066":"wolves-removals-crew-beside-van",
 "067":"hanging-antique-portrait-fine-art",
 "068":"installing-framed-antique-portrait-removals",
 "069":"wolves-removals-lorry-and-crew",
 "070":"removal-vans-at-customer-property",
 "072":"room-of-wrapped-furniture-removals",
 "073":"carrying-wrapped-round-antique-table",
 "074":"loading-wrapped-boxes-at-doorway",
 "075":"two-vans-at-country-house",
 "076":"lapada-approved-service-provider-white",
 "077":"lapada-approved-provider-emblem-light",
 "078":"lapada-approved-service-provider-dark",
 "079":"lapada-approved-provider-emblem-charcoal",
 "080":"lapada-art-antiques-dealers-white",
 "081":"lapada-art-antiques-dealers-dark",
 "082":"lapada-member-antiques-dealers-emblem",
 "083":"wolves-removals-justin-lloyd-logos",
 "084":"wolves-removals-wolf-head-emblem",
 "085":"your-moving-group-member-badge",
 "086":"wrapped-mattresses-furniture-storage-packing",
 "087":"wrapped-furniture-protective-covers-removals",
 "088":"building-wooden-crate-for-fine-art",
 "089":"loading-furniture-into-street-van",
 "090":"removal-van-rear-loading-doors",
 "091":"wrapped-furniture-boxes-living-room",
 "092":"loading-crates-into-street-van",
 "093":"movers-with-fragile-front-crate",
 "094":"craning-bronze-statue-in-garden",
 "095":"flat-mirror-art-export-crate",
 "096":"carrying-furniture-up-staircase",
 "097":"congratulations-new-home-wolves-card",
 "098":"carrying-wrapped-items-into-house",
 "099":"carrying-gilt-framed-landscape-painting",
 "100":"wolves-removals-team-beside-van",
 "101":"wolves-removals-lorry-at-barn",
 "102":"wolves-removals-crew-beside-lorry",
 "103":"packing-wrapped-bed-in-bedroom",
 "104":"wrapped-antique-round-table-packing",
 "105":"removal-vans-at-stately-home",
 "106":"lifting-garden-bronze-sculpture-removals",
 "107":"craning-bronze-horse-statue-garden",
 "108":"hoisting-bronze-garden-statue-removal",
 "109":"hanging-antique-oil-portrait-wall",
 "110":"installing-antique-portrait-painting-wall",
 "111":"carrying-potted-palm-plant-garden",
 "112":"removal-van-on-customer-driveway",
 "113":"wolves-removals-brochure-marketing-folder",
 "114":"removal-lorry-on-residential-street",
 "115":"carrying-wrapped-mirror-house-move",
 "116":"games-room-snooker-table-interior",
 "117":"wrapping-round-dining-table-packing",
 "118":"framed-mirror-in-wooden-crate",
 "119":"wooden-crate-packing-detail-fine-art",
 "120":"wrapping-ornate-gilt-framed-mirror",
 "121":"two-movers-with-front-export-crate",
 "122":"carrying-gilt-framed-antique-painting",
 "123":"wheeling-export-crate-on-trolley",
 "124":"mover-walking-to-van-barn",
 "125":"packing-small-item-into-box",
 "126":"packing-cardboard-box-home-removals",
 "127":"loading-wooden-crates-storage-container",
 "128":"loading-crates-into-storage-container",
 "129":"carrying-wooden-export-crate-outdoors",
 "130":"handling-storage-crates-at-container",
 "131":"loading-wooden-crate-into-container",
 "132":"loading-crate-into-container-barn",
 "133":"carrying-boxes-into-barn-van",
 "134":"loading-furniture-onto-storage-van",
 "135":"packing-furniture-boxes-in-lounge",
 "136":"packing-items-at-dining-table",
 "137":"movers-taping-cardboard-box-packing",
 "138":"aerial-removal-van-country-lane",
 "139":"drone-removal-van-country-property",
 "140":"aerial-removal-van-garden-driveway",
 "141":"drone-removal-van-country-driveway",
 "142":"loading-wrapped-panels-storage-container",
 "143":"packing-cardboard-boxes-in-room",
 "144":"packing-boxes-and-wrapped-items",
 "145":"two-removal-lorries-residential-street",
 "146":"wrapped-mattresses-furniture-storage-room",
 "147":"wrapped-furniture-protective-covers-packing",
 "148":"packed-wrapped-furniture-ready-removal",
 "149":"wrapped-antique-round-table-storage",
 "150":"mover-with-wrapped-dining-set",
 "151":"wrapped-dining-table-and-chairs",
 "152":"packing-furniture-in-attic-bedroom",
 "153":"packing-items-in-loft-bedroom",
 "154":"wrapping-large-furniture-protective-cover",
 "155":"removal-lorry-at-stately-home",
 "156":"antique-furniture-drawing-room-interior",
 "157":"carrying-antique-piano-specialist-removals",
 "158":"two-removal-vans-at-country-house",
 "159":"loading-packed-boxes-into-lorry",
 "160":"wolves-removals-logo-white-background",
 "161":"wolves-removals-emblem-white-background",
 "162":"two-vans-outside-red-brick-house",
 "163":"wolves-storage-logo-black-background",
 "164":"wolves-storage-emblem-grey-background",
 "165":"wolves-removals-storage-certificate-recognition",
}

# ---- validate ----
errs=[]
slugs=list(NAMES.values())
dups={s for s in slugs if slugs.count(s)>1}
if dups: errs.append(f"duplicate slugs: {dups}")
for num,slug in NAMES.items():
    wc=len(slug.split("-"))
    if wc<3 or wc>6: errs.append(f"{num}: '{slug}' has {wc} words (need 3-6)")
    if not (LIB/f"wolves-photo-{num}.webp").exists():
        errs.append(f"{num}: source file missing")
# any library files not covered?
present={p.name.replace('wolves-photo-','').replace('.webp','')
         for p in LIB.glob('wolves-photo-*.webp')}
missing=present-set(NAMES)
if missing: errs.append(f"library photos with no name mapping: {sorted(missing)}")

if errs:
    print("VALIDATION FAILED — nothing renamed:")
    for e in errs: print("  -",e)
    sys.exit(1)

dry = "--apply" not in sys.argv
print(f"{'DRY RUN' if dry else 'APPLYING'}: {len(NAMES)} renames, all 3-6 words, all unique.")
wc_dist={}
for s in slugs: wc_dist[len(s.split('-'))]=wc_dist.get(len(s.split('-')),0)+1
print("word-count spread:", dict(sorted(wc_dist.items())))
if dry:
    for n in list(NAMES)[:5]: print(f"  {n} -> {NAMES[n]}.webp")
    print("  ... run with --apply to execute"); sys.exit(0)

# ---- apply rename ----
for num,slug in NAMES.items():
    (LIB/f"wolves-photo-{num}.webp").rename(LIB/f"{slug}.webp")

# ---- update INDEX.csv ----
rows=list(csv.DictReader(open(CSV)))
for r in rows:
    num=r["new_name"].replace("wolves-photo-","").replace(".webp","")
    if num in NAMES: r["new_name"]=f"{NAMES[num]}.webp"
with open(CSV,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f"renamed {len(NAMES)} files + updated INDEX.csv")
