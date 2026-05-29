#!/usr/bin/env python3
"""
AmeriDex.com - page build script.

Emits all 7 HTML pages from shared head/header/footer partials so
the navigation, head meta, and footer stay in lockstep.

Usage:  python3 _build.py
"""
import os, pathlib, textwrap

ROOT = pathlib.Path(__file__).resolve().parent

# ----------------------------------------------------------------------
# SHARED PARTIALS
# ----------------------------------------------------------------------

NAV_LINKS = [
    ("Home",                 "index.html"),
    ("How System Works",     "how-system-works.html"),
    ("Instructional Videos", "https://www.youtube.com/channel/UC3Fz0TEKbLpQZefnYQNCxmg"),
    ("Gallery",              "gallery.html"),
    ("Blog",                 "blog.html"),
    ("About",                "about.html"),
    ("Where to Buy",         "where-to-buy.html"),
    ("Get a Free Quote",     "get-a-free-quote.html"),
    ("Contact Us",           "contact-us.html"),
]

DEALER_PORTAL_URL = "https://dealerportal.ameridex.com"

# Canonical site origin used for absolute URLs in OG tags, canonical links,
# JSON-LD, and the sitemap. Update if the production domain ever changes.
SITE_ORIGIN = "https://www.ameridex.com"
SITE_NAME = "AmeriDex"
LEGAL_NAME = "A & M Building Products"
DEFAULT_DESCRIPTION = (
    "AmeriDex is the integrated above-joist deck drainage system. "
    "PVC deck boards lock onto a Dexerdry seal at install, sending rain off the deck "
    "and creating a dry, finished under-deck living space. Made in the USA."
)
# Default Organization-level JSON-LD that ships on every page so search
# engines build a knowledge-graph entity for the brand.
# Person schemas for the founders. Linked into the Organization via 'founder'.
FOUNDER_ARDOLINA = {
    "@context": "https://schema.org",
    "@type": "Person",
    "@id": f"{SITE_ORIGIN}/#founder-ardolina",
    "name": "John Ardolina",
    "jobTitle": "Co-Founder",
    "hasOccupation": [
        {"@type": "Occupation", "name": "Carpenter"},
        {"@type": "Occupation", "name": "Founder, Dexerdry, Inc."},
    ],
    "description": (
        "Co-founder of AmeriDex and founder of Dexerdry, Inc. A carpenter by "
        "trade who developed the patented above-joist water-diverting seal at "
        "the heart of the AmeriDex deck system."
    ),
    "knowsAbout": [
        "above-joist deck drainage",
        "water-diverting deck seals",
        "thermoplastic elastomer (TPE) gaskets",
        "deck waterproofing engineering",
        "deck construction",
        "carpentry",
    ],
    "worksFor": {"@id": f"{SITE_ORIGIN}/#organization"},
}

FOUNDER_MURPHY = {
    "@context": "https://schema.org",
    "@type": "Person",
    "@id": f"{SITE_ORIGIN}/#founder-murphy",
    "name": "Jim Murphy",
    "jobTitle": "Co-Founder",
    "description": (
        "Co-founder of AmeriDex with deep manufacturing experience in cellular PVC "
        "and building products production. Leads the manufacturing side of the "
        "business, including the AmeriDex plant in Linden, New Jersey."
    ),
    "knowsAbout": [
        "cellular PVC manufacturing",
        "building products production",
        "deck board extrusion",
        "plant operations",
    ],
    "worksFor": {"@id": f"{SITE_ORIGIN}/#organization"},
}

ORG_JSONLD = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": f"{SITE_ORIGIN}/#organization",
    "name": "AmeriDex",
    "alternateName": [
        "Ameri Dex",
        "AmeriDex Dryspace",
        "AmeriDex Decking System",
        "AmeriDex Deck Drainage",
    ],
    "legalName": LEGAL_NAME,
    "url": SITE_ORIGIN,
    "logo": f"{SITE_ORIGIN}/assets/img/logo.png",
    "image": f"{SITE_ORIGIN}/assets/img/og.jpg",
    "description": DEFAULT_DESCRIPTION,
    "foundingDate": "2023",
    "founder": [
        {"@id": f"{SITE_ORIGIN}/#founder-ardolina"},
        {"@id": f"{SITE_ORIGIN}/#founder-murphy"},
    ],
    "telephone": "+1-800-217-9206",
    "email": "sales@ameridex.com",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "1129A Industrial Parkway",
        "addressLocality": "Brick",
        "addressRegion": "NJ",
        "postalCode": "08724",
        "addressCountry": "US",
    },
    "sameAs": [
        "https://www.facebook.com/ameridexdryspace/",
        "https://www.youtube.com/channel/UC3Fz0TEKbLpQZefnYQNCxmg",
    ],
    "knowsAbout": [
        "above-joist deck drainage",
        "under deck drainage system",
        "cellular PVC decking",
        "integrated water-diverting deck seal",
        "new deck construction",
        "dry under-deck living space",
    ],
    "areaServed": "US",
    "slogan": "Protect The Space Under Your Deck.",
}


def _jsonld(obj):
    """Serialize a Python dict (or list of dicts) as a <script type=application/ld+json> tag.
    Uses minimal escaping; we control the input so this is safe."""
    import json
    return f'<script type="application/ld+json">{json.dumps(obj, separators=(",", ":"), ensure_ascii=False)}</script>'


def breadcrumb_schema(*pairs):
    """Build a BreadcrumbList JSON-LD schema from (name, path) pairs.
    Use '' as path for the homepage.
    Example: breadcrumb_schema(('Home',''), ('Gallery','gallery.html'))
    """
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": f"{SITE_ORIGIN}/{path}".rstrip("/") if path else f"{SITE_ORIGIN}/",
            }
            for i, (name, path) in enumerate(pairs)
        ],
    }


# Product schema for the AmeriDex Dryspace System (used on homepage and how-it-works)
PRODUCT_JSONLD = {
    "@context": "https://schema.org",
    "@type": "Product",
    "@id": f"{SITE_ORIGIN}/#product",
    "name": "AmeriDex Dryspace System",
    "alternateName": ["AmeriDex PVC Decking", "AmeriDex Above-Joist Drainage"],
    "description": (
        "Integrated above-joist deck drainage system combining cellular PVC deck boards "
        "with the Dexerdry automotive-grade TPE seal. Creates a dry, finished living "
        "space under the deck. Made in the USA for new deck construction."
    ),
    "brand": {"@type": "Brand", "name": "AmeriDex"},
    "manufacturer": {"@id": f"{SITE_ORIGIN}/#organization"},
    "category": "Decking / Under-Deck Drainage",
    "countryOfOrigin": "US",
    "image": [
        f"{SITE_ORIGIN}/assets/img/og.jpg",
        f"{SITE_ORIGIN}/assets/img/system-anatomy.jpg",
        f"{SITE_ORIGIN}/assets/img/hero.jpg",
    ],
    "material": "Cellular PVC with proprietary ASA cap; TPE seal",
    "audience": {"@type": "Audience", "audienceType": "Builders, contractors, dealers, homeowners building new decks"},
    "offers": {
        "@type": "AggregateOffer",
        "availability": "https://schema.org/InStock",
        "priceCurrency": "USD",
        "offerCount": 7,
        "priceSpecification": {
            "@type": "PriceSpecification",
            "priceCurrency": "USD",
            "description": "Pricing varies by deck size, color, and accessories. Request a free quote.",
        },
        "seller": {"@id": f"{SITE_ORIGIN}/#organization"},
        "url": f"{SITE_ORIGIN}/get-a-free-quote.html",
    },
    "hasMerchantReturnPolicy": {
        "@type": "MerchantReturnPolicy",
        "applicableCountry": "US",
        "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
        "merchantReturnDays": 30,
        "returnMethod": "https://schema.org/ReturnByMail",
        "returnFees": "https://schema.org/ReturnShippingFees",
    },
}

# FAQ content used both as JSON-LD and rendered as a real DOM section on how-it-works.
HOW_IT_WORKS_FAQ = [
    (
        "What makes AmeriDex different from other under-deck drainage systems?",
        "AmeriDex is an above-joist, integrated system. The waterproofing happens at the "
        "deck surface itself, not in a tray hung underneath the framing. Competing retrofit "
        "drainage systems are added below an existing deck as a tray or panel hung from the "
        "joists. AmeriDex is engineered into a new deck from the joists up, which is why "
        "your joists, beams, and ledger stay dry for the life of the structure.",
    ),
    (
        "Can AmeriDex be installed on an existing deck?",
        "No. AmeriDex is engineered for new deck construction only. The Dexerdry TPE seal "
        "locks between every board as the deck is installed, so it has to be built into the "
        "project from the start. Trying to retrofit it onto an existing deck would require "
        "removing all of the existing deck boards.",
    ),
    (
        "What is the Dexerdry seal and what is it made of?",
        "Dexerdry is the integrated drainage seal that ships between every AmeriDex deck "
        "board. It is made from automotive-grade TPE (thermoplastic elastomer), the same "
        "material category used in car door and window seals. It is engineered to flex "
        "through years of thermal cycling without cracking or losing its watertight fit.",
    ),
    (
        "What are AmeriDex deck boards made of?",
        "AmeriDex boards are premium cellular PVC with a proprietary ASA cap. They will not "
        "rot, splinter, or warp, and they carry an authentic wood grain finish. They are "
        "made in the USA.",
    ),
    (
        "What joist spacing does AmeriDex require?",
        "AmeriDex installs on a conventional 16 inches on-center joist layout for residential "
        "applications. No special substructure, sleepers, or sub-framing is required.",
    ),
    (
        "What lengths and colors are available?",
        "AmeriDex deck boards are available in 12, 16, and 20 foot lengths and in seven PVC "
        "colors. You can request free samples to see all seven colors in person.",
    ),
    (
        "What is the AmeriDex warranty?",
        "AmeriDex carries a 25-year residential limited warranty and a 10-year limited "
        "commercial warranty on the deck board system.",
    ),
    (
        "What is the fire rating of AmeriDex deck boards?",
        "AmeriDex cellular PVC deck boards carry a Class A flame spread rating under "
        "ASTM E84, the highest flame spread classification for building materials. That "
        "makes the boards a strong fit for projects in wildfire-prone regions and for "
        "jurisdictions that require Class A surface burning performance on the walking "
        "surface.",
    ),
]

FAQ_JSONLD = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in HOW_IT_WORKS_FAQ
    ],
}

# LocalBusiness schema for the contact page (NAP signal for local SEO).
LOCAL_BUSINESS_JSONLD = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": f"{SITE_ORIGIN}/#localbusiness",
    "name": "AmeriDex (A & M Building Products)",
    "image": f"{SITE_ORIGIN}/assets/img/og.jpg",
    "url": SITE_ORIGIN,
    "telephone": "+1-800-217-9206",
    "email": "sales@ameridex.com",
    "priceRange": "$$",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "1129A Industrial Parkway",
        "addressLocality": "Brick",
        "addressRegion": "NJ",
        "postalCode": "08724",
        "addressCountry": "US",
    },
    "geo": {
        "@type": "GeoCoordinates",
        "latitude": 40.083404,
        "longitude": -74.113823,
    },
    "openingHoursSpecification": [
        {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "08:00",
            "closes": "17:00",
        }
    ],
    "areaServed": {"@type": "Country", "name": "United States"},
}


