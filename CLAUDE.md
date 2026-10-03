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
- Each page sets its own `<title>` ("… · Der Anfang der Unendlichkeit"), the
  matching `twitter:title`/`og:title`, `og:url` and a canonical link. New pages
  need all of these and an entry in `sitemap.xml`.
- `pages/`, `xmas.html` and `rezensionen.html` are meta-refresh redirects from
  URLs the old site used. Keep them so old links and search results keep
  working.
- Glossary anchor ids are the entry titles transliterated and dasherized the
  way Rails' `parameterize` did it (`Mittelmäßigkeitsprinzip` →
  `mittelmassigkeitsprinzip`), so existing `#…` links keep working.
- Errata are listed in page order.

## Assets

- Bootstrap 4.6 CSS is vendored; no JavaScript library is loaded.
- Fonts (EB Garamond, Pathway Gothic One) are self-hosted in `fonts/` under the
  SIL Open Font License, so the site loads nothing from font services. Keep it
  that way: any new third-party request needs a section in the privacy policy
  (`datenschutzerklaerung.html`).
- Files must stay under GitHub's 100 MB limit. Unused originals (such as the
  full-quality Socrates audio) live outside the repo in
  `../assets/`.

## Deploys

Pushing to `main` publishes the site through GitHub Pages. `CNAME` sets the
custom domain. The other domains (anfa.ng, anfangderunendlichkeit.de) are
forwarded at their registrars, not here.
