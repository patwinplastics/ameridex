# AmeriDex.com - Build Notes (v2)

This is the v2 rebuild that matches the live ameridex.com structure, copy, and
imagery. The site is pure static HTML/CSS/JS - no build step required to serve.
The `_build.py` helper is optional and regenerates all pages from shared partials.

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
- Update the Facebook URL in the footer (currently links to facebook.com root;
  search for `facebook.com` in `_build.py` to update).