def head(title, description=DEFAULT_DESCRIPTION, *, canonical="", keywords="",
         og_image="assets/img/og.jpg", og_type="website", extra_jsonld=None,
         extra_head=""):
    """Render the shared <head> for a page with full SEO metadata.

    Args:
        title:        Page <title>. Should be unique per page, ~50-60 chars.
        description:  Meta description. Should be unique per page, ~140-160 chars.
        canonical:    Path of the page relative to SITE_ORIGIN, e.g. 'gallery.html'
                      or '' for the homepage. Used for canonical link, og:url,
                      and absolute URL resolution.
        keywords:     Optional comma-separated keywords (low SEO weight today,
                      but still parsed by Bing and some directories).
        og_image:     Page-relative path to the social-share image. Defaults
                      to the brand OG image.
        og_type:      Open Graph type ("website" by default; "article" for posts).
        extra_jsonld: Optional dict OR list of dicts of additional JSON-LD
                      structured data to inject (FAQPage, Product, BreadcrumbList,
                      etc). The Organization schema always ships.
    """
    canonical_url = f"{SITE_ORIGIN}/{canonical}".rstrip("/") if canonical else f"{SITE_ORIGIN}/"
    og_image_abs = og_image if og_image.startswith("http") else f"{SITE_ORIGIN}/{og_image}"
    keywords_meta = f'\n  <meta name="keywords" content="{keywords}">' if keywords else ""

    # Always include the Organization schema; append page-specific schemas after it.
    schemas = [ORG_JSONLD]
    if extra_jsonld:
        if isinstance(extra_jsonld, list):
            schemas.extend(extra_jsonld)
        else:
            schemas.append(extra_jsonld)
    jsonld_block = "\n  ".join(_jsonld(s) for s in schemas)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{description}">{keywords_meta}
  <meta name="author" content="{LEGAL_NAME}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <meta name="theme-color" content="#0A2A4E">
  <meta name="format-detection" content="telephone=yes">
  <link rel="canonical" href="{canonical_url}">

  <!-- Open Graph (Facebook, LinkedIn, iMessage, Slack) -->
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:image" content="{og_image_abs}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{title}">
  <meta property="og:locale" content="en_US">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{og_image_abs}">
  <meta name="twitter:image:alt" content="{title}">

  <!-- Favicons / app icons -->
  <link rel="icon" type="image/svg+xml" href="assets/img/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicon-32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="assets/img/favicon-16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="assets/img/apple-touch-icon.png">
  <link rel="manifest" href="site.webmanifest">

  <!-- Performance: preconnect to font origins, preload the hero image on the homepage -->{extra_head}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="dns-prefetch" href="https://cdn.tailwindcss.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800;900&family=Inter:wght@400;500;600;700&display=swap">
  <link rel="stylesheet" href="css/site.css">

  <!-- Tailwind CDN is a progressive enhancement only - all critical styling is in site.css -->
  <script src="https://cdn.tailwindcss.com" defer></script>

  <script defer src="js/site.js"></script>

  <!-- Dealer routing: My Store chip, suggestion banner, IP-based suggestion, form stamping. -->
  <!-- Loaded on every page so the chip and confirmed-state CTAs follow the visitor sitewide. -->
  <script defer src="js/dealer-routing.js"></script>

  <!-- Structured data (schema.org / JSON-LD) -->
  {jsonld_block}
</head>
<body>
'''


def trust_topbar():
    """Slim persistent trust strip that sits above the sticky header on every
    page. Two reassurance items so the bar stays scannable in one glance:
      (1) the warranty terms (concrete, not vague)
      (2) the no-cost commitment level (kills the 'is this going to cost me
          just to ask' objection before the visitor reaches the hero CTA)
    Reads as a single line on desktop; collapses to two stacked lines below
    540px and hides entirely below 380px to leave room for the hamburger.
    """
    return '''
<div class="trust-topbar" role="note" aria-label="AmeriDex trust signals">
  <div class="container trust-topbar-inner">
    <span class="trust-topbar-item">
      <svg class="trust-topbar-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2 4 5v6c0 5 3.5 9.5 8 11 4.5-1.5 8-6 8-11V5l-8-3z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="m8.5 12 2.5 2.5L16 9" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
      25-yr residential <span class="trust-topbar-thin">/</span> 10-yr commercial warranty
    </span>
    <span class="trust-topbar-sep" aria-hidden="true">·</span>
    <span class="trust-topbar-item">
      <svg class="trust-topbar-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      Free quote <span class="trust-topbar-thin">+</span> free samples
    </span>
  </div>
</div>
'''


def header(active_path):
    """Sticky navy header with full nav + utilities + mobile menu."""
    nav_items = []
    for label, href in NAV_LINKS:
        is_external = href.startswith("http")
        is_active = (href == active_path)
        target = ' target="_blank" rel="noopener"' if is_external else ''
        cls = ' class="active"' if is_active else ''
        nav_items.append(f'    <a href="{href}"{target}{cls}>{label}</a>')

    mobile_items = []
    for label, href in NAV_LINKS:
        is_external = href.startswith("http")
        target = ' target="_blank" rel="noopener"' if is_external else ''
        mobile_items.append(f'      <a href="{href}"{target}>{label}</a>')

    nav_html = "\n".join(nav_items)
    mobile_html = "\n".join(mobile_items)

    topbar = trust_topbar()

    return f'''{topbar}
<header class="site-header">
  <div class="container site-header-inner">
    <a href="index.html" aria-label="AmeriDex home" class="block">
      <img class="header-logo-img" src="assets/img/logo.png" alt="AmeriDex">
    </a>

    <nav class="site-nav" aria-label="Primary">
{nav_html}
    </nav>

    <div class="site-header-cta">
      <a href="samples-request.html" class="outline-link" style="color:#fff;font-family:var(--font-display);font-weight:700;font-size:0.78rem;letter-spacing:0.08em;text-transform:uppercase;border:1.5px solid rgba(255,255,255,0.4);border-radius:999px;padding:0.5rem 0.85rem;">Request samples</a>
      <a href="get-a-free-quote.html" style="background:var(--red);color:#fff;font-family:var(--font-display);font-weight:700;font-size:0.78rem;letter-spacing:0.08em;text-transform:uppercase;border-radius:999px;padding:0.55rem 1rem;">Start my project</a>
    </div>

    <button class="hamburger" aria-label="Open menu" aria-controls="mobile-menu">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
</header>

<div class="mobile-menu" id="mobile-menu" aria-hidden="true">
  <div class="mobile-menu-head container">
    <a href="index.html" aria-label="AmeriDex home"><img class="header-logo-img" style="height:36px" src="assets/img/logo.png" alt="AmeriDex"></a>
    <button class="hamburger mobile-menu-close" aria-label="Close menu">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="M6 6 18 18M6 18 18 6"/></svg>
    </button>
  </div>
  <nav class="container" aria-label="Mobile">
{mobile_html}
    <a href="samples-request.html">Request samples</a>
    <a href="warranty-registration.html">Register Warranty</a>
  </nav>
  <div class="mobile-cta container">
    <a class="btn btn-red btn-lg" href="get-a-free-quote.html">Start my project</a>
    <a class="btn btn-outline-white btn-lg" href="{DEALER_PORTAL_URL}" target="_blank" rel="noopener">Dealer Portal</a>
  </div>
</div>
'''


def footer():
    return f'''
<footer class="site-footer">
  <div class="container footer-grid">

    <div class="footer-col footer-brand">
      <h4>SITEMAP</h4>
      <ul>
        <li><a href="index.html">Home</a></li>
        <li><a href="https://www.youtube.com/channel/UC3Fz0TEKbLpQZefnYQNCxmg" target="_blank" rel="noopener">Instructional Videos</a></li>
        <li><a href="keep-under-deck-dry.html">Keep Under Deck Dry</a></li>
        <li><a href="protect-under-deck-from-water.html">Protect Under Deck From Water</a></li>
        <li><a href="gallery.html">Gallery</a></li>
        <li><a href="where-to-buy.html">Where to Buy</a></li>
        <li><a href="get-a-free-quote.html">Get a Free Quote</a></li>
        <li><a href="contact-us.html">Contact Us</a></li>
        <li><a href="warranty-registration.html">Register Warranty</a></li>
      </ul>
    </div>

    <div class="footer-col">
      <h4>LOCATION</h4>
      <p class="footer-contact">
        <a href="mailto:sales@ameridex.com?subject=AmeriDex%20Inquiry">sales@ameridex.com</a><br>
        <a href="tel:18002179206">Tel. 1-800-217-9206</a><br>
        1129A Industrial Parkway<br>
        Brick, NJ 08724
      </p>
    </div>

    <div class="footer-col">
      <h4>SOCIAL</h4>
      <ul>
        <li><a href="https://www.facebook.com/ameridexdryspace/" target="_blank" rel="noopener">Facebook</a></li>
      </ul>
      <p style="margin-top:1rem;color:rgba(255,255,255,0.78);font-size:0.92rem;line-height:1.55;max-width:18rem;">Under-deck dryspace systems that protect and transform outdoor living.</p>
      <div class="badge-row">
        <span class="badge-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 5h18v14H3z"/><path d="M3 9h18M3 13h18"/></svg>Made in USA</span>
        <span class="badge-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2 4 5v6c0 5 3.5 9.4 8 11 4.5-1.6 8-6 8-11V5l-8-3z"/></svg>Warranty</span>
      </div>
    </div>

    <div class="footer-col footer-logo-block">
      <img src="assets/img/logo.png" alt="AmeriDex">
      <p style="color:rgba(255,255,255,0.7);font-size:0.85rem;margin-top:0.25rem;">Authorized dealers, log in to manage orders.</p>
      <a href="{DEALER_PORTAL_URL}" target="_blank" rel="noopener" class="footer-portal-pill">Dealer Portal</a>
    </div>

  </div>
  <div class="footer-bottom">
    <div class="container">© 2026 by A &amp; M Building Products</div>
  </div>
</footer>

<a class="dealer-pill" href="{DEALER_PORTAL_URL}" target="_blank" rel="noopener" aria-label="AmeriDex Dealer Portal (opens new tab)">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/></svg>
  AmeriDex Dealer Portal
</a>

</body>
</html>
'''


# ----------------------------------------------------------------------
# REUSABLE BLOCKS
# ----------------------------------------------------------------------

SWATCHES = [
    ("Driftwood",  "driftwood",  "solid",      "Solid"),
    ("Khaki",      "khaki",      "solid",      "Solid"),
    ("Slate",      "slate",      "solid",      "Solid"),
    ("Beachwood",  "beachwood",  "variegated", "Variegated"),
    ("Chestnut",   "chestnut",   "variegated", "Variegated"),
    ("Redwood",    "redwood",    "variegated", "Variegated"),
    ("Hazelnut",   "hazelnut",   "variegated", "Variegated"),
]


def trust_strip_white():
    return '''
<section class="trust-strip-white reveal">
  <div class="container">
    <div class="trust-strip-white-grid">
      <div>
        <div class="trust-icon">
          <svg viewBox="0 0 24 24"><path d="M3 4v16"/><path d="M3 4h12l-2 4 2 4H3"/></svg>
        </div>
        <span class="trust-title">American Made</span>
        <span class="trust-sub">Produced in the USA</span>
      </div>
      <div>
        <div class="trust-icon">
          <svg viewBox="0 0 24 24"><path d="M12 3s-6 7.5-6 12a6 6 0 0 0 12 0c0-4.5-6-12-6-12z"/><path d="M9.5 14a2.5 2.5 0 0 0 2.5 2.5"/></svg>
        </div>
        <span class="trust-title">Integrated Waterproofing</span>
        <span class="trust-sub">Seamless protection</span>
      </div>
      <div>
        <div class="trust-icon">
          <svg viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="3" rx="0.5"/><rect x="3" y="11" width="18" height="3" rx="0.5"/><rect x="3" y="16" width="18" height="3" rx="0.5"/></svg>
        </div>
        <span class="trust-title">Premium PVC Decking</span>
        <span class="trust-sub">Durable and low-maintenance</span>
      </div>
    </div>
  </div>
</section>
'''


def cross_section_svg():
    """AmeriDex assembly cross-section, generated directly from the geometry
    in Assem2.STEP and Azek-Seal-4-19-19-Version-1.2.STEP. The SVG file lives
    at assets/img/diagrams/ameridex-system.svg and is the source of truth for
    the board + Dexerdry seal profile. Do NOT replace with hand-drawn shapes."""
    return '''
<img src="assets/img/diagrams/ameridex-system.svg"
     alt="AmeriDex assembly cross-section: cellular PVC deck boards locking onto the Dexerdry TPE seal"
     loading="lazy"
     style="width:100%;height:auto;display:block;">
'''


def swatch_grid_v2_html():
    cards = []
    for name, slug, kind, label in SWATCHES:
        cards.append(f'''      <div class="swatch-card-v2 reveal">
        <img src="assets/img/swatches/{slug}.png" alt="AmeriDex {name} cellular PVC deck board color sample" loading="lazy">
        <h3>{name}</h3>
        <span class="tag-pill {kind}">{label}</span>
      </div>''')
    return "\n".join(cards)


# ----------------------------------------------------------------------
# PAGES
# ----------------------------------------------------------------------

def page_index():
    body = f'''
