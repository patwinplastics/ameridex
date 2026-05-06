# AmeriDex Dealer Routing & My Store Picker

A small, dependency-free system for steering visitors from `ameridex.com` to the
right authorized regional dealer. Designed to scale from one dealer to dozens
without code changes.

## How a visitor flows through the site

There are two states a visitor can be in: **suggested** (we think we know their
nearest dealer, but they have not picked) and **confirmed** (they explicitly set
a store). The two states look and behave differently.

### Suggested (no pick yet)

1. **Landing.** Homeowner Googles "AmeriDex" or sees a Facebook post from a
   dealer. They land on the site.
2. **Background ZIP detection.** `js/dealer-routing.js` calls `ipapi.co/json/`
   with a 2.5s timeout to read the visitor's `postal` (ZIP) code. The result is
   cached for 24h in `ameridex_zip_cache`. If the call fails, times out, or the
   visitor is non-US, we silently do nothing (no chip, no banner, page works
   normally).
3. **If the ZIP matches a dealer territory**, the header chip flips into a
   neutral "suggested" state (cream background, pin icon, dealer city) and a
   one-time first-visit banner appears across the top:
   _"Nearest dealer: Guy C Lee Building Supply (Mt. Pleasant, SC) [Set as my
   store] [×]"_.
4. **Forms are NOT stamped while suggested.** A suggestion is just a hint. The
   visitor still has to opt in.

### Confirmed (explicit pick)

A visitor enters confirmed state in any of three ways:

- They click **Set as My Store** on the suggestion banner or chip popover.
- They click **Set as My Store** on the Where to Buy page (after a ZIP search
  or from the dealer directory list).
- They click any AmeriDex link with `?dealer=<slug>` on it. This is the
  dealer-shared URL pattern (silent confirm, no banner shown).

Once confirmed:

- The header chip turns red ("Mt. Pleasant" with a red pin and caret) on every
  page.
- The first-visit banner reads _"Guy C Lee Building Supply is set as your
  store (Mt. Pleasant, SC) [Change] [×]"_.
- The "Get a Free Quote" CTA quietly relabels to "Quote from Mt. Pleasant".
- Every quote, contact, and samples form gets hidden fields stamped on it
  (see Form Routing below).
- The visitor can change or clear the store anytime from the chip popover.

## Files in this system

```
data/dealers.json                   # single source of truth
js/dealer-routing.js                # cookie, ZIP match, form stamp, banner, chip, IP geo
where-to-buy.html                   # ZIP lookup + full dealer directory + Set as My Store
dealers/<slug>.html                 # one co-branded page per dealer
css/site.css                        # appended .ad-dealer-* and .ad-store-chip-* styles
DEALERS_README.md                   # this file
```

Every existing page (`index.html`, `gallery.html`, etc.) loads
`js/dealer-routing.js` and includes a "Where to Buy" link in the nav, mobile
menu, and footer.

## Cookie schema

| Cookie / storage              | Lifetime  | Purpose                                                                |
|-------------------------------|-----------|------------------------------------------------------------------------|
| `ameridex_dealer`             | 90 days   | Confirmed dealer slug. Drives chip, banner, form stamping.             |
| `ameridex_dealer_dismissed`   | 24 hours  | Visitor said "Not now" to the suggestion. Suppresses banner & chip.    |
| `ameridex_zip_cache`          | 24 hours  | Cached IP-detected ZIP so we don't hit ipapi.co on every page load.    |
| `ameridex_banner_dismissed`   | session   | Visitor closed the banner this session. Chip stays visible.            |

After a 24h dismissal expires, we re-suggest. Clearing `ameridex_dealer` from
the chip popover puts the visitor back into the suggested-or-blank state.

## Header chip behavior

The chip lives in the page header, between the nav and the dealer-portal
button. Two visual states:

- **Suggested:** cream pill, pin icon, dealer city in muted text, small caret.
  Click opens a popover with **Set as my store** (primary), **Visit Where to
  Buy**, and **Not now** (24h dismiss).
- **Confirmed:** red pin, dealer city in dark bold text, caret. Click opens a
  popover with **Change store** (goes to Where to Buy) and **Clear store**.

### Responsive behavior (carefully tuned, do not regress)

Header is tight at desktop widths because we have 7 nav items + logo + chip +
dealer portal button. Breakpoints:

| Viewport       | Chip rendering                                          |
|----------------|---------------------------------------------------------|
| `< 1100px`     | Chip hidden. Picker only available via Where to Buy.    |
| `1100–1280px`  | Chip collapses to **icon only** (pin + caret).          |
| `1281–1399px`  | Chip shows pin + city, no eyebrow ("Nearest dealer:").  |
| `≥ 1400px`     | Full chip: eyebrow + dealer city + caret.               |

