#!/usr/bin/env bash
# Renders the footer's pencil drawing into images/footer/ from the homepage banner:
#
#   sky-1200.webp, sky-1600.webp  the drawing, without his pointing arm
#   sky-phone.webp                its right part (x 850-2400), which is all phones show
#   arm-1.webp … arm-4.webp       his arm pointing at each of the four links, cut out so the
#                                 footer can swing it between them about his shoulder
#   sky-tile.webp                 seamless sky that fills the sides on wide screens
#
# Everything is drawn in a 2400x1080 space. The man and his rock come from the
# banner's bottom-right corner (420x460+1080+1040), scaled 1.5x and placed at
# +1650+390. The footer's markup and CSS rely on that geometry (shoulder at
# 1927,556; fingertip at 1813,429), so update them together.
#
# Requires ImageMagick 7 and Python 3 (standard library only). Takes a few
# minutes. Run from anywhere: bin/footer-drawing/build.sh

set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/../.."
root=$(pwd)
OUT=${OUT:-images/footer}
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)

tmp=$(mktemp -d "${TMPDIR:-/tmp}/footer-drawing.XXXXXX")
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"
cp "$here"/*.fx .
BANNER="$root/images/banner-lg-min.webp"
CROP=420x460+1080+1040
ARM_LIFT=0.15
# The arm's angle for each footer link, in degrees clockwise from where the
# banner has it. application.css turns the arm by these, so keep them in step.
ARM_POSES=(-10.7 -27.0 -41.9 -57.5)
# Where the arm images go in the drawing; every pose fits inside
ARM_BOX=260x250+1730+390

# --- The man and his rock -----------------------------------------------------
magick "$BANNER" -crop $CROP +repage -resize 200% -channel B -separate -blur 0x2 -threshold 65% -negate -compress none pgm:blue.pgm
magick "$BANNER" -crop $CROP +repage -resize 200% -colorspace gray -blur 0x1.5 -threshold 60% -negate -compress none pgm:gray.pgm
python3 "$here/figure.py" blue.pgm gray.pgm fig.pbm
magick fig.pbm -resize 630x690! -blur 0x0.8 -negate figmask.png
# The rock melts into the Earth on its left
magick -size 690x630 gradient:black-white -rotate -90 -level 0,22% fadeL.png
magick figmask.png fadeL.png -compose multiply -composite fullmask.png
# His arm: everything beyond a cut across the shoulder, plus a round joint as
# thick as the arm, centred on the pivot it turns about
magick figmask.png -fx '(-27*(j-132) - 58*(i-292) > 0 && i < 320 && j < 215) ? u : 0' armside.png
magick -size 630x690 xc:black -fill white -draw "circle 277,166 277,187" -blur 0x0.8 pivot.png
magick armside.png pivot.png -compose lighten -composite armmask.png
# His shading, from the banner's brightness. The sleeve is darker there than
# his torso, which stands out once the arm moves, so lighten the arm a little,
# easing in from the shoulder joint so there's no seam. Lightening it more
# thins out its cross-hatching, which looks just as wrong.
magick "$BANNER" -crop $CROP +repage -resize 630x690! -colorspace gray -fx '0.05 + 0.78*pow(u, 2.3)' figtone.png
magick figtone.png \( armside.png -blur 0x2 \) -fx "u + $ARM_LIFT*v*min(1, max(0, (hypot(i-277, j-166) - 21)/35))" figtone.png
magick figmask.png armside.png -compose minus_src -composite pivot.png -compose lighten -composite fadeL.png -compose multiply -composite bodymask.png

# --- Tone ---------------------------------------------------------------------
# Multi-octave smooth noise: out W H cell-width cell-height seed
fbm() {
  local out=$1 w=$2 h=$3 sx=$4 sy=$5 seed=$6 args=() k
  for k in 1 2 4 8 16; do
    args+=( \( -size $(( w*k/sx + 2 ))x$(( h*k/sy + 2 )) xc:gray50 -seed $((seed+k)) +noise Random -channel R -separate +channel -resize ${w}x${h}! -evaluate multiply "$(echo "scale=4; 0.5/$k" | bc)" \) )
  done
  magick "${args[@]}" -background black -compose plus -flatten -auto-level -colorspace gray "$out"
}
fbm iso.png 2400 1080 260 260 10
fbm cloud.png 2400 1080 200 40 30
magick -size 2400x1080 xc:gray50 -seed 77 +noise Gaussian -colorspace gray -blur 0x0.7 -auto-level \
  \( +clone -shade 120x45 -auto-level \) -compose overlay -composite -level 15%,85% tooth.png
magick -size 2400x1080 xc:black iso.png cloud.png -fx @tone.fx -colorspace gray tone_bg.png

# --- Strokes, stars, the ring, city lights and the rocket ---------------------
python3 "$here/strokes.py" .
python3 "$here/erase.py" .
for n in sky1 sky2 sky3 sky4 earth1 earth2 earth3 fig1 fig2 fig3 fig4; do
  magick -size 2400x1080 xc:white -draw @$n.mvg -colorspace gray $n.png &
done
wait
magick -size 2400x1080 xc:black -draw @stars.mvg -blur 0x0.5 stars.png
magick -size 2400x1080 xc:black -draw @glints.mvg -blur 0x0.6 glints.png
magick -size 2400x1080 xc:black -draw @ring.mvg -blur 0x0.6 ring.png
python3 "$here/extras.py" .
magick -size 2400x1080 xc:black -draw @lights.mvg -blur 0x0.5 \
  \( -size 2400x1080 xc:black -draw @lights-glow.mvg -blur 0x6 \) -compose plus -composite lights.png
magick -size 2400x1080 xc:black -draw @rocket.mvg -blur 0x0.6 \
  \( -size 2400x1080 xc:black -draw @rocket-glow.mvg -blur 0x9 \) -compose lighten -composite rocket.png
magick -size 2400x1080 xc:black -draw @rocket-ink.mvg -blur 0x0.5 rocket-ink.png

# --- The drawing without his arm, and the arm in each pose -------------------
render() {
  local m=$1 tone=$2
  magick $tone ${m}mask.png -alpha off -compose copy_opacity -composite figtone_$m.png
  magick -size 2400x1080 xc:black ${m}mask.png -geometry +1650+390 -compose over -composite -colorspace gray figA_$m.png
  magick figA_$m.png -morphology Edge Disk:1.2 -level 10%,70% figEdge_$m.png
  magick tone_bg.png figtone_$m.png -geometry +1650+390 -compose over -composite tone_$m.png
  magick tone_$m.png figA_$m.png sky1.png sky2.png sky3.png sky4.png earth1.png earth2.png earth3.png \
    fig1.png fig2.png fig3.png fig4.png tooth.png figEdge_$m.png -fx @pencil.fx -colorspace gray pencil0_$m.png
  magick pencil0_$m.png stars.png glints.png ring.png figA_$m.png tooth.png iso.png lights.png rocket.png rocket-ink.png \
    -fx @post.fx -colorspace gray pencil_$m.png
}
render body figtone.png
# Each pose is drawn in place rather than turned from one image: turning an
# image resamples it, which smears the hatching into flat grey
for i in 1 2 3 4; do
  a=${ARM_POSES[$((i-1))]}
  magick armmask.png -virtual-pixel black -distort SRT "277,166 1 $a" armmask_$i.png
  magick figtone.png -virtual-pixel edge -distort SRT "277,166 1 $a" armtone_$i.png
  magick figtone.png armtone_$i.png armmask_$i.png -composite figtone_$i.png
  magick bodymask.png armmask_$i.png -compose lighten -composite pose${i}mask.png
  render pose$i figtone_$i.png
  magick -size 2400x1080 xc:black armmask_$i.png -geometry +1650+390 -compose over -composite -colorspace gray \
    -morphology Dilate Disk:1.5 armA_$i.png
  # the box must hold the whole arm
  all=$(magick armA_$i.png -format '%[fx:mean*w*h]' info:)
  boxed=$(magick armA_$i.png -crop $ARM_BOX +repage -format '%[fx:mean*w*h]' info:)
  awk -v a="$all" -v b="$boxed" 'BEGIN { exit (a - b > 1) }' || { echo "Arm pose $i sticks out of ARM_BOX" >&2; exit 1; }
  magick pencil_pose$i.png armA_$i.png -alpha off -compose copy_opacity -composite -crop $ARM_BOX +repage arm-$i.png
done

# --- Seamless sky for the sides -----------------------------------------------
python3 "$here/tile.py" .
# Noise that wraps: each octave is resized three tiles wide and the middle one kept
args=()
for k in 1 2 4 8 16; do
  args+=( \( -size $((5*k))x$((4*k+1)) xc:gray50 -seed $((40+k)) +noise Random -channel R -separate +channel \
    \( +clone \) \( +clone \) +append -filter Gaussian -resize 3600x1080! -crop 1200x1080+1200+0 +repage \
    -evaluate multiply "$(echo "scale=4; 0.5/$k" | bc)" \) )
done
magick "${args[@]}" -background black -compose plus -flatten -auto-level -colorspace gray t_iso.png
magick -size 1200x1080 xc:gray50 -seed 77 +noise Gaussian -colorspace gray -virtual-pixel tile -blur 0x0.7 -auto-level \
  \( +clone -virtual-pixel tile -shade 120x45 -auto-level \) -compose overlay -composite -level 15%,85% t_tooth.png
for n in sky1 sky2 sky3 sky4; do
  magick -size 1200x1080 xc:white -draw @t_$n.mvg -colorspace gray t_$n.png &
done
wait
magick -size 1200x1080 xc:black -draw @t_stars.mvg -blur 0x0.5 t_stars.png
magick -size 1200x1080 xc:black -draw @t_glints.mvg -blur 0x0.6 t_glints.png
magick -size 1200x1080 xc:black t_iso.png -fx @tile-tone.fx -colorspace gray t_tone.png
magick t_tone.png t_sky1.png t_sky2.png t_sky3.png t_sky4.png t_tooth.png t_stars.png t_glints.png t_iso.png \
  -fx @tile-pencil.fx -colorspace gray t_pencil.png

# --- Export, on paper the colour of the page (floralwhite) --------------------
paper() {
  magick "$1" -colorspace gray -colorspace sRGB -type TrueColor \
    \( +clone -fill '#fffaf0' -draw 'color 0,0 reset' \) -compose multiply -composite "$2"
}
paper pencil_body.png body.png
paper t_pencil.png tile.png
WEBP=(-quality 30 -define webp:method=6)
magick body.png -crop 1550x1080+850+0 +repage -resize 800x "${WEBP[@]}" "$OUT/sky-phone.webp"
magick body.png -resize 1200x "${WEBP[@]}" "$OUT/sky-1200.webp"
magick body.png -resize 1600x "${WEBP[@]}" "$OUT/sky-1600.webp"
magick tile.png -resize 800x "${WEBP[@]}" "$OUT/sky-tile.webp"
# The arm at the same scale as sky-1600, resized the same way, so its hatching
# stays as crisp as the rest of him instead of the browser blurring it to grey
for i in 1 2 3 4; do
  magick arm-$i.png \( +clone -alpha off -fill '#fffaf0' -draw 'color 0,0 reset' \) -compose multiply -composite \
    arm-$i.png -compose copy_opacity -composite -resize 66.667% -quality 80 -define webp:alpha-quality=80 "$OUT/arm-$i.webp"
done
echo "Wrote $OUT"
# Point the pages at the new images, so browsers don't show cached old ones
if [ "$OUT" = "$root/images/footer" ]; then
  "$root/bin/version-assets.sh"
fi