<main id="main">

  <!-- Hero with photo on right, navy gradient overlay -->
  <section class="hero hero-with-photo">
    <div class="hero-photo" aria-hidden="true">
      <img src="assets/img/hero.jpg" alt="Finished dry living space under an AmeriDex Dryspace deck with lounge and dining furniture" loading="eager" fetchpriority="high" width="1600" height="1066">
    </div>
    <div class="container">
      <div class="hero-content reveal">
        <h1>The Integrated Above-Joist Deck Drainage System.</h1>
        <p class="kicker">AmeriDex is the American-made above-joist deck drainage system. Cellular PVC boards lock onto the Dexerdry seal so 100% of rain is diverted off the deck, protecting your framing and creating a dry, finished living space below.</p>
        <div class="hero-cta">
          <a class="btn btn-red btn-lg" href="get-a-free-quote.html">Start my project</a>
          <a class="btn btn-outline-white btn-lg" href="how-system-works.html">See How it Works</a>
        </div>
        <a class="hero-pdf-link" href="pdfs/ameridex-installation.pdf" target="_blank" rel="noopener">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M12 18v-6M9 15l3 3 3-3"/></svg>
          Download Installation Instructions (PDF)
        </a>
        <!-- TODO: drop the real installation PDF at pdfs/ameridex-installation.pdf -->
      </div>
    </div>
  </section>

  <!-- Deck Board Colors -->
  <section class="section-pad bg-cream">
    <div class="container">
      <div class="section-head reveal" style="text-align:center;margin-left:auto;margin-right:auto;">
        <h2 style="color:var(--navy)">Deck Board Colors</h2>
        <p>Visualize the perfect finish for your AmeriDex system.</p>
      </div>
      <div class="swatch-grid-v2">
{swatch_grid_v2_html()}
      </div>
      <div class="swatch-cta-row reveal">
        <a class="btn btn-navy btn-lg" href="samples-request.html">Order Color Samples</a>
      </div>
    </div>
  </section>

  {trust_strip_white()}

  <!-- Why the AmeriDex System Works -->
  <section class="section-pad bg-offwhite">
    <div class="container">
      <div class="why-grid">
        <div class="reveal">
          <div class="section-head" style="margin-bottom:1.25rem;">
            <h2 style="color:var(--navy)">Why an Above-Joist Deck Drainage System Wins</h2>
            <p>The AmeriDex water-diverting system stops every drop at the surface, before it ever touches your joists or beams.</p>
          </div>
          <div class="why-bullets">
            <div class="why-bullet">
              <svg viewBox="0 0 96 72" role="img" aria-label="Integrated board and seal" xmlns="http://www.w3.org/2000/svg" style="width:96px;height:72px;margin:0 auto 0.6rem;display:block;">
                <rect x="4"  y="24" width="40" height="36" fill="#7a5538" stroke="#0A2A4E" stroke-width="2"/>
                <rect x="52" y="24" width="40" height="36" fill="#7a5538" stroke="#0A2A4E" stroke-width="2"/>
                <rect x="40" y="18" width="16" height="48" fill="#9aa0a8" stroke="#0A2A4E" stroke-width="2"/>
              </svg>
              <span class="label">Integrated<br>Board + Seal</span>
            </div>
            <div class="why-bullet">
              <svg viewBox="0 0 96 72" role="img" aria-label="Water stopped at the surface" xmlns="http://www.w3.org/2000/svg" style="width:96px;height:72px;margin:0 auto 0.6rem;display:block;">
                <g fill="#3D8BD6" stroke="#0A2A4E" stroke-width="1.5">
                  <path d="M30 6 c-4 8 -8 14 -8 18 a8 8 0 0 0 16 0 c0 -4 -4 -10 -8 -18z"/>
                  <path d="M48 2  c-4 8 -8 14 -8 18 a8 8 0 0 0 16 0 c0 -4 -4 -10 -8 -18z"/>
                  <path d="M66 6  c-4 8 -8 14 -8 18 a8 8 0 0 0 16 0 c0 -4 -4 -10 -8 -18z"/>
                </g>
                <rect x="4" y="42" width="88" height="22" fill="#7a5538" stroke="#0A2A4E" stroke-width="2"/>
              </svg>
              <span class="label">Water and Debris Stopped<br>at the Surface</span>
            </div>
            <div class="why-bullet">
              <svg viewBox="0 0 96 72" role="img" aria-label="Dry space below" xmlns="http://www.w3.org/2000/svg" style="width:96px;height:72px;margin:0 auto 0.6rem;display:block;">
                <rect x="4" y="6" width="88" height="10" fill="#7a5538" stroke="#0A2A4E" stroke-width="2"/>
                <rect x="10" y="16" width="6"  height="48" fill="#5a4632" stroke="#0A2A4E" stroke-width="2"/>
                <rect x="80" y="16" width="6"  height="48" fill="#5a4632" stroke="#0A2A4E" stroke-width="2"/>
                <rect x="22" y="42" width="22" height="22" fill="#cdb795" stroke="#0A2A4E" stroke-width="1.5"/>
                <rect x="50" y="34" width="22" height="30" fill="#cdb795" stroke="#0A2A4E" stroke-width="1.5"/>
              </svg>
              <span class="label">Dry Space<br>Below</span>
            </div>
          </div>
        </div>
        <div class="why-diagram reveal">
{cross_section_svg()}
        </div>
      </div>
    </div>
  </section>

  <!-- SEO content: Above-Joist vs Below-Joist context -->
  <section class="section-pad bg-white">
    <div class="container" style="max-width:880px;">
      <div class="section-head reveal">
        <h2 style="color:var(--navy)">Above-Joist vs Below-Joist: The Real Difference</h2>
        <p>Most under-deck drainage systems are retrofits. AmeriDex is engineered into the deck itself.</p>
      </div>
      <div class="reveal" style="font-size:1.03rem;line-height:1.7;color:var(--navy);">
        <p>An <strong>above-joist deck drainage system</strong> stops water at the walking surface. The waterproofing happens between the boards, on top of the joists, before a single drop reaches the framing. AmeriDex is built this way. Cellular PVC deck boards lock onto the Dexerdry TPE seal as the deck is installed, so 100% of the rain is diverted off the deck and away from the structure.</p>
        <p>Below-joist, retrofit drainage systems are different. They are tray, panel, or membrane assemblies hung underneath an existing deck after the boards are already in place. Water still falls through the gaps in the deck boards, soaks the joists and beams, and is caught in a tray below. Over time, those wet joists can rot, fasteners can corrode, and stains can bleed through onto the panels.</p>
        <p>If you are building a new deck and you want a real <strong>dry space under the deck</strong>, integrated above-joist drainage is the only way to keep your framing dry for the life of the structure. <a href="above-joist-vs-below-joist-deck-drainage.html">See the full above-joist vs below-joist comparison</a>, read the deeper <a href="above-joist-deck-drainage.html">above-joist deck drainage explainer</a>, or learn <a href="about.html">about AmeriDex and the patented Dexerdry seal</a> behind the system.</p>
      </div>
    </div>
  </section>

  <!-- Lifestyle -->
  <section class="section-pad bg-cream">
    <div class="container">
      <div class="section-head reveal" style="text-align:center;margin-left:auto;margin-right:auto;">
        <h2 style="color:var(--navy)">See What Your Under-Deck Space Can Become</h2>
      </div>
      <div class="lifestyle-grid">
        <div class="lifestyle-card reveal">
          <img src="assets/img/lifestyle/outdoor-kitchen.png" alt="Outdoor Kitchen: covered cooking and dining zone that stays usable in rain">
        </div>
        <div class="lifestyle-card reveal">
          <img src="assets/img/lifestyle/lounge-area.png" alt="Lounge Area: turn the space under your deck into an all-weather living room">
        </div>
        <div class="lifestyle-card reveal">
          <img src="assets/img/lifestyle/kids-play-zone.png" alt="Kids Play Zone: give kids a dry place to play, even when the weather does not cooperate">
        </div>
      </div>
      <div style="text-align:center;margin-top:2.25rem;" class="reveal">
        <a class="btn btn-red btn-lg" href="get-a-free-quote.html">Start my project</a>
      </div>
    </div>
  </section>

</main>
'''
    return head(
        "Above-Joist Deck Drainage System | AmeriDex Made in USA",
        "AmeriDex is the integrated above-joist deck drainage system. Cellular PVC boards lock onto the Dexerdry seal so rain is diverted off the deck and the space below stays dry. Made in the USA.",
        # description is 192 chars; Google may truncate at ~160 but the lead phrase is preserved
        canonical="",
        keywords="above-joist deck drainage, above joist deck drainage system, under deck drainage system, water diverting system for deck, dry space under deck, integrated deck drainage, deck water diverter, PVC deck drainage, AmeriDex, Dexerdry, new deck construction, made in USA deck drainage",
        extra_jsonld=[PRODUCT_JSONLD, breadcrumb_schema(("Home", ""))],
        extra_head='\n  <link rel="preload" as="image" href="assets/img/hero.jpg" fetchpriority="high">',
    ) + header("index.html") + body + footer()


def page_how_it_works():
    faq_html = "\n        ".join(
        f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>'
        for q, a in HOW_IT_WORKS_FAQ
    )
    body = f'''
<main id="main">

  <section class="page-hero">
    <div class="container">
      <span class="eyebrow">ENGINEERED FOR DRY SPACE</span>
      <h1>How the AmeriDex Dryspace System Works</h1>
      <p>Integrated PVC decking and Dexerdry seal stop water at the surface and create dry, finished space below.</p>
    </div>
  </section>

  <!-- Two-part system -->
  <section class="section-pad bg-offwhite">
    <div class="container">
      <div class="section-head reveal">
        <h2 style="color:var(--navy)">The Two-Part System</h2>
        <p>One product. Two engineered components working together.</p>
      </div>
      <div class="two-card-grid">
        <div class="system-card reveal">
          <div class="visual">
            <img src="assets/img/swatches/driftwood.png" alt="AmeriDex Driftwood cellular PVC deck board with authentic wood grain finish" loading="lazy">
          </div>
          <div class="body">
            <h3>Cellular PVC Deck Boards</h3>
            <p>Premium cellular PVC core with a proprietary ASA cap. Will not rot, splinter, or warp. Authentic grain. Generational lifespan.</p>
          </div>
        </div>
        <div class="system-card reveal">
          <div class="visual">
            <!-- Real Dexerdry profile generated from the seal STEP geometry.
                 Source of truth: assets/img/diagrams/dexerdry-profile.svg.
                 Do NOT replace with hand-drawn shapes. -->
            <img src="assets/img/diagrams/dexerdry-profile.svg"
                 alt="Dexerdry seal cross-section profile (from SolidWorks STEP geometry)"
                 loading="lazy"
                 style="width:100%;height:auto;display:block;">
          </div>
          <div class="body">
            <h3>Dexerdry Integrated Seal</h3>
            <p>Automotive-grade TPE seal engineered to lock between every board. Diverts every drop of rain and snowmelt off the deck and away from the framing below.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- 3 steps -->
  <section class="section-pad bg-cream">
    <div class="container">
      <div class="section-head reveal" style="text-align:center;margin-left:auto;margin-right:auto;">
        <h2 style="color:var(--navy)">How It Works in 3 Steps</h2>
      </div>
      <div class="steps">
        <div class="step reveal">
          <span class="step-num">01</span>
          <h3 style="color:var(--navy)">Frame your deck like normal.</h3>
          <p>Standard joist layout, standard framing, no special substructure. AmeriDex installs on a conventional frame at 16" o.c.</p>
        </div>
        <div class="step reveal">
          <span class="step-num">02</span>
          <h3 style="color:var(--navy)">Install AmeriDex boards with the integrated Dexerdry seal.</h3>
          <p>Interlocking fit creates a continuous water-diverting deck surface.</p>
        </div>
        <div class="step reveal">
          <span class="step-num">03</span>
          <h3 style="color:var(--navy)">Water sheds away. Under-deck space stays bone dry.</h3>
          <p>Rain runs across the deck, gets carried out by the seal, and falls clear of the joists. The space below stays dry, finished, and usable.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- New construction only -->
  <section class="section-pad bg-offwhite">
    <div class="container" style="max-width:880px;">
      <div class="callout-card reveal">
        <h3>Why New Construction Only</h3>
        <p>AmeriDex is engineered into your build from the joists up. That is exactly why it works. Retrofit drainage systems hang underneath your deck and fail. AmeriDex is the deck.</p>
      </div>
    </div>
  </section>

  <!-- Specs at a glance -->
  <section class="section-pad bg-offwhite">
    <div class="container" style="max-width:960px;">
      <div class="section-head reveal">
        <h2 style="color:var(--navy)">Specs At A Glance</h2>
      </div>
      <table class="spec-table-v2 reveal">
        <tbody>
          <tr><td>Board</td><td>Cellular PVC with proprietary ASA cap</td></tr>
          <tr><td>Seal</td><td>Dexerdry automotive-grade TPE</td></tr>
          <tr><td>Profile</td><td>Tongue-and-groove with integrated water-diverting seal</td></tr>
          <!-- TODO: confirm exact lengths offered with A&M -->
          <tr><td>Lengths</td><td>12 ft, 16 ft, 20 ft</td></tr>
          <tr><td>Joist Spacing</td><td>16" o.c. residential</td></tr>
          <tr><td>Fasteners</td><td>Starborn epoxy-coated screws or stainless screws and plugs (sold separately)</td></tr>
          <tr><td>Warranty</td><td>25-Year Residential, 10-Year Limited Commercial</td></tr>
          <tr><td>Fire Rating</td><td>Class A flame spread (ASTM E84)</td></tr>
          <tr><td>Application</td><td>New deck construction only</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- FAQ -->
  <section class="section-pad bg-cream" id="faq">
    <div class="container" style="max-width:880px;">
      <div class="section-head reveal">
        <h2 style="color:var(--navy)">Frequently Asked Questions</h2>
        <p>Everything builders, dealers, and homeowners ask before specifying AmeriDex.</p>
      </div>
      <div class="faq-list reveal">
        {faq_html}
      </div>
    </div>
  </section>

  <!-- Related reading -->
  <section class="section-pad bg-white">
    <div class="container" style="max-width:880px;">
      <div class="section-head reveal">
        <h2 style="color:var(--navy)">Related Reading</h2>
      </div>
      <ul class="reveal" style="font-size:1.03rem;line-height:1.8;color:var(--navy);list-style:disc;padding-left:1.25rem;">
        <li><a href="above-joist-deck-drainage.html">What is an above-joist deck drainage system?</a></li>
        <li><a href="above-joist-vs-below-joist-deck-drainage.html">Above-joist vs below-joist deck drainage: a builder's comparison</a></li>
        <li><a href="about.html">About AmeriDex: the engineering origin behind the system</a></li>
      </ul>
    </div>
  </section>

  <!-- CTA band -->
  <section class="section-pad bg-navy">
    <div class="container" style="text-align:center;">
      <h2 style="color:#fff;font-size:clamp(1.6rem,3vw,2.4rem);margin-bottom:1.5rem;">Ready to build with AmeriDex?</h2>
      <div style="display:flex;gap:0.85rem;justify-content:center;flex-wrap:wrap;">
        <a class="btn btn-red btn-lg" href="get-a-free-quote.html">Start my project</a>
        <a class="btn btn-outline-white btn-lg" href="samples-request.html">Request samples</a>
      </div>
    </div>
  </section>

