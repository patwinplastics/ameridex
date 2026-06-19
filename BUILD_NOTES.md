# AmeriDex.com - Build Notes (v2)

This is the v2 rebuild that matches the live ameridex.com structure, copy, and
imagery. The site is pure static HTML/CSS/JS - no build step required to serve.
The `_build.py` helper is optional and regenerates all pages from shared partials.

> WARNING: `_build.py` has drifted behind the production HTML.
>
> The live `index.html` (and several others) carry phase-1 neuro-conversion
> additions that were applied directly to the HTML and never back-ported into
> the build script:
>   - hero copy rewrite ("Build the deck. Keep the space underneath.")
>   - felt-loss section ("This is happening above your head right now")
>   - testimonial slot, reciprocity grid, scarcity band, why-bullets row with
>     the CAD-rendered dexerdry-cross-section icon
>   - quote-reassure aside on `get-a-free-quote.html`
>   - first-person hero CTAs on index ("Get my free quote", "Ship my free samples")
>   - persistent trust topbar inserted above the header on every page
>   - sitewide CTA verb sweep ("Start my project" / "Request samples")
>
> Running `python3 _build.py` today will overwrite all of these. Before any
> future build run, port the page-specific additions into the relevant
> `page_*` functions in `_build.py`. The build script already contains the
> trust topbar partial (`trust_topbar()`) and the renamed header/mobile CTA
> labels, so those WILL be preserved on a rebuild.

## Blog (added 2026-05-29, hand-built, NOT in _build.py)

The blog is a static hub. `_build.py` does NOT know about it, so a future
build run will not touch or regenerate these files, but it also will not
recreate them if deleted. To add a new post:

1. Copy any file in `blog/` as the template (it carries the full site chrome:
   trust topbar, header, mobile menu, footer, JSON-LD).
2. From inside `blog/`, all shared links use a `../` prefix
   (`../css/site.css`, `../index.html`, `../blog.html`, etc.).
3. Swap the `<title>`, meta description/keywords, OG/Twitter tags, the
   `BlogPosting` + `BreadcrumbList` JSON-LD, the hero kicker/H1/lead, the
   article body, and the CTA heading.
4. Add a card for it in `blog.html` (the post list `grid-3`) and add a
   `<loc>` entry in `sitemap.xml`.
5. Brand rules still apply: no em-dash, relative links only.

Blog files:
- `blog.html` (index/landing)
- `blog/under-deck-living-space-ideas.html`
- `blog/why-decks-rot-from-the-top-down.html`
- `blog/planning-a-new-deck-checklist.html`
- `blog/cellular-pvc-vs-composite-decking.html`
- `blog/choosing-the-right-ameridex-color.html`
- `blog/nj-shore-deck-guide.html` (added 2026-06-19)

A "Blog" link was added to the primary nav, mobile menu, and footer sitemap
on every root page directly in the HTML (not via _build.py).

### Blog engagement components (added 2026-05-29)

Reusable styling lives in `css/blog-engage.css`; interactive checklist logic
in `js/blog-checklist.js`. Link both in any post `<head>` after `site.css` /
`site.js`. All components are scoped and built to beat the Tailwind CDN
preflight, so reuse the exact class names. Available pieces:

- Numbered step cards: `.blog-steps` wrapper with `.blog-step` cards, each a
  `.blog-step-num` badge, an `h3.blog-step-head`, and a `.blog-step-body`.
  Add `.idea` to a step for an image-friendly card with no checkbox.
- Interactive checklist: put `data-checklist="<id>"` on `.blog-steps`, give
  each card a `<label class="blog-step-check"><input type="checkbox"
  data-step="N"> Mark as decided</label>`, and add a sticky progress bar with
  `data-checklist-bar="<id>"` containing `.blog-progress-fill`,
  `[data-checklist-count]`, and a `[data-checklist-reset="<id>"]` button.
  Progress persists in localStorage per page. Bar sticks at `top:69px`
  (just under the ~70px sticky site header).
- Callout boxes: `.blog-callout` with modifier `.key` (navy/gold),
  `.tip` (green), or `.warn` (red). Inner `.blog-callout-icon` (inline SVG)
  + `.blog-callout-body` with a `.blog-callout-title` label.
- Pull-quote: `.blog-pullquote` with a single `<p>` inside.
- Do/Don't grid: `.blog-dodont` with two `.blog-dodont-col` columns,
  `.do` (green) and `.dont` (red), each an `h4` + `ul`.

If a post is an ordered checklist, also add an `ItemList` JSON-LD block (see
`planning-a-new-deck-checklist.html`) for SEO.

## Pages built (7)