Container max-width is normally `1240px`; pages with the chip use `1380px` and
tighter right padding so the chip doesn't push nav items off-screen. The
chip is hidden on mobile (under 1100px); the banner handles the picker UI on
phones.

## Form routing (AmeriDex-only delivery)

When a dealer is **confirmed**, every Formspree form on the site gets these
hidden fields injected at runtime:

| Field name                | Value                                       |
|---------------------------|---------------------------------------------|
| `routed_to_dealer`        | dealer slug (e.g. `guy-c-lee-mt-pleasant`)  |
| `routed_to_dealer_name`   | Display name + location                     |
| `_subject`                | Prefixed with `[<slug>]`                    |

**Critical policy: AmeriDex sales is the only recipient.** We deliberately do
**not** stamp `_cc` and **do not** stamp `routed_to_dealer_email`. The dealer's
email lives in `data/dealers.json` for internal reference only and is never
rendered to the page or sent to Formspree. AmeriDex forwards leads to dealers
manually, on its own SLA.

The router includes defensive cleanup that strips any pre-existing `_cc` or
`routed_to_dealer_email` inputs from a form before submit. This protects
against template drift if someone copies an old form.

Suggestions never stamp forms. A suggestion is a hint, not a routing decision.

## Reporting

Because every submission carries `routed_to_dealer`, you can build a monthly
"dealer lead report" by filtering Formspree exports (or a downstream CRM) on
that field. Per dealer, you can show: visits to their landing page (UTM), quote
requests submitted with their slug, and sample requests.

## Adding a new dealer

It is a 3-step process. No code changes required.

### 1. Add the dealer to `data/dealers.json`

Copy the existing block, change the values. Slug must be URL-safe and unique.

```json
{
  "slug": "smith-lumber-asheville",
  "name": "Smith Lumber Co.",
  "location_label": "Asheville, NC",
  "url_external": "https://smithlumber.com/asheville",
  "logo": "",
  "address_line1": "123 Main St",
  "address_line2": "Asheville, NC 28801",
  "phone": "828-555-0100",
  "email": "sales@smithlumber.com",
  "contact_person": "Jane Smith, Manager",
  "hours": "Mon-Fri 7-5, Sat 8-12",
  "lat": 35.5951,
  "lng": -82.5515,
  "service_radius_miles": 60,
  "zip_prefixes": ["287", "288", "289"]
}
```

The `email` field is internal-only. It is never rendered or sent to Formspree.

**Important:** Territories are exclusive. Do not assign a ZIP prefix to two
dealers. The ZIP lookup returns the first match it finds.

### 2. Create a co-branded landing page

Copy `dealers/guy-c-lee-mt-pleasant.html` to `dealers/<new-slug>.html` and edit
exactly four things:

- `<title>` and `<meta name="description">`
- The `<meta name="ad-dealer-slug" content="...">` value
- The `<link rel="canonical">` URL
- The `og:url` meta tag

Everything else (dealer name, address, phone, hours, contact person, quote-form
routing) is pulled from `data/dealers.json` at runtime.

A direct visit to `dealers/<slug>.html` does **not** auto-set the cookie. The
visitor must click **Set as My Store**. Only `?dealer=<slug>` in the URL sets
the cookie silently (this is the pattern dealers use in their own marketing
links).

### 3. Hand the URL to the dealer

Give them:

```
https://ameridex.com/dealers/<new-slug>.html?dealer=<new-slug>&utm_source=<dealer>&utm_medium=referral
```

They put it in their email signature, on their location page, on Facebook,
behind a yard-sign QR code. The `?dealer=` parameter sets the cookie silently
so the visitor stays tagged even if they wander into the main site.

## Editing territories later

Open `data/dealers.json` and edit the `zip_prefixes` array. To exclude a
specific ZIP that falls inside a prefix, the easiest path is a 5-digit override
list (future enhancement, not built yet). Today, ZIP-prefix is the finest
granularity and covers 99% of cases.

## IP geolocation: tradeoffs

We use `ipapi.co/json/` (free tier, ~1,000 requests/day) for the suggested
state. Reasons:

- Returns `postal` (ZIP) directly. Most free services only give city/region.
- HTTPS, no API key needed for the free tier.
- Browser-side call, so we don't burn a server budget.

Fallback behavior is **always silent**. If the request times out (2.5s),
returns no `postal`, returns a non-US country, or errors, we render the page
exactly as if the visitor had no cookie and we never tried. The 24h
`ameridex_zip_cache` minimizes repeat calls. Confirmed picks never call ipapi
at all.

## Things deliberately not built (yet)

- **Map view.** A pin map is overkill for one or a handful of dealers and
  highlights coverage gaps. Add when you have ~10+ dealers.
- **Reciprocal link from dealer site.** We left the door open by including
  `url_external` on every dealer record.
- **5-digit ZIP overrides.** See above.
- **Spam honeypot (`_gotcha`).** Easy to add to all forms when needed.