</main>
'''
    return head(
        "How the AmeriDex Dryspace System Works | Above-Joist Deck Drainage",
        "See how AmeriDex PVC boards and the Dexerdry TPE seal create a dry under-deck living space. Above-joist drainage, 16 in. o.c. install, 25-year warranty.",
        canonical="how-system-works.html",
        keywords="how under deck drainage works, above joist deck drainage system, Dexerdry seal, integrated deck drainage, PVC deck installation",
        extra_jsonld=[
            PRODUCT_JSONLD,
            FAQ_JSONLD,
            breadcrumb_schema(("Home", ""), ("How System Works", "how-system-works.html")),
        ],
    ) + header("how-system-works.html") + body + footer()


def page_gallery():
    body = '''
<main id="main">

  <section class="page-hero">
    <div class="container">
      <h1>AmeriDex Dryspace Showcase</h1>
      <p>See how customers utilized their extra space.</p>
    </div>
  </section>

  <section class="section-pad bg-offwhite">
    <div class="container">
      <!-- Gallery photos live in assets/img/gallery/ as 01-deck-overview.jpg through 08-deck-stairs.jpg.
           Each figure has a marketing caption: a short headline + tagline meant to help
           the visitor picture themselves owning the space, not just describe the photo.
           To add another, drop the file in that folder and append a <figure class="gallery-photo"> here. -->
      <div class="gallery-carousel reveal">
        <figure class="gallery-photo">
          <img src="assets/img/gallery/01-deck-overview.jpg" alt="Illuminated AmeriDex dock and walkway at night with lake view" loading="lazy">
          <figcaption><strong>Entertain after dark.</strong>A lit walkway and dock that’s ready when you are.</figcaption>
        </figure>
        <figure class="gallery-photo">
          <img src="assets/img/gallery/02-deck-detail.jpg" alt="Aerial view of an AmeriDex elevated lakeside deck" loading="lazy">
          <figcaption><strong>Build over the water.</strong>Lakeside platforms that stay dry season after season.</figcaption>
        </figure>
        <figure class="gallery-photo">
          <img src="assets/img/gallery/03-deck-side.jpg" alt="Side view of an elevated AmeriDex boathouse deck with lower-level living space" loading="lazy">
          <figcaption><strong>Two stories of living.</strong>Sun deck above, covered slip below. One footprint, double the use.</figcaption>
        </figure>
        <figure class="gallery-photo">
          <img src="assets/img/gallery/04-deck-corner.jpg" alt="Comfortable patio seating beneath an AmeriDex deck" loading="lazy">
          <figcaption><strong>Your second living room, outside.</strong>Dappled shade, all-weather furniture, zero rain interruptions.</figcaption>
        </figure>
        <figure class="gallery-photo">
          <img src="assets/img/gallery/05-deck-installed.jpg" alt="Multi-level AmeriDex deck showing the dry, finished underside above a covered patio" loading="lazy">
          <figcaption><strong>Family wing, weatherproof.</strong>Finished underside turns square footage you weren’t using into the room you live in.</figcaption>
        </figure>
        <figure class="gallery-photo">
          <img src="assets/img/gallery/06-deck-finished.jpg" alt="Finished AmeriDex deck with outdoor kitchen and dining area" loading="lazy">
          <figcaption><strong>Cook, dine, repeat.</strong>Outdoor kitchen and dining table that don’t pack up when the forecast turns.</figcaption>
        </figure>
        <figure class="gallery-photo">
          <img src="assets/img/gallery/07-deck-railing.jpg" alt="Family relaxing on a paver patio under an AmeriDex deck" loading="lazy">
          <figcaption><strong>Rain or shine.</strong>The patio underneath stays bone dry while the deck does the work.</figcaption>
        </figure>
        <figure class="gallery-photo">
          <img src="assets/img/gallery/08-deck-stairs.jpg" alt="Two-story home with an AmeriDex deck and finished, lit under-deck living space below" loading="lazy">
          <figcaption><strong>Doubled square footage.</strong>Recessed lighting, fireplace, finished walls. Where your family actually wants to be.</figcaption>
        </figure>
      </div>
      <div style="text-align:center;margin-top:3rem;" class="reveal">
        <a class="footer-portal-pill" href="contact-us.html" style="background:var(--navy);border-color:var(--navy);">Talk to an AmeriDex Specialist</a>
      </div>
    </div>
  </section>

</main>
'''
    return head(
        "Gallery: Real AmeriDex Under-Deck Spaces | Dryspace Showcase",
        "Real AmeriDex Dryspace installations. See finished under-deck living rooms, outdoor kitchens, fire-pit lounges, and lakeside decks built dry.",
        canonical="gallery.html",
        keywords="under deck drainage gallery, dry space under deck examples, AmeriDex installations, dexerdry deck photos",
        extra_jsonld=[
            breadcrumb_schema(("Home", ""), ("Gallery", "gallery.html")),
            {
                "@context": "https://schema.org",
                "@type": "ImageGallery",
                "name": "AmeriDex Dryspace Installations",
                "description": "Real-world AmeriDex Dryspace System under-deck living spaces.",
                "url": f"{SITE_ORIGIN}/gallery.html",
            },
        ],
    ) + header("gallery.html") + body + footer()


def page_quote():
    body = '''
<main id="main">

  <section class="page-hero">
    <div class="container">
      <h1 data-quote-h1>Get a Free AmeriDex Quote</h1>
      <p data-quote-sub>Share a few details about your deck and how you may want to use the space underneath. We will connect you with an AmeriDex expert.</p>
    </div>
  </section>

  <section class="section-pad bg-offwhite">
    <div class="container">

      <div class="form-card reveal">
        <div class="form-card-header">
          <h2>AmeriDex Quote Request</h2>
          <p data-quote-cardsub>Fill out the form below and we will provide a detailed quote for your DrySpace project within 1-2 business days.</p>
        </div>

        <div class="step-indicator" aria-hidden="true">
          <span class="step-pill active"><span class="num">1</span> Project Basics</span>
          <span class="step-connector"></span>
          <span class="step-pill"><span class="num">2</span> Site Details</span>
          <span class="step-connector"></span>
          <span class="step-pill"><span class="num">3</span> Contact</span>
        </div>

        <!-- Replace https://formspree.io/f/xreljrrd with your real endpoint. -->
        <form class="form" action="https://formspree.io/f/xreljrrd" method="POST" enctype="multipart/form-data">

          <div class="form-section" data-dealer-hide>
            <h3>1. Project Basics</h3>
            <div class="form-row form-row-2">
              <div>
                <label for="deck_status">New or existing deck?</label>
                <select id="deck_status" name="deck_status">
                  <option value="">Select an option</option>
                  <option>New construction</option>
                  <option>Replacing an existing deck</option>
                  <option>Other</option>
                </select>
              </div>
              <div>
                <label for="deck_height">Deck height off the ground</label>
                <select id="deck_height" name="deck_height">
                  <option value="">Select height</option>
                  <option>Under 8 ft</option>
                  <option>8-12 ft</option>
                  <option>12+ ft</option>
                </select>
              </div>
            </div>
            <div class="form-row form-row-2">
              <div>
                <label for="deck_width">Deck size (approx. width, ft)</label>
                <input type="number" id="deck_width" name="deck_width" min="0" inputmode="numeric">
              </div>
              <div>
                <label for="deck_depth">Deck size (approx. depth, ft)</label>
                <input type="number" id="deck_depth" name="deck_depth" min="0" inputmode="numeric">
              </div>
            </div>
            <div>
              <label>How do you want to use the space below?</label>
              <div class="checkbox-row">
                <label><input type="checkbox" name="use_below" value="Outdoor Kitchen"> Outdoor Kitchen</label>
                <label><input type="checkbox" name="use_below" value="Lounge Area"> Lounge Area</label>
                <label><input type="checkbox" name="use_below" value="Kids Play Zone"> Kids Play Zone</label>
                <label><input type="checkbox" name="use_below" value="Storage / Gear"> Storage / Gear</label>
                <label><input type="checkbox" name="use_below" value="Other"> Other</label>
              </div>
            </div>
          </div>

          <div class="form-section" data-dealer-show style="display:none;">
            <h3>Tell us about your business</h3>
            <div>
              <label for="business_info">Tell us about your business</label>
              <textarea id="business_info" name="business_info" placeholder="Company name, type of business (lumber yard, builder, architect, etc.), markets served, and what you are looking for from AmeriDex."></textarea>
            </div>
          </div>

          <div class="form-section" data-dealer-hide>
            <h3>2. Site Details</h3>
            <div class="form-row form-row-2">
              <div>
                <label for="zip">ZIP Code</label>
                <input type="text" id="zip" name="zip" inputmode="numeric" autocomplete="postal-code">
              </div>
              <div>
                <label for="city">City</label>
                <input type="text" id="city" name="city" autocomplete="address-level2">
              </div>
            </div>
            <div>
              <label for="state">State</label>
              <input type="text" id="state" name="state" autocomplete="address-level1">
            </div>
            <div>
              <label for="files">Upload photos or plans</label>
              <input type="file" id="files" name="files" multiple accept="image/*,.pdf">
              <p class="helper">Images and PDFs only. Max 10MB per file.</p>
            </div>
          </div>

          <div class="form-section">
            <h3>3. Contact</h3>
            <div class="form-row form-row-2">
              <div>
                <label for="first_name">First Name *</label>
                <input type="text" id="first_name" name="first_name" required autocomplete="given-name">
              </div>
              <div>
                <label for="last_name">Last Name *</label>
                <input type="text" id="last_name" name="last_name" required autocomplete="family-name">
              </div>
            </div>
            <div class="form-row form-row-2">
              <div>
                <label for="email">Email *</label>
                <input type="email" id="email" name="email" required autocomplete="email">
              </div>
              <div>
                <label for="phone">Phone (optional)</label>
                <input type="tel" id="phone" name="phone" autocomplete="tel">
              </div>
            </div>
            <div>
              <label for="best_time">Best time to reach you</label>
              <select id="best_time" name="best_time">
                <option value="">Select a window</option>
                <option>Morning</option>
                <option>Afternoon</option>
                <option>Evening</option>
                <option>Anytime</option>
              </select>
            </div>
          </div>

          <div class="form-section">
            <label class="agree-line">
              <input type="checkbox" name="agree" required>
              <span>I agree that AmeriDex or an authorized installer may contact me regarding my inquiry.</span>
            </label>
          </div>

          <div class="submit-row">
            <button type="submit" class="btn btn-red btn-lg">Submit Quote Request</button>
          </div>
        </form>
      </div>

    </div>
  </section>

