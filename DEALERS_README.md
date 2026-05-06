# AmeriDex Dealer Routing

A small, dependency-free system for steering visitors from `ameridex.com` to the
right authorized regional dealer. Designed to scale from one dealer to dozens
without code changes.

## How a visitor flows through the site

1. **Landing.** A homeowner Googles "AmeriDex" or sees a Facebook post from a
   dealer. They land on the site.
2. **Picking a dealer happens one of three ways:**
   - They click **Where to Buy** in the nav and enter their ZIP code.
   - They visit a **co-branded dealer landing page** like
     `/dealers/guy-c-lee-mt-pleasant.html` (the URL the dealer shares in their
     own marketing).
   - They click any AmeriDex link with `?dealer=<slug>` (UTM-style) on it.
3. **A cookie tags the session.** From that point on, every page shows a sticky
   banner ("Shopping with Guy C Lee Building Supply, Mt. Pleasant, SC") and the
   "Get a Free Quote" CTA quietly relabels to "Quote from Mt. Pleasant".
4. **Form submissions route to the dealer.** The quote, contact, and samples
   forms get hidden fields stamped on them: dealer slug, dealer name, dealer
   email. Formspree sends the message to AmeriDex sales (primary) and CCs the
   dealer's email so both teams see it. The subject line is prefixed with the
   dealer slug so the AmeriDex inbox is filterable.
5. **Visitor can change dealer** anytime via the "Change" button in the banner,
   which clears the cookie and bounces them back to Where to Buy.

## Files in this system

```
data/dealers.json                   # single source of truth
js/dealer-routing.js                # cookie, ZIP match, form stamp, banner
where-to-buy.html                   # ZIP lookup + full dealer directory
dealers/<slug>.html                 # one co-branded page per dealer
css/site.css                        # appended .ad-dealer-* styles
DEALERS_README.md                   # this file
```

Every existing page (`index.html`, `gallery.html`, etc.) loads
`js/dealer-routing.js` and includes a "Where to Buy" link in the nav, mobile
menu, and footer.

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
  "hours": "Mon–Fri 7–5, Sat 8–12",
  "lat": 35.5951,
  "lng": -82.5515,
  "service_radius_miles": 60,
  "zip_prefixes": ["287", "288", "289"]
}
```

**Important:** Territories are exclusive. Do not assign a ZIP prefix to two
dealers. The ZIP lookup returns the first match it finds.

### 2. Create a co-branded landing page

Copy `dealers/guy-c-lee-mt-pleasant.html` to `dealers/<new-slug>.html` and edit
exactly four things:

- `<title>` and `<meta name="description">`
- The `<meta name="ad-dealer-slug" content="...">` value
- The `<link rel="canonical">` URL
- The `og:url` meta tag

Everything else (the dealer name, address, phone, hours, contact person, the
quote-form routing) is pulled from `data/dealers.json` at runtime.

### 3. Hand the URL to the dealer

Give them:

```
https://ameridex.com/dealers/<new-slug>.html?utm_source=<dealer>&utm_medium=referral
```

They can put it in their email signature, on their location page, on Facebook,
behind a yard-sign QR code. Every visit sets the cookie, so even if the visitor
wanders into the main AmeriDex site to browse, they stay tagged to that dealer.

## How form routing works

When a dealer is active, every Formspree form on the site gets four hidden
fields injected at runtime:

| Field name                | Value                                       |
|---------------------------|---------------------------------------------|
| `routed_to_dealer`        | dealer slug (e.g. `guy-c-lee-mt-pleasant`)  |
| `routed_to_dealer_name`   | Display name + location                     |
| `routed_to_dealer_email`  | Dealer's email                              |
| `_subject`                | Prefixed with `[<slug>]`                    |
| `_cc`                     | Dealer's email (Formspree CC)               |

This means **the dealer always gets a copy** of every quote, contact, or sample
request from a visitor in their territory, while AmeriDex stays the primary
recipient and can step in if the dealer doesn't respond.

> If the dealer prefers to be the **primary** recipient instead of CC, we can
> swap the Formspree config. For now, AmeriDex sales is primary so we maintain
> visibility and a 24-hour SLA fallback.

## Reporting

Because every submission carries `routed_to_dealer`, you can build a monthly
"dealer lead report" by filtering Formspree exports (or a downstream CRM) on
that field. Per dealer, you can show: visits to their landing page (UTM), quote
requests submitted with their slug, and sample requests. That gives you both a
partner-strengthening metric and a sales tool when pitching the next dealer.

## Editing territories later

Open `data/dealers.json` and edit the `zip_prefixes` array. To exclude a
specific ZIP that falls inside a prefix, the easiest path is to add a 5-digit
override list (a future enhancement; not built yet). Today, ZIP-prefix is the
finest granularity and 99% of cases are fine at the 3-digit level.

## Things deliberately not built (yet)

- **Map view.** A pin map is overkill for one or a handful of dealers and
  highlights coverage gaps. Add when you have ~10+ dealers.
- **Geo-IP auto-suggest.** We could pre-detect the visitor's region and prompt
  them with "Looks like you're in Charleston — Guy C Lee Building Supply is
  your local dealer. Continue?" That's a nice touch but unnecessary v1.
- **Reciprocal link from dealer site.** We left the door open by including
  `url_external` on every dealer record. If Bryan wants to deep-link from
  guyclee.com back to the co-branded page, that link already exists.
