#!/usr/bin/env bash
# Renders the link preview image (og:image) for each page into images/og/.
# Requires ImageMagick 7. Run from anywhere: bin/og-images.sh

set -euo pipefail
cd "$(dirname "$0")/.."

GOTHIC=fonts/PathwayGothicOne-Regular.ttf
GARAMOND=fonts/EBGaramond-Variable.ttf
OUT=images/og
TEXT_X=470       # left edge of the text column
TEXT_WIDTH=670   # width of the text column
MAX_HEADING=130  # heading point size, shrunk to fit long words

tmp=$(mktemp -d "${TMPDIR:-/tmp}/og-images.XXXXXX")
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$OUT"

# Blurred, darkened banner as the background
magick images/banner-lg-min.webp -resize 300x300 -blur 0x25 -resize 1200x1200^ \
  -gravity center -crop 1200x630+0+0 +repage -fill '#050a24' -colorize 55% "$tmp/bg.png"

# Cover with drop shadow. It ends well above the bottom edge, where X overlays
# the domain in the bottom-left corner.
magick images/2d-cover-min.jpg -resize x500 \
  \( +clone -background black -shadow 70x14+0+10 \) +swap -background none -layers merge +repage \
  "$tmp/cover.png"
magick "$tmp/bg.png" "$tmp/cover.png" -gravity northwest -geometry +46+28 -composite "$tmp/base.png"

# slug|heading (\n for line breaks)|subtitle
while IFS='|' read -r slug heading subtitle; do
  [ -z "$slug" ] && continue
  heading=$(printf '%b' "$heading")

  # Largest point size up to MAX_HEADING at which the widest line fits
  width=$(magick -font "$GOTHIC" -pointsize 100 label:"$heading" -format '%w' info:)
  size=$(( 100 * TEXT_WIDTH / width ))
  [ "$size" -gt "$MAX_HEADING" ] && size=$MAX_HEADING

  magick "$tmp/base.png" \
    \( -background none \
       \( -font "$GOTHIC" -pointsize "$size" -fill '#fff36b' -interline-spacing -10 label:"$heading" \) \
       \( -size 1x36 xc:none \) \
       \( -size ${TEXT_WIDTH}x -font "$GARAMOND" -pointsize 46 -fill white caption:"$subtitle" \) \
       -gravity west -append \) \
    -gravity west -geometry +${TEXT_X}+0 -composite \
    -quality 85 "$OUT/$slug.jpg"
  echo "$OUT/$slug.jpg"
done <<'PAGES'
index|DER ANFANG\nDER UNENDLICHKEIT|Die offizielle Website zum Buch von David Deutsch
ausschnitt|AUSSCHNITT|Inhaltsverzeichnis und Leseprobe aus dem Buch von David Deutsch
glossar|GLOSSAR|Die zentralen Begriffe aus dem Buch von David Deutsch
zitate|ZITATE|Ausgewählte Passagen aus dem Buch von David Deutsch
pressestimmen|PRESSESTIMMEN|Was die Presse über das Buch von David Deutsch sagt
leserstimmen|LESERSTIMMEN|Was Leser über das Buch von David Deutsch sagen
interview|INTERVIEW|David Deutsch und Übersetzer Dennis Hackethal sprechen über das Buch
kontakt|KONTAKT|Für Leser, Presse und Buchhändler
mehr|INTERVIEWS, ARTIKEL,\nPODCASTS UND MEHR|Rund um David Deutsch und sein Buch
kaufen|JETZT KAUFEN|Als Taschenbuch und E-Book erhältlich
sokrates|EIN TRAUM\nVON SOKRATES|Kapitel 10 als Hörbuch – jetzt kostenlos anhören
wilhelm-busch|WO IST\nWILHELM BUSCH?|Das Gewinnspiel um einen versteckten Verweis im Buch
errata|ERRATA|Korrekturen zur deutschen Ausgabe, zusammengestellt vom Übersetzer
datenschutzerklaerung|DATENSCHUTZ-\nERKLÄRUNG|Wie diese Website mit Ihren Daten umgeht
PAGES