</main>
'''
    return head(
        "Get a Free AmeriDex Quote | Under-Deck Drainage Pricing",
        "Request a free AmeriDex Dryspace quote. Share your new deck plans and we will price cellular PVC boards, the Dexerdry seal, and accessories.",
        canonical="get-a-free-quote.html",
        keywords="AmeriDex quote, PVC decking quote, under deck drainage pricing, deck system pricing, get a deck quote",
        extra_jsonld=[
            breadcrumb_schema(("Home", ""), ("Get a Free Quote", "get-a-free-quote.html")),
        ],
    ) + header("get-a-free-quote.html") + body + footer()


def page_contact():
    states = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"]
    state_options = "\n".join(f'                  <option>{s}</option>' for s in states)
    body = f'''
<main id="main">

  <section class="page-hero">
    <div class="container">
      <h1>Contact AmeriDex</h1>
      <p>Have questions about the AmeriDex dryspace system, products, or installation? Send us a message and we will respond within 1-2 business days.</p>
    </div>
  </section>

  <section class="section-pad bg-offwhite">
    <div class="container">

      <div class="form-card reveal">
        <div class="form-card-header">
          <h2>Contact AmeriDex</h2>
          <p>Send us a message and we will respond within 1-2 business days.</p>
        </div>

        <!-- Replace https://formspree.io/f/xreljrrd with your real endpoint. -->
        <form class="form" action="https://formspree.io/f/xreljrrd" method="POST">
          <div class="form-row form-row-2">
            <div>
              <label for="first_name">First Name *</label>
              <input type="text" id="first_name" name="first_name" required autocomplete="given-name">
            </div>
            <div>
              <label for="last_name">Last Name *</label>
              <input type="text" id="last_name" name="last_name" required autocomplete="family-name">
            </div>
          </div>
          <div class="form-row form-row-2">
            <div>
              <label for="email">Email *</label>
              <input type="email" id="email" name="email" required autocomplete="email">
            </div>
            <div>
              <label for="phone">Phone (optional)</label>
              <input type="tel" id="phone" name="phone" autocomplete="tel">
            </div>
          </div>
          <div class="form-row form-row-2">
            <div>
              <label for="city">City *</label>
              <input type="text" id="city" name="city" required autocomplete="address-level2">
            </div>
            <div>
              <label for="state">State / Province *</label>
              <select id="state" name="state" required autocomplete="address-level1">
                <option value="">Select a state</option>
{state_options}
              </select>
            </div>
          </div>
          <div class="form-row form-row-2">
            <div>
              <label for="zip">ZIP / Postal Code *</label>
              <input type="text" id="zip" name="zip" required inputmode="numeric" autocomplete="postal-code">
            </div>
            <div>
              <label for="topic">How can we help? *</label>
              <select id="topic" name="topic" required>
                <option value="">Select a topic</option>
                <option>General Question</option>
                <option>Pricing &amp; Quote</option>
                <option>Installation Help</option>
                <option>Warranty</option>
                <option>Become a Dealer</option>
                <option>Other</option>
              </select>
            </div>
          </div>
          <div>
            <label for="message">Message *</label>
            <textarea id="message" name="message" required></textarea>
          </div>
          <label class="agree-line">
            <input type="checkbox" name="agree" required>
            <span>I agree that AmeriDex or an authorized installer may contact me regarding my inquiry.</span>
          </label>
          <div class="submit-row">
            <button type="submit" class="btn btn-red btn-lg">Send Message</button>
          </div>
        </form>
      </div>

      <div class="direct-contact-band reveal">
        <div class="direct-contact-grid">
          <div>
            <h4>Sales</h4>
            <p>
              <a href="mailto:sales@ameridex.com?subject=AmeriDex%20Inquiry">sales@ameridex.com</a><br>
              <a href="tel:18002179206">1-800-217-9206</a><br>
              Mon-Fri, 8am-5pm ET
            </p>
          </div>
          <div>
            <h4>Address</h4>
            <p>1129A Industrial Parkway<br>Brick, NJ 08724</p>
          </div>
          <div>
            <h4>Dealer Portal</h4>
            <p><a href="https://dealerportal.ameridex.com" target="_blank" rel="noopener">dealerportal.ameridex.com</a><br>For authorized AmeriDex dealers and installers.</p>
          </div>
        </div>
      </div>

    </div>
  </section>

</main>
'''
    return head(
        "Contact AmeriDex | New Jersey PVC Decking Manufacturer",
        "Reach the AmeriDex team in Brick, NJ. Call 1-800-217-9206 or email sales@ameridex.com for product, dealer, and Dryspace system questions.",
        canonical="contact-us.html",
        keywords="contact AmeriDex, AmeriDex phone number, AmeriDex Brick NJ, decking manufacturer New Jersey, A and M Building Products",
        extra_jsonld=[
            LOCAL_BUSINESS_JSONLD,
            breadcrumb_schema(("Home", ""), ("Contact Us", "contact-us.html")),
        ],
    ) + header("contact-us.html") + body + footer()


def page_samples():
    color_picks = []
    for name, slug, kind, label in SWATCHES:
        color_picks.append(f'''        <button type="button" class="color-pick" data-color="{name}" aria-pressed="false">
          <img src="assets/img/swatches/{slug}.png" alt="AmeriDex {name} cellular PVC deck board color sample" loading="lazy">
          <span>{name}</span>
          <span class="check" aria-hidden="true">&#10003;</span>
        </button>''')
    color_html = "\n".join(color_picks)

    body = f'''
<main id="main">

  <section class="page-hero">
    <div class="container">
      <span class="eyebrow">FREE SAMPLES</span>
      <h1>Request AmeriDex Deck Samples</h1>
      <p>Pick the colors you want to see in person. We will ship small deck board samples to your door at no cost.</p>
    </div>
  </section>

  <section class="section-pad bg-offwhite">
    <div class="container">

      <div class="form-card reveal">
        <!-- Replace https://formspree.io/f/xreljrrd with your real endpoint. -->
        <form class="form" action="https://formspree.io/f/xreljrrd" method="POST">

          <div class="form-section">
            <h3>1. Choose your sample size</h3>
            <div class="size-radio-row">
              <label class="size-radio">
                <input type="radio" name="sample_size" value="6-Inch Sample" checked>
                <span class="icon">
                  <svg viewBox="0 0 80 36" fill="none" stroke="#0A2A4E" stroke-width="2"><rect x="2" y="6" width="76" height="24" rx="3"/><path d="M14 10v16M26 10v16M38 10v16M50 10v16M62 10v16"/></svg>
                </span>
                <strong>6-Inch Sample</strong>
                <span>Compact swatch, great for color matching.</span>
              </label>
              <label class="size-radio">
                <input type="radio" name="sample_size" value="12-Inch Sample">
                <span class="icon">
                  <svg viewBox="0 0 120 36" fill="none" stroke="#0A2A4E" stroke-width="2"><rect x="2" y="6" width="116" height="24" rx="3"/><path d="M16 10v16M30 10v16M44 10v16M58 10v16M72 10v16M86 10v16M100 10v16"/></svg>
                </span>
                <strong>12-Inch Sample</strong>
                <span>Larger piece, see the full grain and texture.</span>
              </label>
            </div>
          </div>

          <div class="form-section">
            <h3>2. Select your colors</h3>
            <div class="color-pick-head">
              <span class="color-pick-counter">0 colors selected</span>
              <button type="button" class="select-all-pill">Select All</button>
            </div>
            <div class="color-pick-grid">
{color_html}
            </div>
            <input type="hidden" name="selected_colors" value="">
          </div>

          <div class="form-section">
            <h3>3. Where do we send them?</h3>
            <div class="form-row form-row-2">
              <div>
                <label for="first_name">First Name *</label>
                <input type="text" id="first_name" name="first_name" required autocomplete="given-name">
              </div>
              <div>
                <label for="last_name">Last Name *</label>
                <input type="text" id="last_name" name="last_name" required autocomplete="family-name">
              </div>
            </div>
            <div class="form-row form-row-2">
              <div>
                <label for="email">Email *</label>
                <input type="email" id="email" name="email" required autocomplete="email">
              </div>
              <div>
                <label for="phone">Phone</label>
                <input type="tel" id="phone" name="phone" autocomplete="tel">
              </div>
            </div>
            <div>
              <label for="street">Mailing Address *</label>
              <input type="text" id="street" name="street" required placeholder="Street address" autocomplete="street-address">
            </div>
            <div class="form-row form-row-2">
              <div>
                <label for="city">City *</label>
                <input type="text" id="city" name="city" required autocomplete="address-level2">
              </div>
              <div>
                <label for="state">State *</label>
                <input type="text" id="state" name="state" required autocomplete="address-level1">
              </div>
            </div>
            <div class="form-row form-row-2">
              <div>
                <label for="zip">ZIP *</label>
                <input type="text" id="zip" name="zip" required autocomplete="postal-code">
              </div>
              <div>
                <label for="project_type">Project type</label>
                <select id="project_type" name="project_type">
                  <option value="">Select a type</option>
                  <option>Homeowner</option>
                  <option>Builder</option>
                  <option>Architect</option>
                  <option>Dealer prospect</option>
                </select>
              </div>
            </div>
          </div>

          <div class="submit-row">
            <button type="submit" class="btn btn-red btn-lg">Send My Sample Request</button>
          </div>
        </form>
      </div>

    </div>
  </section>

</main>
'''
    return head(
        "Free AmeriDex Decking Samples | 7 PVC Color Options",
        "Order free AmeriDex PVC decking samples. Pick from seven authentic wood-grain colors and we will ship them direct to match your home and deck.",
        canonical="samples-request.html",
        keywords="free decking samples, AmeriDex color samples, PVC deck colors, deck board samples, free PVC decking sample",
        extra_jsonld=[
            breadcrumb_schema(("Home", ""), ("Order Samples", "samples-request.html")),
        ],
    ) + header("samples-request.html") + body + footer()


def page_warranty():
    body = '''
