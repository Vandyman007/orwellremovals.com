#!/bin/bash
# Convert Jack's raw photos -> upright WebP <=200KB, sequential names, with a manifest.
# Orientation baked via sips (re-encode applies EXIF); resized to 1600px longest edge.
# PNGs kept as PNG through sips to preserve transparency (logos/badges).
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RAW="$ROOT/_photo-library/_raw"
OUT="$ROOT/_photo-library"
TMP="/tmp/jacks-convert"
MAX=204800          # 200 KB
EDGE=1600           # longest edge px
MANIFEST="$OUT/INDEX.csv"

rm -rf "$TMP"; mkdir -p "$TMP"
echo "new_name,original_file,source_folder,width,height,kb" > "$MANIFEST"

# collect images, sorted, stable
imgs=()
while IFS= read -r f; do imgs+=("$f"); done < <(find "$RAW" -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.heic' -o -iname '*.webp' \) \
  ! -name '.*' | sort)

total=${#imgs[@]}
echo "Found $total images to convert."
i=0; ok=0; fail=0
for src in "${imgs[@]}"; do
  i=$((i+1))
  n=$(printf "%03d" "$i")
  out="$OUT/wolves-photo-$n.webp"
  ext="${src##*.}"; extl=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
  orig="$(basename "$src")"
  folder="$(dirname "${src#$RAW/}")"

  # normalize -> temp (bake orientation + resize)
  if [ "$extl" = "png" ]; then
    tmp="$TMP/n.png"
    sips -s format png -Z "$EDGE" "$src" --out "$tmp" >/dev/null 2>&1
  else
    tmp="$TMP/n.jpg"
    sips -s format jpeg -Z "$EDGE" "$src" --out "$tmp" >/dev/null 2>&1
  fi
  if [ ! -f "$tmp" ]; then
    echo "  [FAIL] $orig (sips could not read)"; fail=$((fail+1))
    echo "\"(failed)\",\"$orig\",\"$folder\",,," >> "$MANIFEST"; continue
  fi

  # quality search to land <=200KB
  for q in 82 72 62 52 42; do
    cwebp -quiet -q "$q" -m 6 "$tmp" -o "$out" >/dev/null 2>&1
    sz=$(stat -f%z "$out" 2>/dev/null || echo 999999)
    [ "$sz" -le "$MAX" ] && break
  done

  dims=$(sips -g pixelWidth -g pixelHeight "$out" 2>/dev/null)
  w=$(echo "$dims" | awk '/pixelWidth/{print $2}')
  h=$(echo "$dims" | awk '/pixelHeight/{print $2}')
  kb=$(( ( $(stat -f%z "$out") + 512 ) / 1024 ))
  echo "wolves-photo-$n.webp,\"$orig\",\"$folder\",$w,$h,$kb" >> "$MANIFEST"
  ok=$((ok+1))
  [ $((i % 20)) -eq 0 ] && echo "  ...$i/$total"
done

rm -rf "$TMP"
echo "DONE: $ok converted, $fail failed, of $total."
echo "Largest outputs:"
ls -S "$OUT"/*.webp 2>/dev/null | head -3 | while read f; do echo "  $(( $(stat -f%z "$f")/1024 ))KB  $(basename "$f")"; done
