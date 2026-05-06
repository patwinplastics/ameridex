/* ==========================================================================
   AmeriDex Dealer Routing
   --------------------------------------------------------------------------
   One file owns:
     1) loading data/dealers.json
     2) ZIP-to-dealer matching (prefix first, radius fallback)
     3) reading/writing the ameridex_dealer cookie
     4) painting the sticky "you're shopping with <dealer>" banner
     5) rewriting the quote/contact CTAs and stamping hidden form fields
     6) URL parameter capture (?dealer=<slug>) from co-branded landing pages

   Treat dealers.json as the only place to add/edit a dealer. No code changes.
   ========================================================================== */
(function () {
  'use strict';

  var DEALERS_URL = '/data/dealers.json';
  var COOKIE_NAME = 'ameridex_dealer';
  var COOKIE_DAYS = 90;
  var STORAGE_KEY = 'ameridex_dealer_cache';

  // ---------- cookie helpers ----------
  function setCookie(name, value, days) {
    var expires = '';
    if (days) {
      var d = new Date();
      d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = '; expires=' + d.toUTCString();
    }
    document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/; SameSite=Lax';
  }
  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[2]) : null;
  }
  function clearCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
  }

  // ---------- data load ----------
  var dealersPromise = null;
  function loadDealers() {
    if (dealersPromise) return dealersPromise;
    dealersPromise = fetch(DEALERS_URL, { credentials: 'same-origin' })
      .then(function (r) { return r.ok ? r.json() : { dealers: [] }; })
      .catch(function () { return { dealers: [] }; });
    return dealersPromise;
  }

  function findDealerBySlug(data, slug) {
    if (!slug) return null;
    var list = (data && data.dealers) || [];
    for (var i = 0; i < list.length; i++) {
      if (list[i].slug === slug) return list[i];
    }
    return null;
  }

  // ---------- ZIP match ----------
  // Primary path: 3-digit ZIP prefix lookup against each dealer's zip_prefixes.
  // Because territories are exclusive, the first prefix match wins.
  function matchByZip(data, rawZip) {
    var zip = String(rawZip || '').replace(/[^0-9]/g, '').slice(0, 5);
    if (zip.length < 3) return null;
    var prefix = zip.slice(0, 3);
    var list = (data && data.dealers) || [];
    for (var i = 0; i < list.length; i++) {
      var d = list[i];
      if (d.zip_prefixes && d.zip_prefixes.indexOf(prefix) !== -1) return d;
    }
    return null;
  }

  // ---------- public API ----------
  var AD = window.AmeriDexDealers = {
    load: loadDealers,
    matchByZip: function (zip) { return loadDealers().then(function (d) { return matchByZip(d, zip); }); },
    getActiveSlug: function () { return getCookie(COOKIE_NAME); },
    getActiveDealer: function () {
      var slug = getCookie(COOKIE_NAME);
      if (!slug) return Promise.resolve(null);
      return loadDealers().then(function (d) { return findDealerBySlug(d, slug); });
    },
    setActiveDealer: function (slug) {
      if (!slug) { clearCookie(COOKIE_NAME); try { sessionStorage.removeItem(STORAGE_KEY); } catch (e) {} return; }
      setCookie(COOKIE_NAME, slug, COOKIE_DAYS);
    },
    clear: function () {
      clearCookie(COOKIE_NAME);
      try { sessionStorage.removeItem(STORAGE_KEY); } catch (e) {}
    }
  };

  // ---------- URL capture ----------
  // Any page can be visited as ?dealer=<slug> and we'll tag the session.
  // Used by co-branded landing pages and any UTM-style links the dealer shares.
  function captureFromUrl() {
    var qs = new URLSearchParams(window.location.search);
    var slug = qs.get('dealer');
    if (slug) AD.setActiveDealer(slug);
  }

  // ---------- sticky banner ----------
  // Shows "Shopping with Guy C Lee Building Supply (Mt. Pleasant, SC) \u00b7 Change"
  // Once a dealer is matched, this rides along on every page.
  function paintBanner(dealer) {
    if (!dealer) return;
    if (document.getElementById('ad-dealer-banner')) return;
    var bar = document.createElement('div');
    bar.id = 'ad-dealer-banner';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', 'Active dealer');
    bar.innerHTML =
      '<div class="ad-dealer-banner-inner">' +
        '<span class="ad-dealer-banner-label">Shopping with</span> ' +
        '<strong>' + escapeHtml(dealer.name) + '</strong> ' +
        '<span class="ad-dealer-banner-loc">' + escapeHtml(dealer.location_label) + '</span>' +
        '<a class="ad-dealer-banner-action" href="/dealers/' + encodeURIComponent(dealer.slug) + '.html">View dealer</a>' +
        '<button type="button" class="ad-dealer-banner-clear" aria-label="Clear selected dealer">Change</button>' +
      '</div>';
    document.body.insertBefore(bar, document.body.firstChild);
    bar.querySelector('.ad-dealer-banner-clear').addEventListener('click', function () {
      AD.clear();
      bar.parentNode.removeChild(bar);
      // Optional: bounce them to where-to-buy so they can pick again.
      window.location.href = '/where-to-buy.html';
    });
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  // ---------- form rewrite ----------
  // POLICY: All form submissions go to AmeriDex only. AmeriDex manually pushes
  // each lead to the matched dealer. The dealer's email is NOT used for routing
  // and is intentionally never stamped onto the form. The dealer's phone and
  // website (url_external) remain visible on dealer cards and landing pages so
  // visitors can self-serve those channels if they want.
  //
  // What we DO stamp on every form when a dealer is active:
  //   - routed_to_dealer       (slug, e.g. "guy-c-lee-mt-pleasant")
  //   - routed_to_dealer_name  (display name + location)
  //   - _subject prefix        ("[<slug>] ...") so the AmeriDex inbox is filterable
  //
  // That gives AmeriDex everything needed to know which dealer to forward to,
  // without copying the dealer on the raw inbound message.
  function stampForms(dealer) {
    if (!dealer) return;
    var forms = document.querySelectorAll('form[action*="formspree"]');
    forms.forEach(function (form) {
      ensureHidden(form, 'routed_to_dealer', dealer.slug);
      ensureHidden(form, 'routed_to_dealer_name', dealer.name + ' \u2014 ' + dealer.location_label);
      // Subject prefix: makes the AmeriDex inbox instantly filterable per dealer.
      var existingSubject = form.querySelector('input[name="_subject"]');
      var prefix = '[' + dealer.slug + '] ';
      if (existingSubject) {
        if (existingSubject.value.indexOf(prefix) !== 0) {
          existingSubject.value = prefix + existingSubject.value;
        }
      } else {
        ensureHidden(form, '_subject', prefix + (document.title || 'AmeriDex submission'));
      }
      // Defensive cleanup: if a previous version of this script stamped a CC or
      // dealer email field onto the form, remove them. AmeriDex is the only
      // recipient by policy.
      var stale = form.querySelectorAll('input[name="_cc"], input[name="routed_to_dealer_email"]');
      stale.forEach(function (n) { n.parentNode.removeChild(n); });
    });

    // Visitor-facing note above forms. Honest framing: AmeriDex receives the
    // request and connects them with their local dealer. (We don't promise the
    // dealer is copied, because they're not.)
    var noteHosts = document.querySelectorAll('[data-dealer-note]');
    noteHosts.forEach(function (host) {
      host.style.display = '';
      host.innerHTML =
        'AmeriDex will receive your request and connect you with <strong>' + escapeHtml(dealer.name) + '</strong> ' +
        '(' + escapeHtml(dealer.location_label) + '). ' +
        '<a href="/where-to-buy.html">Use a different dealer</a>.';
    });
  }

  function ensureHidden(form, name, value) {
    var el = form.querySelector('input[name="' + cssEsc(name) + '"][type="hidden"]');
    if (!el) {
      el = document.createElement('input');
      el.type = 'hidden';
      el.name = name;
      form.appendChild(el);
    }
    el.value = value;
  }
  function cssEsc(s) { return String(s).replace(/"/g, '\\"'); }

  // ---------- nav rewrite ----------
  // When a dealer is active, the "Get a Free Quote" button on every page becomes
  // "Quote from <Dealer>" so the visitor never feels handed off to a faceless brand.
  function relabelNavCtas(dealer) {
    if (!dealer) return;
    // Only relabel CTAs that explicitly opt in via data-dealer-cta. This keeps
    // the persistent header/nav stable (predictable widths, screen readers) and
    // lets pages choose where the personalized label appears.
    document.querySelectorAll('[data-dealer-cta]').forEach(function (el) {
      var city = dealer.location_label.split(',')[0].trim();
      el.textContent = 'Quote from ' + city;
      el.setAttribute('aria-label', 'Get a quote from ' + dealer.name + ' (' + dealer.location_label + ')');
    });
  }

  // ---------- boot ----------
  document.addEventListener('DOMContentLoaded', function () {
    captureFromUrl();
    AD.getActiveDealer().then(function (dealer) {
      if (!dealer) return;
      paintBanner(dealer);
      stampForms(dealer);
      relabelNavCtas(dealer);
    });
  });
})();
