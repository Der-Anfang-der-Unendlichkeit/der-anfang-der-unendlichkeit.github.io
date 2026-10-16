# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

The official website for *Der Anfang der Unendlichkeit*, Dennis Hackethal's
German translation of David Deutsch's *The Beginning of Infinity*. It lives at
deranfangderunendlichkeit.de and is hosted on GitHub Pages. All UI copy is
German.

The site is plain static HTML with no build step, no templating and no
JavaScript framework. It replaced an earlier Rails app.

## Preview

Paths are root-absolute (`/application.css`, `/images/…`), so opening files
directly from disk shows unstyled text. Serve the directory instead:

```bash
python3 -m http.server 8000
```

Python's server doesn't map `/glossar` to `glossar.html` the way GitHub Pages
does, so add `.html` when previewing locally.

## Structure

- Every page repeats the same `<head>`, header, nav and footer. A change to any
  of them has to be made in every top-level `.html` file, including `404.html`.
- Each page's `<h1>` has an `id` matching its URL, and nav links point to it
  (`/glossar#glossar`). The active nav item gets the `active` class.
- Each page sets its own `<title>` ("… · Der Anfang der Unendlichkeit"; the
  homepage's is "Der Anfang der Unendlichkeit von David Deutsch"), the
  matching `twitter:title`/`og:title`, `og:url`, a canonical link and a meta
  description (about 120–160 characters) that `twitter:description`/
  `og:description` repeat. New pages need all of these and an entry in
  `sitemap.xml`.
- Each page has exactly one `<h1>`. Where something else needs to look like a
  heading of another level, use Bootstrap's classes (`<h2 class="h1">`).
- The homepage carries the site's structured data (JSON-LD `WebSite` and
  `Book`). Keep it in sync when book details or retailers change.
- `pages/`, `xmas.html` and `rezensionen.html` are meta-refresh redirects from
  URLs the old site used. Keep them so old links and search results keep
  working.
- Glossary anchor ids are the entry titles transliterated and dasherized the
  way Rails' `parameterize` did it (`Mittelmäßigkeitsprinzip` →
  `mittelmassigkeitsprinzip`), so existing `#…` links keep working.
- Errata are listed in page order.

## Preview images

Each page has its own link preview image (`og:image`) in `images/og/`,
rendered by `bin/og-images.sh` (ImageMagick) from the heading and subtitle
listed at the bottom of that script. When a page's heading or content changes
enough that its image or subtitle no longer fits, update the list and rerun
the script. New pages need an entry there, too. Images keep the bottom-left
corner free, where X overlays the domain.

## Footer

The footer is a pencil drawing of the cover's scene with the footer links as a
constellation the man points at; hovering or focusing a link swings his arm
toward its star (CSS only, in `application.css` under `.site-footer`). The
drawing, his arm and the sky that tiles the sides on wide screens are in
`images/footer/`, rendered from the banner by `bin/footer-drawing/build.sh`.
The markup and CSS use the drawing's 2400×1080 coordinates (star positions,
the shoulder the arm turns about, the hover rotations), so if the drawing's
geometry changes, update them together. Phones get an image cropped to the
part they show; keep the images small, since they load on every page.
`overscroll.js` keeps the page from bouncing past the footer (which would
reveal the plain background below the drawing) while still letting it bounce
at the top.

## Assets

- Bootstrap 4.6 CSS is vendored; no JavaScript library is loaded.
- Pages load `application.css` and the footer images with `?v=` and the first
  8 characters of the file's MD5. GitHub Pages lets browsers cache files for 10
  minutes, so without a new URL a deploy can pair fresh markup with a stale
  stylesheet or image. After changing either, run `bin/version-assets.sh`
  (`bin/footer-drawing/build.sh` runs it itself).
- Fonts (EB Garamond, Pathway Gothic One) are self-hosted in `fonts/` under the
  SIL Open Font License, so the site loads nothing from font services. Keep it
  that way: any new third-party request needs a section in the privacy policy
  (`datenschutzerklaerung.html`).
- The site loads EB Garamond as WOFF2 files subset to Latin, Greek and common
  punctuation, made from the TTFs next to them (which `bin/og-images.sh` uses)
  with fonttools:
  `pyftsubset EBGaramond-Variable.ttf --unicodes='U+0000-036F,U+0370-03FF,U+1E00-1EFF,U+2000-206F,U+2070-209F,U+20A0-20CF,U+2100-214F,U+2190-21FF,U+2200-22FF,U+25CA,U+FB00-FB06' --layout-features='*' --flavor=woff2 --output-file=EBGaramond-Variable.woff2`
  (likewise for the italic). Redo this if a page needs a character outside
  those ranges.
- The homepage banner comes in two sizes: `banner-600.webp` for phones and
  `banner-lg-min.webp` above 576px. The homepage preloads both by media query.
- Files must stay under GitHub's 100 MB limit. Unused originals live outside
  the repo. `socrates.mp3` is made from the full-quality
  `../socrates-original.mp3` as 40 kbps mono (lower sounds muffled):
  `lame -m m -b 40 --resample 24 ../socrates-original.mp3 socrates.mp3`

## Deploys

Pushing to `main` publishes the site through GitHub Pages. `CNAME` sets the
custom domain. The other domains (anfa.ng, anfangderunendlichkeit.de) are
forwarded at their registrars, not here.

`6520b8fde17765146bba6267c605b63c.txt` at the root is the IndexNow key that
proves to Bing (and other IndexNow engines) that pings for this site come from
its owner. Keep it. To ask them to recrawl pages after a deploy, POST the URLs
to `https://api.indexnow.org/indexnow` with that key.
