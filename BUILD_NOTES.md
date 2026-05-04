# AmeriDex.com - Build Notes

## Pages built (8)

1. `index.html` - Home (hero, trust strip, why AmeriDex, how-it-works snippet, color preview, gallery preview, split CTA, testimonial)
2. `how-it-works.html` - How It Works (anatomy diagram, "new construction only" feature callout, spec/warranty table)
3. `colors.html` - Colors & Pricing (3 solids at $10/ft, 4 variegated at $9.50/ft, downloads block)
4. `gallery.html` - 9-card masonry gallery
5. `resources.html` - Installation/Specs/Warranty PDF cards + 3 video tiles + sales CTA
6. `dealers.html` - Search bar, map placeholder, 8 sample dealer cards rendered from inline JS, "Become a Dealer" band, dealer portal box
7. `quote.html` - 2-column form + "What happens next" sidebar; reads `?type=dealer` and prefills + swaps H1
8. `contact.html` - 3 info cards + simpler contact form + map placeholder

## Where to drop real content

- **Hero photo:** `/assets/img/hero.jpg`. Replace the CSS-composed `.hero-art` block in `index.html` with `<img src="/assets/img/hero.jpg" alt="..." />`. Look for the `<!-- TODO: Replace this CSS-composed scene ... -->` comment.
- **Open Graph image:** `/assets/img/og.jpg` (1200x630). Already referenced by every page in `<meta property="og:image">`.
- **Gallery photos:** `/assets/img/gallery/`. Then update the `<div class="gallery-img ...">` placeholders in `gallery.html` and the homepage gallery preview to `<img src="..." alt="...">`. Comment in place: `<!-- TODO: Replace placeholder gradients with real project photos. -->`
- **Testimonials:** `index.html`, look for `<!-- TODO: Replace placeholder testimonial ... -->`.
- **PDFs:** drop into `/pdfs/`. Then replace `href="#"` placeholders on `resources.html` and the Downloads section of `colors.html`.

## Where to set the Formspree endpoint

Both `quote.html` and `contact.html` have:

```html
<form action="https://formspree.io/f/REPLACE_WITH_YOUR_ENDPOINT" method="POST">
```

Replace `REPLACE_WITH_YOUR_ENDPOINT` with your real endpoint in both files. Search both files for the literal string `REPLACE_WITH_YOUR_ENDPOINT`.

## Known TODOs / Future work

- Wire dealer search form on `/dealers.html` to a real locator API; current submit shows an alert.
- Replace dealer list with real production data (currently hard-coded sample list of 8 NJ/PA/NY yards in inline `<script>` at the bottom of `dealers.html`).
- Replace map placeholders on `/dealers.html` and `/contact.html` with embedded Mapbox / Google Maps.
- Replace the homepage hero CSS scene with a real photo once available.
- Replace placeholder gallery gradient blocks with real project photography.
- Replace placeholder testimonial on the homepage with a real customer quote (and optionally a headshot).
- Drop final spec/warranty/installation PDFs into `/pdfs/` and link them from `resources.html` and `colors.html`.

## Tech notes

- Static-only. No backend. No build step required to serve.
- `_build.py` and `_partials.py` are optional helpers used to regenerate the HTML files from a single source of truth (header, footer, head). They are not required to view the site. Edit the generated HTML directly OR rerun `python3 _build.py`.
- Tailwind via CDN + `/css/site.css` for design tokens and component styles.
- Google Fonts: Archivo (display) + Inter (body).
- Logo is inline SVG (header + footer); favicon SVG at `/assets/img/favicon.svg`.
- Reveal-on-scroll animations via IntersectionObserver in `/js/site.js`.
- Quote page reads `?type=dealer` and pre-selects the "Dealer prospect" role and swaps the H1.
- All copy avoids the em-dash character (`—`) per brand voice rules. Verified via grep.
- All copy uses "wood-alternative" instead of "composite".
- `CNAME` set to `ameridex.com`; `.nojekyll` in place so Pages serves files raw.
- GitHub Pages deploy workflow at `.github/workflows/pages.yml`.
