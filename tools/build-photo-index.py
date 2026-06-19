#!/usr/bin/env python3
"""Build INDEX.html contact sheet for _photo-library so the user can browse,
pick keepers, and delete rejects. Reads INDEX.csv for the new->original mapping,
re-reads each webp for live size/dimensions."""
import csv, os, subprocess
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "_photo-library"
CSV = LIB / "INDEX.csv"

def dims(p):
    try:
        out = subprocess.run(["sips","-g","pixelWidth","-g","pixelHeight",str(p)],
                              capture_output=True, text=True).stdout
        w = next((l.split()[1] for l in out.splitlines() if "pixelWidth" in l), "?")
        h = next((l.split()[1] for l in out.splitlines() if "pixelHeight" in l), "?")
        return f"{w}×{h}"
    except Exception:
        return "?"

rows = []
with open(CSV) as f:
    for r in csv.DictReader(f):
        nn = r["new_name"]
        p = LIB / nn
        if not p.exists():
            continue
        kb = round(p.stat().st_size/1024)
        rows.append({"new": nn, "orig": r["original_file"], "folder": r["source_folder"],
                     "dims": dims(p), "kb": kb})

rows.sort(key=lambda x: x["new"])
total = len(rows)

cards = []
for r in rows:
    cards.append(f"""
    <figure class="card" data-name="{r['new']}" data-folder="{r['folder']}">
      <a href="{r['new']}" target="_blank"><img loading="lazy" src="{r['new']}" alt="{r['orig']}"></a>
      <figcaption>
        <strong>{r['new']}</strong>
        <span class="orig" title="{r['folder']}/{r['orig']}">{r['orig']}</span>
        <span class="meta">{r['dims']} · {r['kb']}KB · {r['folder']}</span>
      </figcaption>
    </figure>""")

folders = sorted({r["folder"] for r in rows})
chips = " ".join(f'<button class="chip" onclick="flt(this,\'{f}\')">{f}</button>' for f in folders)

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wolves Photo Library — {total} photos</title>
<style>
 :root{{--orange:#FC9700}}
 *{{box-sizing:border-box}}
 body{{font-family:-apple-system,Barlow,Segoe UI,sans-serif;margin:0;background:#1c1f22;color:#e8eaed}}
 header{{position:sticky;top:0;background:#15171a;padding:14px 20px;border-bottom:3px solid var(--orange);z-index:10}}
 h1{{margin:0 0 8px;font-size:20px}} h1 span{{color:var(--orange)}}
 .hint{{font-size:13px;color:#9aa0a6;margin:0 0 10px}}
 .chips{{display:flex;flex-wrap:wrap;gap:6px}}
 .chip{{background:#2a2e33;color:#cfd3d8;border:1px solid #3a3f45;border-radius:14px;padding:4px 11px;font-size:12px;cursor:pointer}}
 .chip.on{{background:var(--orange);color:#1c1f22;border-color:var(--orange);font-weight:600}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;padding:18px}}
 .card{{margin:0;background:#24282c;border-radius:8px;overflow:hidden;border:1px solid #31363b}}
 .card img{{width:100%;height:260px;object-fit:contain;display:block;background:#000}}
 figcaption{{padding:7px 9px;display:flex;flex-direction:column;gap:2px}}
 figcaption strong{{color:var(--orange);font-size:12.5px}}
 .orig{{font-size:11.5px;color:#cfd3d8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
 .meta{{font-size:10.5px;color:#7e858c}}
 .hide{{display:none}}
</style></head><body>
<header>
  <h1>Wolves Photo Library — <span>{total}</span> photos</h1>
  <p class="hint">Click a thumb to open full size. Filter by source folder below. To reject a photo, delete its <code>wolves-photo-NNN.webp</code> file from <code>_photo-library/</code>. When you're done picking, tell me and I'll give the keepers descriptive SEO filenames.</p>
  <div class="chips"><button class="chip on" onclick="flt(this,'')">All ({total})</button>{chips}</div>
</header>
<div class="grid" id="grid">{''.join(cards)}</div>
<script>
function flt(btn,f){{
  document.querySelectorAll('.chip').forEach(c=>c.classList.remove('on'));
  btn.classList.add('on');
  document.querySelectorAll('.card').forEach(c=>{{
    c.classList.toggle('hide', f && c.dataset.folder!==f);
  }});
}}
</script>
</body></html>"""

(LIB / "INDEX.html").write_text(html)
print(f"Wrote INDEX.html with {total} photos across {len(folders)} folders.")
