# AmeriDex.com

Static marketing site for the AmeriDex Dryspace System (made by A & M Building Products, Brick, NJ).

Plain HTML + Tailwind (CDN) + a small custom CSS file + vanilla JS. No build step required to view.

## Local development

Just open `index.html` in a browser, or serve the folder:

```bash
cd ameridex
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploy via GitHub Pages

This repo ships with `.github/workflows/pages.yml` which deploys the repo root on every push to `main` using the official `actions/deploy-pages@v4` workflow.

1. Push to GitHub (`patwinplastics/ameridex`).
2. In the repo settings, under **Pages**, set the source to **GitHub Actions**.
3. The custom domain is configured via the `CNAME` file (`ameridex.com`). Point your DNS A/AAAA records (or `CNAME` for `www`) at GitHub Pages.
4. The `.nojekyll` file ensures GitHub serves files like `_partials.py` are ignored only if you exclude them. They are safe to leave but do nothing on the static site.

## Where to drop real content

| What                      | Where                                                |
| ------------------------- | ---------------------------------------------------- |
| Hero photo                | `/assets/img/hero.jpg` and update `index.html`       |
| Open Graph share image    | `/assets/img/og.jpg`                                 |
| Project photos            | `/assets/img/gallery/` and update `gallery.html`     |
| Spec sheets, warranty PDFs| `/pdfs/` and update `href="#"` in `resources.html` and `colors.html` |
| Real testimonials         | `index.html` (search for `TODO: Replace placeholder testimonial`) |

## Form endpoint

Both `quote.html` and `contact.html` use Formspree as the placeholder submission target. Replace `REPLACE_WITH_YOUR_ENDPOINT` in both files with your actual Formspree (or other) form endpoint.

```html
<form action="https://formspree.io/f/xreljrrd" method="POST">
```

## Site map

- `/index.html` - Home
- `/how-it-works.html` - How It Works
- `/colors.html` - Colors & Pricing
- `/gallery.html` - Project Gallery
- `/resources.html` - Installation Resources
- `/dealers.html` - Find a Dealer
- `/quote.html` - Get a Free Quote (also `?type=dealer` for the dealer flow)
- `/contact.html` - Contact

## Editing the build helpers

The `_build.py` and `_partials.py` files are optional Python helpers used to regenerate the HTML. They are NOT required for the site to run. You can edit the HTML files directly. If you prefer to use the helpers, run `python3 _build.py` from the project root.