1. `index.html` - Home (hero with real photo, deck colors grid, trust strip,
   why-system-works, lifestyle 3-up, footer CTA)
2. `how-system-works.html` - The two-part system, 3-step process, "new
   construction only" callout, specs at a glance, CTA band
3. `gallery.html` - Dryspace showcase (carousel desktop / stack mobile),
   "Talk to a Specialist" CTA
4. `get-a-free-quote.html` - Quote form (project basics + site details +
   contact). Reads `?type=dealer` and swaps copy / hides deck-size fields.
5. `contact-us.html` - Contact form (50-state select) + "or reach us directly"
   band (Sales / Address / Dealer Portal)
6. `samples-request.html` - Free deck sample request: size radio cards,
   color toggle grid with counter + "Select All" pill, contact + address
7. `warranty-registration.html` - 25-Year Residential / 10-Year Commercial
   warranty registration form with proof of purchase upload + acknowledgment

## Where to drop the OG image

Drop a real 1200x630 PNG/JPG at `assets/img/og.jpg`. Every page already
references it via `<meta property="og:image">`.

## Where to set the Formspree endpoint

Every form page contains:

```html
<form action="https://formspree.io/f/xreljrrd" method="POST">
```

Search-and-replace `REPLACE_WITH_YOUR_ENDPOINT` across:
- `get-a-free-quote.html`
- `contact-us.html`
- `samples-request.html`
- `warranty-registration.html`

## Where to add real PDFs

Drop final PDFs into `pdfs/`:
- `pdfs/ameridex-installation.pdf` - linked from the hero on `index.html`
  ("Download Installation Instructions (PDF)")

The home page hero link to that PDF will start working as soon as the file
exists at the path. No HTML changes needed.

## Where to add more gallery photos

Drop more `.png`/`.jpg` files into `assets/img/gallery/`, then add another
`<figure class="gallery-photo">` block in `gallery.html` for each one. There
is a TODO comment in `gallery.html` directly above the carousel.

## Dealer portal (separate codebase)

The Dealer Portal is a separate codebase (not in this repo). Every page on
this site links out to `https://dealerportal.ameridex.com` from:

1. The floating bottom-right pill ("AmeriDex Dealer Portal", on every page,
   hidden under 480px width)
2. The footer column 4 pill button
3. The mobile menu CTA

Update the URL in `_build.py` (constant `DEALER_PORTAL_URL`) and rerun
`python3 _build.py` to propagate, OR search-and-replace
`https://dealerportal.ameridex.com` across all 7 HTML files.

## Brand voice / content rules

- No em-dash character (`-` hyphen with spaces, comma, or period instead)
- No public pricing. All pricing flows through the quote form or the dealer
  portal. The swatch grid uses Solid / Variegated badges only.
- Product is described as: cellular PVC deck boards with a proprietary ASA
  cap PLUS Dexerdry, the integrated water-diverting seal made of
  automotive-grade TPE. Marketing copy can use "premium PVC decking" or
  "wood-alternative PVC decking". Never just "composite".
- AmeriDex installs on new construction only. Frame this as a feature.
- Warranty: 25-Year Residential / 10-Year Limited Commercial.

## Tech notes

- Static-only. No backend. No build step required to serve.
- `_build.py` is the optional source-of-truth generator. All HTML files can
  be edited directly OR regenerated via `python3 _build.py`.
- Tailwind CDN is a progressive enhancement only - all critical styling
  lives in `css/site.css` so the site looks right even if the CDN is blocked.
- All internal links are RELATIVE (e.g. `gallery.html`, never `/gallery.html`).
  This was a previously-shipped bug; do not regress.
- Google Fonts: Archivo (display) + Inter (body).
- Logo: `assets/img/logo.png` in header + footer; SVG favicon at
  `assets/img/favicon.svg`.
- Reveal-on-scroll via IntersectionObserver in `js/site.js`.
- Quote page reads `?type=dealer` (in `js/site.js`) and swaps the H1 +
  hides the deck-size fields + reveals a "Tell us about your business"
  textarea.
- Samples page color toggles + size radios are wired up in `js/site.js`.
- `CNAME` set to `ameridex.com`; `.nojekyll` in place.
- GitHub Pages deploy workflow at `.github/workflows/pages.yml`.

## Known TODOs

- Drop a real OG image at `assets/img/og.jpg`.
- Drop the final installation PDF at `pdfs/ameridex-installation.pdf`.
- Wire up Formspree endpoint (4 forms, see above).
- Confirm the exact deck board lengths offered (currently shown as 12 / 16 /
  20 ft on `how-system-works.html`; there is a TODO comment in that file).
