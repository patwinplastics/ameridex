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
4. **Form submissions go to AmeriDex only.** All quote, contact, and sample
   requests are sent to AmeriDex. AmeriDex manually forwards each lead to the
   matched dealer. The forms get hidden fields stamped with the dealer slug and
   name, plus a subject prefix (`[<slug>] ...`), so the AmeriDex inbox is
   filterable per dealer and you always know which dealer to forward to. The
   dealer is **not** CC'd — this keeps quality control with AmeriDex.
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
  "email": "sales@smithlumber.com",   // INTERNAL ONLY — never shown on the site; used by AmeriDex to forward leads
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

**Policy: every form submission goes to AmeriDex only.** AmeriDex manually
forwards each lead to the matched dealer. The dealer is never CC'd or copied
on the raw inbound message.

When a dealer is active, every Formspree form on the site gets these hidden
fields stamped on it at runtime:

| Field name              | Value                                          |
|-------------------------|------------------------------------------------|
| `routed_to_dealer`      | dealer slug (e.g. `guy-c-lee-mt-pleasant`)     |
| `routed_to_dealer_name` | Display name + location                        |
| `_subject`              | Prefixed with `[<slug>]` for inbox filtering   |

The dealer's `email` in `dealers.json` is **internal-only**. It exists so the
AmeriDex team knows where to forward each lead. It is never rendered on a
public page and never used as a Formspree recipient.

What the visitor sees on dealer cards and the co-branded landing page:

- Dealer name, location, address
- **Phone number** (click-to-call)
- Contact person (manager/salesperson)
- Hours
- **Visit Dealer Site** link (when `url_external` is set)

So if the visitor wants to bypass the form and contact the dealer directly,
they can call them or visit their website — those channels are intentionally
left open. The form, however, always lands in the AmeriDex inbox first.

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
