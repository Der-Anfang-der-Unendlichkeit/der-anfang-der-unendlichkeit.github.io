#!/usr/bin/env bash
# Stamps a hash of each versioned asset's content onto the URLs that load it
# (`/images/footer/arm.webp?v=1a2b3c4d`), so a deploy that changes an asset
# also changes its URL and browsers can't keep showing a cached old copy.
# GitHub Pages lets browsers cache files for 10 minutes. Run after changing
# application.css or anything in images/footer/. Run from anywhere:
# bin/version-assets.sh

set -euo pipefail
cd "$(dirname "$0")/.."

# Replaces every reference to $1 (with or without an old ?v=) in the given files
stamp() {
  local asset=$1; shift
  local h; h=$(md5 -q "$asset" | cut -c1-8)
  local re; re=$(printf '%s' "/$asset" | sed 's/[.]/\\./g')
  sed -i '' -E "s#${re}(\?v=[0-9a-f]+)?#/${asset}?v=${h}#g" "$@"
}

# The stylesheet loads the sky tile, so stamp it before hashing the stylesheet
for f in images/footer/*.webp; do
  stamp "$f" application.css *.html
done
stamp application.css *.html
