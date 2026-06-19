#!/usr/bin/env python3
"""Rotate selected library photos to upright and re-encode to WebP <=200KB.
Usage: python3 rotate-photos.py 069:cw 070:cw 073:ccw ...
  cw  = 90 clockwise, ccw = 90 counter-clockwise, 180 = half turn.
"""
import sys, io
from pathlib import Path
from PIL import Image

LIB = Path(__file__).resolve().parent.parent / "_photo-library"
MAX = 204800

def encode_under(im, out):
    for q in (82,72,62,52,42,34):
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=q, method=6)
        if buf.tell() <= MAX or q == 34:
            out.write_bytes(buf.getvalue())
            return round(buf.tell()/1024), q
    return None, None

for arg in sys.argv[1:]:
    num, _, d = arg.partition(":")
    p = LIB / f"wolves-photo-{num}.webp"
    if not p.exists():
        print(f"  MISSING {p.name}"); continue
    im = Image.open(p).convert("RGB")
    if d == "cw":   im = im.rotate(-90, expand=True)
    elif d == "ccw":im = im.rotate(90, expand=True)
    elif d == "180":im = im.rotate(180, expand=True)
    else: print(f"  bad dir {d} for {num}"); continue
    kb, q = encode_under(im, p)
    print(f"  {p.name}: rotated {d} -> {im.width}x{im.height}, {kb}KB q{q}")
print("done")