<main id="main">

  <section class="page-hero">
    <div class="container">
      <span class="eyebrow">A&amp;M BUILDING PRODUCTS LLC</span>
      <h1>AmeriDex Dryspace System Warranty Registration</h1>
      <p>25-Year Residential / 10-Year Commercial Limited Warranty.</p>
    </div>
  </section>

  <section class="section-pad bg-offwhite">
    <div class="container">

      <div class="form-card reveal">
        <div class="note-yellow">
          <strong>Important.</strong> Registration is required within 30 days of purchase or installation completion (whichever is later) for warranty coverage to take effect. Submit this form to register your AmeriDex Dryspace System installation.
        </div>

        <!-- Replace https://formspree.io/f/xreljrrd with your real endpoint. -->
        <form class="form" action="https://formspree.io/f/xreljrrd" method="POST" enctype="multipart/form-data">

          <div class="form-section">
            <h3>Purchaser Information</h3>
            <div>
              <label for="purchaser_name">Original Purchaser / Property Owner *</label>
              <input type="text" id="purchaser_name" name="purchaser_name" required>
            </div>
            <div class="form-row form-row-2">
              <div>
                <label for="phone">Telephone *</label>
                <input type="tel" id="phone" name="phone" required>
              </div>
              <div>
                <label for="email">Email *</label>
                <input type="email" id="email" name="email" required>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>Property Address</h3>
            <div>
              <label for="install_address">Installation Address *</label>
              <input type="text" id="install_address" name="install_address" required placeholder="Street, City, State, ZIP">
            </div>
            <div>
              <label for="mail_address">Mailing Address (if different)</label>
              <input type="text" id="mail_address" name="mail_address" placeholder="Street, City, State, ZIP">
            </div>
          </div>

          <div class="form-section">
            <h3>Purchase &amp; Installation</h3>
            <div class="form-row form-row-2">
              <div>
                <label for="purchase_date">Date of Purchase *</label>
                <input type="date" id="purchase_date" name="purchase_date" required>
              </div>
              <div>
                <label for="install_date">Date of Installation Completion *</label>
                <input type="date" id="install_date" name="install_date" required>
              </div>
            </div>
            <div class="form-row form-row-2">
              <div>
                <label for="dealer">Dealer / Distributor *</label>
                <input type="text" id="dealer" name="dealer" required>
              </div>
              <div>
                <label for="installer">Installer / Contractor *</label>
                <input type="text" id="installer" name="installer" required>
              </div>
            </div>
            <div class="form-row form-row-2">
              <div>
                <label for="lf_board">Linear Feet of Deck Board Installed *</label>
                <input type="number" id="lf_board" name="lf_board" required min="0">
              </div>
              <div>
                <label for="lf_seal">Linear Feet of Seal / Drainage Component *</label>
                <input type="number" id="lf_seal" name="lf_seal" required min="0">
              </div>
            </div>
            <div>
              <label>Application Type *</label>
              <div class="radio-inline">
                <label><input type="radio" name="application" value="Residential" required> Residential</label>
                <label><input type="radio" name="application" value="Commercial"> Commercial</label>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>Proof of Purchase</h3>
            <div>
              <label for="proof_file">Upload Proof of Purchase (receipt or invoice)</label>
              <input type="file" id="proof_file" name="proof_file" accept="image/*,.pdf">
              <p class="helper">Optional but strongly recommended. PDF or image, max 10MB.</p>
            </div>
            <div>
              <label>Proof of Purchase Status *</label>
              <div class="radio-inline">
                <label><input type="radio" name="proof_status" value="Attached above" required> Attached above</label>
                <label><input type="radio" name="proof_status" value="Will email separately"> Will email separately</label>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>Purchaser Acknowledgment</h3>
            <p style="font-size:0.92rem;line-height:1.55;color:#333;margin-bottom:1rem;">
              The AmeriDex Dryspace System Limited Warranty issued by A&amp;M Building Products LLC sets out the terms, conditions, and exclusions that apply to this product. Coverage requires installation per published instructions, including the use of approved fasteners (Starborn epoxy-coated screws or stainless steel screws and plugs), even though fasteners themselves are not warranted under this Limited Warranty.
            </p>
            <label class="agree-line">
              <input type="checkbox" name="ack" required>
              <span>I certify that the information provided is accurate and complete. I acknowledge that I have read and understand the AmeriDex Dryspace System Limited Warranty issued by A&amp;M Building Products LLC, including its terms, conditions, exclusions, and the requirement that fasteners (Starborn epoxy-coated screws or stainless steel screws and plugs) were used as specified, even though fasteners are not warranted under this Limited Warranty.</span>
            </label>
            <div class="form-row form-row-2" style="margin-top:1rem;">
              <div>
                <label for="signature">Digital Signature (type full name) *</label>
                <input type="text" id="signature" name="signature" required>
              </div>
              <div>
                <label for="signature_date">Date *</label>
                <input type="date" id="signature_date" name="signature_date" required>
              </div>
            </div>
          </div>

          <div class="submit-row">
            <button type="submit" class="btn btn-navy btn-lg">SUBMIT REGISTRATION</button>
          </div>
        </form>
      </div>

      <div style="text-align:center;margin-top:2.5rem;font-size:0.92rem;line-height:1.7;color:#444;" class="reveal">
        <strong style="display:block;color:var(--navy);font-family:var(--font-display);">A&amp;M Building Products LLC</strong>
        Attn: AmeriDex Warranty Registration<br>
        1129A Industrial Parkway, Brick, NJ 08724<br>
        <a href="mailto:sales@ameridex.com" style="color:var(--red);font-weight:600;">sales@ameridex.com</a>
      </div>

    </div>
  </section>

</main>
'''
    return head(
        "Register Your AmeriDex Warranty | 25-Year Dryspace Warranty",
        "Register your AmeriDex Dryspace purchase to activate the 25-year residential limited warranty. Submit proof of purchase and project details in minutes.",
        canonical="warranty-registration.html",
        keywords="AmeriDex warranty registration, deck warranty registration, PVC decking warranty, 25 year deck warranty",
        extra_jsonld=[
            breadcrumb_schema(("Home", ""), ("Warranty Registration", "warranty-registration.html")),
        ],
    ) + header("warranty-registration.html") + body + footer()


# ----------------------------------------------------------------------
# SEO PILLAR PAGE: Above-Joist Deck Drainage (the explainer)
# ----------------------------------------------------------------------
ABOVE_JOIST_FAQ = [
    (
        "What does above-joist deck drainage mean?",
        "Above-joist deck drainage is a waterproofing approach where the drainage layer sits on top of the joists, between the deck boards themselves, instead of being hung underneath the framing as a separate tray or panel. The deck surface itself is the watertight layer. With AmeriDex, every cellular PVC deck board locks onto the Dexerdry TPE seal as it is installed, so 100% of the rain is diverted off the deck before it can ever touch the joists, beams, or ledger.",
    ),
    (
        "Is above-joist drainage better than below-joist drainage?",
        "For new deck construction, yes. Below-joist systems are retrofits. They are designed to be added to a deck that already exists, and they protect the space below by catching water that has already passed through the deck surface and soaked the framing. Above-joist drainage stops the water before it ever gets to the joists. That keeps the structural members dry for the life of the deck and removes the long-term risk of joist rot, fastener corrosion, and stained tray panels.",
    ),
    (
        "Can an above-joist drainage system be retrofitted onto an existing deck?",
        "Not without removing the existing deck boards. The integrated water-diverting seal has to be placed between every board as the deck is built. AmeriDex specifically is engineered for new deck construction. If you already have a finished deck and you do not want to tear up the surface, a below-joist retrofit drainage system is the only option, but you will be living with wet framing.",
    ),
    (
        "Will above-joist drainage protect my joists from rot?",
        "That is the entire point of the design. With AmeriDex, water and debris stop at the surface of the deck. The joists, beams, ledger, and fasteners stay dry from the day the deck is built. Dry framing lasts longer, holds fasteners better, and removes the maintenance and inspection burden that wet framing creates over the life of the structure.",
    ),
    (
        "What does an above-joist deck drainage system cost?",
        "Pricing varies by deck size, board color, and accessories. AmeriDex does not publish public price lists because every project is quoted from a takeoff. Submit your deck dimensions through the free quote form and a regional dealer will return a written quote, usually within one or two business days.",
    ),
    (
        "What materials are used in the AmeriDex above-joist system?",
        "AmeriDex deck boards are premium cellular PVC with a proprietary ASA cap. The water-diverting layer is the Dexerdry seal, which is made from automotive-grade TPE (thermoplastic elastomer), the same material category used in car door and window seals. Both components are made in the USA.",
    ),
]

ABOVE_JOIST_FAQ_JSONLD = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in ABOVE_JOIST_FAQ
    ],
}

ABOVE_JOIST_ARTICLE_JSONLD = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Above-Joist Deck Drainage: How Integrated Systems Keep the Space Below Dry",
    "description": (
        "An in-depth guide to above-joist deck drainage systems, how they differ "
        "from below-joist retrofit systems, and why integrated above-joist "
        "drainage is the right choice for new deck construction."
    ),
    "image": f"{SITE_ORIGIN}/assets/img/og.jpg",
    "author": {"@type": "Organization", "name": "AmeriDex", "url": SITE_ORIGIN},
    "publisher": {"@id": f"{SITE_ORIGIN}/#organization"},
    "mainEntityOfPage": f"{SITE_ORIGIN}/above-joist-deck-drainage.html",
    "inLanguage": "en-US",
}


def page_above_joist_drainage():
    faq_html = "\n        ".join(
        f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>'
        for q, a in ABOVE_JOIST_FAQ
    )
    body = f'''
<main id="main">

  <!-- Pillar hero -->
  <section class="section-pad bg-navy" style="color:#fff;">
    <div class="container" style="max-width:880px;text-align:center;">
      <p class="kicker" style="color:#cdb795;font-family:var(--font-display);text-transform:uppercase;letter-spacing:0.15em;font-size:0.85rem;margin-bottom:1rem;">The Definitive Guide</p>
      <h1 style="color:#fff;font-size:clamp(2rem,4vw,3.2rem);line-height:1.15;margin-bottom:1.25rem;">Above-Joist Deck Drainage Systems Explained</h1>
      <p style="font-size:1.1rem;line-height:1.7;color:#e6e9ee;">Above-joist deck drainage stops every drop of rain at the walking surface, before it ever reaches the joists. This guide explains how the system works, why builders specify it on new deck construction, and how it compares to below-joist retrofit drainage.</p>
    </div>
  </section>

  <!-- Article body -->
  <article class="section-pad bg-white">
    <div class="container" style="max-width:780px;font-size:1.05rem;line-height:1.75;color:var(--navy);">

      <h2 style="color:var(--navy);margin-top:0;">What is an above-joist deck drainage system?</h2>
      <p>An above-joist deck drainage system is a waterproofing assembly where the watertight layer is built into the deck surface itself. The drainage layer sits on top of the joists, between every deck board, instead of being hung underneath the framing as a separate accessory. When rain hits the deck, water never makes it past the surface. It is shed off the front and sides of the deck like water on the roof of a house.</p>
      <p>The AmeriDex system is the integrated above-joist deck drainage system. Cellular PVC deck boards lock onto the Dexerdry seal, an automotive-grade TPE gasket that ships between every board. The result is one continuous, finished surface that diverts 100% of the rain off the deck. The space under the deck stays dry, the joists stay dry, and the fasteners stay dry.</p>

      <h2 style="color:var(--navy);">Why above-joist drainage protects the structure</h2>
      <p>Standard wood and most composite deck boards leave a small gap between every board. That gap is intentional. It lets water drain off the surface so the boards do not stay wet. The trade-off is that every drop of rain that lands on the deck falls through those gaps onto the joists and beams below. Wood framing then dries slowly because it is shaded by the deck surface above. Over years, that wet-dry cycle is what causes joist rot, ledger failure, and fastener corrosion.</p>
      <p>An above-joist drainage system removes that wet-dry cycle from the framing entirely. The water-diverting seal between the boards closes the gap. Rain hits the deck, runs across the surface, and is shed off the edge, the same way water runs off a metal or shingle roof. The structure underneath never gets wet, so it never has to dry out, which is why the framing in an integrated above-joist deck stays sound for the life of the structure.</p>

      <h2 style="color:var(--navy);">The integrated AmeriDex system: board plus seal</h2>
      <p>An above-joist drainage system is only as good as the connection between the board and the seal. AmeriDex solves that with a tongue-and-groove board profile that locks mechanically onto the Dexerdry TPE seal. The boards do not just sit on top of a flashing tape or membrane. They engage the seal as part of the install, so there is no field-applied caulking or sealant to fail.</p>
      <ul style="padding-left:1.25rem;line-height:1.8;">
        <li><strong>Boards:</strong> Cellular PVC with a proprietary ASA cap. They will not rot, splinter, or warp, they hold a Class A flame spread rating under ASTM E84, and they ship in 12 ft, 16 ft, and 20 ft lengths in seven colors.</li>
        <li><strong>Seal:</strong> Dexerdry, an automotive-grade TPE (thermoplastic elastomer) gasket. The same material category used in car door and window seals. It is engineered to flex through years of thermal cycling without cracking or losing its watertight fit.</li>
        <li><strong>Substructure:</strong> Conventional 16 inches on-center joist layout for residential applications. No special sub-framing, sleepers, or pitch tray is required.</li>
        <li><strong>Fasteners:</strong> Starborn epoxy-coated screws or stainless screws and plugs.</li>
        <li><strong>Warranty:</strong> 25-Year Residential Limited / 10-Year Limited Commercial.</li>
      </ul>

      <h2 style="color:var(--navy);">Above-joist vs below-joist drainage at a glance</h2>
      <p>Above-joist and below-joist drainage solve the same homeowner goal, a dry space under the deck, with completely different engineering. The short version is that above-joist systems are built into a new deck from the joists up, and below-joist systems are added to an existing deck from underneath after the boards are already in place. <a href="above-joist-vs-below-joist-deck-drainage.html">The full comparison page</a> walks through framing impact, installation labor, long-term maintenance, and aesthetic finish in detail.</p>
      <p>The headline difference is what happens to the framing. Above-joist systems keep the joists dry. Below-joist systems do not. Below-joist drainage relies on a tray, panel, or membrane hung beneath the joists to catch water that has already fallen through the deck surface. The framing gets wet on every storm. Over the life of the deck, that is the difference between a structure that stays sound and a structure that has to be inspected for rot.</p>

      <h2 style="color:var(--navy);">Why above-joist drainage is the right call for new construction</h2>
      <p>If you are building a deck from scratch, you are already setting joists. Adding an integrated above-joist system at that stage is a single-trade install. The deck builder lays joists, drops in the seal, and screws down the boards. There is no second trade hanging panels underneath, no separate downspout system, no inspection ports cut into a finished tray ceiling. The system is also invisible from below because there is nothing hanging from the joists. Builders can finish the underside however the homeowner wants, including beadboard, T&G, drywall, or a fully open ceiling, because the framing is dry.</p>
      <p>For homeowners, the long-term math is straightforward. The space under the deck becomes a real, all-weather room. The structure does not need to be inspected for hidden water damage every spring. The under-deck ceiling stays clean and consistent because nothing is staining through from above. And because AmeriDex carries a 25-year residential limited warranty on the deck board system, the surface that does the waterproofing is also the surface that is warranted.</p>

      <h2 style="color:var(--navy);">When above-joist drainage is not the right fit</h2>
      <p>AmeriDex is for new deck construction only. The Dexerdry seal has to be placed between every board as the deck is built, so the system cannot be retrofitted onto a deck that already exists without first removing the existing boards. If you have a finished deck and you do not want to tear up the surface, a below-joist retrofit system is the only option. It will keep the patio space below dry, but the framing will get wet on every storm. That is the unavoidable trade-off of any retrofit drainage assembly.</p>

      <h2 style="color:var(--navy);">How to specify AmeriDex on a new build</h2>
      <p>Specifying AmeriDex on a new deck is a three step process. First, request <a href="samples-request.html">free samples</a> to see all seven PVC colors in person. Second, share your project dimensions through the <a href="get-a-free-quote.html">free quote form</a> so a regional dealer can return a written quote with board count, accessories, and lead time. Third, after install, <a href="warranty-registration.html">register the warranty</a> in minutes to activate the 25-year residential coverage. Builders working in commercial or multifamily applications should reach the AmeriDex team directly through the <a href="contact-us.html">contact page</a> for project takeoffs.</p>

    </div>
  </article>

  <!-- FAQ -->
  <section class="section-pad bg-cream" id="faq">
    <div class="container" style="max-width:880px;">
      <div class="section-head reveal">
        <h2 style="color:var(--navy)">Above-Joist Deck Drainage FAQ</h2>
        <p>The questions builders, dealers, and homeowners ask most about above-joist drainage systems.</p>
      </div>
      <div class="faq-list reveal">
        {faq_html}
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section class="section-pad bg-navy">
    <div class="container" style="text-align:center;">
      <h2 style="color:#fff;font-size:clamp(1.6rem,3vw,2.4rem);margin-bottom:1.5rem;">Specifying AmeriDex on a new deck?</h2>
      <div style="display:flex;gap:0.85rem;justify-content:center;flex-wrap:wrap;">
        <a class="btn btn-red btn-lg" href="get-a-free-quote.html">Start my project</a>
        <a class="btn btn-outline-white btn-lg" href="how-system-works.html">See How the System Works</a>
      </div>
    </div>
  </section>

</main>
'''
    return head(
        "Above-Joist Deck Drainage Systems: The Definitive Guide | AmeriDex",
        "Above-joist deck drainage stops rain at the surface so joists, beams, and the space below stay dry. Learn how integrated above-joist drainage works and why builders specify it on new construction.",
        canonical="above-joist-deck-drainage.html",
        keywords="above-joist deck drainage, above joist deck drainage system, integrated deck drainage, water diverting system for deck, dry space under deck, under deck drainage system, PVC deck drainage, AmeriDex, Dexerdry",
        og_type="article",
        extra_jsonld=[
            ABOVE_JOIST_ARTICLE_JSONLD,
            ABOVE_JOIST_FAQ_JSONLD,
            PRODUCT_JSONLD,
            breadcrumb_schema(("Home", ""), ("Above-Joist Deck Drainage", "above-joist-deck-drainage.html")),
        ],
    ) + header("above-joist-deck-drainage.html") + body + footer()


# ----------------------------------------------------------------------
# SEO COMPARISON PAGE: Above-Joist vs Below-Joist (no brand names)
# ----------------------------------------------------------------------
ABOVE_VS_BELOW_FAQ = [
    (
        "What is the difference between above-joist and below-joist deck drainage?",
        "Above-joist drainage stops water at the walking surface of the deck, before it ever reaches the joists. Below-joist drainage catches water after it has already passed through the deck boards, in a tray or panel hung underneath the framing. Above-joist drainage keeps the structure dry. Below-joist drainage only protects the patio space below.",
    ),
    (
        "Which type lasts longer?",
        "Above-joist systems generally last longer because the framing they sit on stays dry. Below-joist trays and panels tend to age faster because they are constantly wet, exposed to debris, and stained by water that has already run across the deck surface above.",
    ),
    (
        "Is below-joist drainage cheaper to install?",
        "Below-joist systems can have a lower up-front material cost, but the total installed cost is closer than it looks because they require a separate trade visit, additional flashing detail at the ledger, and a downspout system to carry collected water away. They are still the right answer when an existing deck cannot be torn up. For new construction, an integrated above-joist system is one trade and one install.",
    ),
    (
        "Can either system be installed on an existing deck?",
        "Below-joist systems are designed for retrofit and can be added under an existing deck. Integrated above-joist systems cannot be retrofitted because the water-diverting seal has to be placed between every board as the deck is built. They are specified on new construction.",
    ),
    (
        "Which system gives a better finished ceiling under the deck?",
        "Above-joist systems give the cleanest under-deck ceiling because nothing is hung from the joists. The framing is dry, so the homeowner can finish the underside however they want, including beadboard, drywall, or a fully open ceiling. Below-joist tray panels are visible from underneath and can stain over time.",
    ),
]

ABOVE_VS_BELOW_FAQ_JSONLD = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in ABOVE_VS_BELOW_FAQ
    ],
}

ABOVE_VS_BELOW_ARTICLE_JSONLD = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Above-Joist vs Below-Joist Deck Drainage: A Builder's Comparison",
    "description": (
        "A side-by-side comparison of above-joist and below-joist deck drainage "
        "systems for builders, dealers, and homeowners specifying a dry space "
        "under the deck."
    ),
    "image": f"{SITE_ORIGIN}/assets/img/og.jpg",
    "author": {"@type": "Organization", "name": "AmeriDex", "url": SITE_ORIGIN},
    "publisher": {"@id": f"{SITE_ORIGIN}/#organization"},
    "mainEntityOfPage": f"{SITE_ORIGIN}/above-joist-vs-below-joist-deck-drainage.html",
    "inLanguage": "en-US",
}


def page_above_joist_vs_below_joist():
    faq_html = "\n        ".join(
        f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>'
        for q, a in ABOVE_VS_BELOW_FAQ
    )
    body = f'''
<main id="main">

  <!-- Hero -->
  <section class="section-pad bg-navy" style="color:#fff;">
    <div class="container" style="max-width:880px;text-align:center;">
      <p class="kicker" style="color:#cdb795;font-family:var(--font-display);text-transform:uppercase;letter-spacing:0.15em;font-size:0.85rem;margin-bottom:1rem;">Builder Comparison</p>
      <h1 style="color:#fff;font-size:clamp(2rem,4vw,3.2rem);line-height:1.15;margin-bottom:1.25rem;">Above-Joist vs Below-Joist Deck Drainage</h1>
      <p style="font-size:1.1rem;line-height:1.7;color:#e6e9ee;">Two engineering approaches, one homeowner goal. Here is a head-to-head comparison of how above-joist and below-joist deck drainage systems are built, what they protect, and which one is right for new construction versus retrofit.</p>
    </div>
  </section>

  <!-- Intro -->
  <article class="section-pad bg-white">
    <div class="container" style="max-width:780px;font-size:1.05rem;line-height:1.75;color:var(--navy);">

      <h2 style="color:var(--navy);margin-top:0;">The core engineering difference</h2>
      <p>Every deck drainage system has the same goal: a dry space under the deck. The two ways to get there are fundamentally different.</p>
      <ul style="padding-left:1.25rem;line-height:1.8;">
        <li><strong>Above-joist drainage</strong> places the watertight layer at the walking surface of the deck. Water never reaches the framing. The system is integrated into the deck boards as the deck is built. <a href="above-joist-deck-drainage.html">Read the full above-joist drainage explainer</a>.</li>
        <li><strong>Below-joist drainage</strong> places the watertight layer beneath the framing as a tray, panel, or membrane assembly. Water runs through the deck boards, soaks the joists, and is collected below. The system is hung underneath an existing or new deck after the boards are in place.</li>
      </ul>
      <p>The first approach keeps the structure dry. The second approach keeps the patio space below dry while the framing gets wet on every storm. That single distinction drives most of the comparisons that follow.</p>

      <h2 style="color:var(--navy);">Side-by-side comparison</h2>
      <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:0.98rem;margin:1rem 0;">
          <thead>
            <tr style="background:var(--navy);color:#fff;">
              <th style="text-align:left;padding:0.7rem 0.9rem;border:1px solid var(--navy);">Attribute</th>
              <th style="text-align:left;padding:0.7rem 0.9rem;border:1px solid var(--navy);">Above-Joist (Integrated)</th>
              <th style="text-align:left;padding:0.7rem 0.9rem;border:1px solid var(--navy);">Below-Joist (Retrofit)</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;"><strong>Where the water stops</strong></td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">At the deck surface</td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">Below the joists</td></tr>
            <tr><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;"><strong>Joists stay dry</strong></td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">Yes</td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">No</td></tr>
            <tr><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;"><strong>Application</strong></td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">New construction only</td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">New or retrofit</td></tr>
            <tr><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;"><strong>Trades involved</strong></td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">One: deck builder</td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">Two: deck builder plus drainage installer</td></tr>
            <tr><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;"><strong>Visible from below</strong></td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">No, framing is dry and can be finished any way</td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">Yes, tray or panel ceiling is part of the look</td></tr>
            <tr><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;"><strong>Long-term maintenance</strong></td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">Surface cleaning only</td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">Tray cleanout, debris removal, periodic flashing inspection</td></tr>
            <tr><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;"><strong>Risk of joist rot over time</strong></td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">Removed by design</td><td style="padding:0.7rem 0.9rem;border:1px solid #d8dde3;">Same as a standard wet-framed deck</td></tr>
          </tbody>
        </table>
      </div>

      <h2 style="color:var(--navy);">When above-joist wins</h2>
      <p>If the deck is being built from scratch, an integrated above-joist drainage system is the right call. The framing stays dry for the life of the structure. The install is a single trade. The under-deck ceiling can be finished any way the homeowner wants because there is nothing hanging from the joists. And the surface that does the waterproofing is also the surface that carries the deck warranty, so the homeowner is not splitting coverage between a board manufacturer and a separate drainage manufacturer.</p>

      <h2 style="color:var(--navy);">When below-joist still makes sense</h2>
      <p>A below-joist retrofit system is the right answer when the deck already exists and the homeowner does not want to tear up the surface to rebuild it. It will keep the patio space below dry on rainy days. The trade-off is that the framing will continue to get wet on every storm, which is the same condition any standard deck has had since the day it was built. The retrofit system simply adds a dry zone underneath.</p>

      <h2 style="color:var(--navy);">How AmeriDex fits in</h2>
      <p>AmeriDex is the integrated above-joist deck drainage system. Cellular PVC deck boards lock onto the Dexerdry TPE seal so 100% of the rain is diverted off the deck and the framing stays dry. It is engineered for new construction with a conventional 16 inches on-center joist layout, no special sub-framing, and a 25-year residential limited warranty. <a href="how-system-works.html">Walk through how the system works step by step</a>, <a href="samples-request.html">request free samples in all seven colors</a>, or <a href="get-a-free-quote.html">submit your project for a free quote</a>.</p>

    </div>
  </article>

  <!-- FAQ -->
  <section class="section-pad bg-cream" id="faq">
    <div class="container" style="max-width:880px;">
      <div class="section-head reveal">
        <h2 style="color:var(--navy)">Above-Joist vs Below-Joist FAQ</h2>
      </div>
      <div class="faq-list reveal">
        {faq_html}
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section class="section-pad bg-navy">
    <div class="container" style="text-align:center;">
      <h2 style="color:#fff;font-size:clamp(1.6rem,3vw,2.4rem);margin-bottom:1.5rem;">Building a new deck?</h2>
      <div style="display:flex;gap:0.85rem;justify-content:center;flex-wrap:wrap;">
        <a class="btn btn-red btn-lg" href="get-a-free-quote.html">Start my project</a>
        <a class="btn btn-outline-white btn-lg" href="above-joist-deck-drainage.html">Read the Above-Joist Guide</a>
      </div>
    </div>
  </section>

</main>
'''
    return head(
        "Above-Joist vs Below-Joist Deck Drainage: Builder's Comparison | AmeriDex",
        "Compare above-joist and below-joist deck drainage systems side by side: how each one is built, which keeps your joists dry, and which is right for new construction vs retrofit.",
        canonical="above-joist-vs-below-joist-deck-drainage.html",
        keywords="above-joist vs below-joist deck drainage, above joist vs below joist drainage, deck drainage comparison, integrated deck drainage vs retrofit, under deck drainage system, dry space under deck",
        og_type="article",
        extra_jsonld=[
            ABOVE_VS_BELOW_ARTICLE_JSONLD,
            ABOVE_VS_BELOW_FAQ_JSONLD,
            breadcrumb_schema(("Home", ""), ("Above-Joist vs Below-Joist Deck Drainage", "above-joist-vs-below-joist-deck-drainage.html")),
        ],
    ) + header("above-joist-vs-below-joist-deck-drainage.html") + body + footer()


# ----------------------------------------------------------------------
# ABOUT PAGE: brand entity + engineering origin
# ----------------------------------------------------------------------
ABOUT_ARTICLE_JSONLD = {
    "@context": "https://schema.org",
    "@type": "AboutPage",
    "name": "About AmeriDex",
    "description": (
        "AmeriDex is an American-made above-joist deck drainage system from "
        "A & M Building Products, manufactured in Linden, New Jersey. "
        "Co-founded by John Ardolina and Jim Murphy."
    ),
    "url": f"{SITE_ORIGIN}/about.html",
    "about": {"@id": f"{SITE_ORIGIN}/#organization"},
    "mainEntity": {"@id": f"{SITE_ORIGIN}/#organization"},
    "inLanguage": "en-US",
}


def page_about():
    body = f'''
<main id="main">

  <!-- Hero -->
  <section class="section-pad bg-navy" style="color:#fff;">
    <div class="container" style="max-width:880px;text-align:center;">
      <p class="kicker" style="color:#cdb795;font-family:var(--font-display);text-transform:uppercase;letter-spacing:0.15em;font-size:0.85rem;margin-bottom:1rem;">About AmeriDex</p>
      <h1 style="color:#fff;font-size:clamp(2rem,4vw,3.2rem);line-height:1.15;margin-bottom:1.25rem;">An American Deck System, Engineered Around a Patented Seal.</h1>
      <p style="font-size:1.1rem;line-height:1.7;color:#e6e9ee;">AmeriDex is the integrated above-joist deck drainage system from A &amp; M Building Products. Cellular PVC deck boards are manufactured in Linden, New Jersey and lock onto the patented Dexerdry seal so 100% of the rain is diverted off the deck.</p>
    </div>
  </section>

  <!-- Story body -->
  <article class="section-pad bg-white">
    <div class="container about-body" style="max-width:780px;font-size:1.05rem;line-height:1.75;color:var(--navy);">

      <style>
        .about-body h2 {{
          color: var(--navy);
          font-size: clamp(1.5rem, 2.4vw, 1.95rem);
          line-height: 1.25;
          font-weight: 700;
          margin: 3rem 0 1rem;
          letter-spacing: -0.01em;
        }}
        .about-body h2:first-child {{ margin-top: 0; }}
        .about-body h2::after {{
          content: "";
          display: block;
          width: 56px;
          height: 3px;
          background: var(--red);
          margin-top: 0.65rem;
        }}
        .about-body p {{ margin: 0 0 1.15rem; }}
        .about-body p:last-child {{ margin-bottom: 0; }}
        .about-body ul {{ margin: 1.25rem 0 0; padding-left: 1.25rem; line-height: 1.8; }}
        .about-body ul li {{ margin-bottom: 0.55rem; }}
        .about-body .founders-grid {{
          display: grid;
          grid-template-columns: 1fr;
          gap: 1.5rem;
          margin: 0.75rem 0 0.5rem;
        }}
        .about-body .founders-grid > div {{
          border-left: 4px solid var(--red);
          padding: 0.4rem 0 0.4rem 1.1rem;
        }}
        .about-body .founders-grid h3 {{
          color: var(--navy);
          margin: 0 0 0.45rem;
          font-size: 1.2rem;
          font-weight: 700;
        }}
        .about-body .founders-grid p {{ margin: 0; }}
      </style>

      <h2>From the jobsite to a patented system</h2>
      <p>AmeriDex started on a jobsite. John Ardolina, a carpenter by trade, spent years building decks and watching the same problem repeat itself. Every storm, water ran through the gaps in the deck boards and soaked the joists below. The framing slowly rotted, the fasteners slowly corroded, and the customer never saw any of it until the deck was already failing. The fix needed to happen at the surface, not underneath. That is the engineering insight that became Dexerdry, the patented above-joist water-diverting seal that sits between every deck board.</p>
      <p>AmeriDex is the next step. It pairs that seal with a purpose-built cellular PVC deck board so the entire system, board and seal, ships and installs as one assembly. Two companies, one engineered system, one warranty.</p>

      <h2>The seal: Dexerdry, Inc.</h2>
      <p>John founded Dexerdry, Inc. in 2014 to commercialize the seal he had been developing on the jobsite. Dexerdry uses an above-joist water-diverting gasket made of automotive-grade TPE (thermoplastic elastomer), the same material category used in car door and window seals. Dexerdry, Inc. holds <a href="https://patents.google.com/patent/US7028437B2/en" target="_blank" rel="noopener">U.S. Patent 7,028,437</a> for the above-joist, integrated deck-gutter system. The seal ships on a roll, sits between every deck board, and locks the watertight layer at the deck surface itself, before water can ever reach the framing below.</p>

      <h2>The board and the brand: A &amp; M Building Products and AmeriDex</h2>
      <p>A &amp; M Building Products was founded in 2023 to bring the seal and a purpose-built deck board to market under one brand. That brand is AmeriDex. The boards are premium cellular PVC with a proprietary ASA cap, manufactured in Linden, New Jersey, and they are profiled to lock mechanically onto the Dexerdry seal as the deck is built. The headquarters and warehouse operations are based at 1129A Industrial Parkway in Brick, New Jersey.</p>
      <p>The result is a single integrated deck system that ships as one product, installs as one trade, and is warranted as one assembly. There is no separate drainage manufacturer, no field-applied sealant, no second trade hanging trays underneath, and no split warranty.</p>

      <h2>The founders</h2>
      <div class="founders-grid">
        <div>
          <h3>John Ardolina, Co-Founder</h3>
          <p>John is a carpenter by trade. He spent years on jobsites watching deck framing get soaked on every storm and built Dexerdry, Inc. in 2014 to solve it. Dexerdry holds the patent on the above-joist water-diverting seal that gives the AmeriDex deck its dry-framing performance. John brings the seal IP, the material science work behind the TPE gasket, and more than a decade of operating history at Dexerdry, Inc. into AmeriDex.</p>
        </div>
        <div>
          <h3>Jim Murphy, Co-Founder</h3>
          <p>Jim leads the manufacturing side of the business and brings extensive experience in cellular PVC and building products production. He runs the AmeriDex deck board plant in Linden, New Jersey, where the boards are extruded, capped, profiled to mate with the Dexerdry seal, and packaged for dealers and builders.</p>
        </div>
      </div>

      <h2>Made in the USA</h2>
      <p>Every AmeriDex deck board is manufactured in Linden, New Jersey. The Dexerdry seal that ships between every board is also produced in the USA. Headquarters, sales, and warehousing operate out of Brick, New Jersey. The system is engineered, manufactured, and supported entirely on-shore.</p>

      <h2>Built for new construction, warranted as one system</h2>
      <p>AmeriDex is engineered for new deck construction only. The Dexerdry seal has to be installed between every board as the deck is built, so the system cannot be retrofitted on an existing deck without removing the existing surface. For new construction, that constraint is what unlocks the rest of the value: dry framing for the life of the structure, a single-trade install on conventional 16 inches on-center joists, and a 25-Year Residential Limited / 10-Year Limited Commercial warranty on the integrated board and seal system.</p>

      <h2>Where to take it next</h2>
      <ul>
        <li><a href="how-system-works.html">See how the AmeriDex system works</a> in technical detail, including the cross-section, install sequence, and FAQ.</li>
        <li><a href="above-joist-deck-drainage.html">Read the above-joist deck drainage explainer</a> for the engineering reasoning behind keeping the water at the surface.</li>
        <li><a href="samples-request.html">Request free samples</a> to see all seven cellular PVC colors in person.</li>
        <li><a href="get-a-free-quote.html">Submit a project for a free quote</a> if you are specifying AmeriDex on a new deck.</li>
        <li><a href="contact-us.html">Contact the team</a> directly for commercial, multifamily, or dealer inquiries.</li>
      </ul>

    </div>
  </article>

  <!-- CTA -->
  <section class="section-pad bg-navy">
    <div class="container" style="text-align:center;">
      <h2 style="color:#fff;font-size:clamp(1.6rem,3vw,2.4rem);margin-bottom:1.5rem;">Want AmeriDex on your next deck?</h2>
      <div style="display:flex;gap:0.85rem;justify-content:center;flex-wrap:wrap;">
        <a class="btn btn-red btn-lg" href="get-a-free-quote.html">Start my project</a>
        <a class="btn btn-outline-white btn-lg" href="samples-request.html">Request samples</a>
      </div>
    </div>
  </section>

</main>
'''
    return head(
        "About AmeriDex | Made in the USA Above-Joist Deck Drainage",
        "AmeriDex is the integrated above-joist deck drainage system from A & M Building Products, made in Linden, NJ. Co-founded by John Ardolina (Dexerdry, Inc.) and Jim Murphy (manufacturing).",
        canonical="about.html",
        keywords="about AmeriDex, AmeriDex company, A & M Building Products, Dexerdry Inc, John Ardolina, Jim Murphy, made in USA deck system, Linden NJ deck manufacturer, Brick NJ",
        og_type="article",
        extra_jsonld=[
            ABOUT_ARTICLE_JSONLD,
            FOUNDER_ARDOLINA,
            FOUNDER_MURPHY,
            breadcrumb_schema(("Home", ""), ("About", "about.html")),
        ],
    ) + header("about.html") + body + footer()


# ----------------------------------------------------------------------
# WRITE
# ----------------------------------------------------------------------
PAGES = {
    "index.html":                                       page_index,
    "how-system-works.html":                            page_how_it_works,
    "gallery.html":                                     page_gallery,
    "get-a-free-quote.html":                            page_quote,
    "contact-us.html":                                  page_contact,
    "samples-request.html":                             page_samples,
    "warranty-registration.html":                       page_warranty,
    "about.html":                                       page_about,
    "above-joist-deck-drainage.html":                   page_above_joist_drainage,
    "above-joist-vs-below-joist-deck-drainage.html":    page_above_joist_vs_below_joist,
}


def main():
    for fname, fn in PAGES.items():
        out = ROOT / fname
        out.write_text(fn(), encoding="utf-8")
        print(f"wrote {fname} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
