/* ==========================================================================
   AmeriDex Dealer Routing + "My Store" Picker
   --------------------------------------------------------------------------
   This file owns:
     1) loading data/dealers.json
     2) ZIP-to-dealer matching (3-digit prefix; territories are exclusive)
     3) reading/writing the ameridex_dealer cookie (the explicit "My Store" pick)
     4) IP-based ZIP detection + soft "Suggested store" UX for un-picked visitors
     5) rendering the persistent header chip + popover (Change / Clear / Visit)
     6) painting the first-visit sticky banner
     7) stamping hidden form fields so the AmeriDex inbox can attribute the lead
     8) URL parameter capture (?dealer=<slug>) for co-branded landing pages

   Cookie layers:
     ameridex_dealer            (90d) explicit pick, slug
     ameridex_dealer_suggested  (session) suggested-but-unconfirmed slug
     ameridex_dealer_dismissed  (24h)  user said "not now" to suggestion
     ameridex_zip_cache         (24h)  cached IP-detected ZIP

   Form-routing policy (per business decision):
     ALL form submissions go to AmeriDex only. AmeriDex manually forwards to
     the dealer. We do NOT _cc the dealer and we do NOT stamp the dealer's
     email anywhere. The dealer's email is INTERNAL to dealers.json.

   Edit dealers.json to add/edit dealers. No code changes required.
   ========================================================================== */
(function () {
  'use strict';

  var DEALERS_URL = '/data/dealers.json';
  var COOKIE_PICKED = 'ameridex_dealer';
  var COOKIE_DISMISSED = 'ameridex_dealer_dismissed';
  var COOKIE_ZIP = 'ameridex_zip_cache';
  var COOKIE_PICKED_DAYS = 90;
  var COOKIE_DISMISSED_HOURS = 24;
  var COOKIE_ZIP_HOURS = 24;
  var BANNER_DISMISS_KEY = 'ameridex_banner_dismissed';
  var GEO_URL = 'https://ipapi.co/json/';
  var GEO_TIMEOUT_MS = 2500;

  // ---------- cookie helpers ----------
  function setCookie(name, value, opts) {
    opts = opts || {};
    var expires = '';
    var ms = 0;
    if (opts.days) ms = opts.days * 24 * 60 * 60 * 1000;
    else if (opts.hours) ms = opts.hours * 60 * 60 * 1000;
    if (ms) {
      var d = new Date();
      d.setTime(d.getTime() + ms);
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

  // ---------- escape ----------
  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  function cityOnly(label) {
    return String(label || '').split(',')[0].trim();
  }

  // ---------- IP geolocation ----------
  // Calls ipapi.co/json/ to get a US ZIP. Returns Promise<string|null>.
  // Heavy defensive coding: any failure returns null and the UI silently
  // degrades to "no suggestion" rather than guessing or showing errors.
  // Result is cached for 24h so repeat visits don't spam the service.
  function detectZip() {
    var cached = getCookie(COOKIE_ZIP);
    if (cached !== null) return Promise.resolve(cached || null);

    return new Promise(function (resolve) {
      var done = false;
      var timer = setTimeout(function () { if (!done) { done = true; resolve(null); } }, GEO_TIMEOUT_MS);

      fetch(GEO_URL, { credentials: 'omit' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) {
          if (done) return;
          done = true; clearTimeout(timer);
          var zip = '';
          if (j && j.country_code === 'US' && j.postal) {
            zip = String(j.postal).replace(/[^0-9]/g, '').slice(0, 5);
          }
          // Cache even an empty result so we don't retry every page (24h).
          setCookie(COOKIE_ZIP, zip, { hours: COOKIE_ZIP_HOURS });
          resolve(zip || null);
        })
        .catch(function () {
          if (done) return;
          done = true; clearTimeout(timer);
          // Don't cache failures; let the next page try again.
          resolve(null);
        });
    });
  }

  // ---------- public API ----------
  var listeners = [];
  function emitChange() { listeners.forEach(function (fn) { try { fn(); } catch (e) {} }); }

  var AD = window.AmeriDexDealers = {
    load: loadDealers,
    matchByZip: function (zip) { return loadDealers().then(function (d) { return matchByZip(d, zip); }); },
    getActiveSlug: function () { return getCookie(COOKIE_PICKED); },
    getActiveDealer: function () {
      var slug = getCookie(COOKIE_PICKED);
      if (!slug) return Promise.resolve(null);
      return loadDealers().then(function (d) { return findDealerBySlug(d, slug); });
    },
    setActiveDealer: function (slug) {
      if (!slug) { clearCookie(COOKIE_PICKED); emitChange(); return; }
      setCookie(COOKIE_PICKED, slug, { days: COOKIE_PICKED_DAYS });
      // A confirmed pick clears any prior dismissal and resurfaces the banner.
      clearCookie(COOKIE_DISMISSED);
      try { sessionStorage.removeItem(BANNER_DISMISS_KEY); } catch (e) {}
      emitChange();
    },
    clear: function () {
      clearCookie(COOKIE_PICKED);
      try { sessionStorage.removeItem(BANNER_DISMISS_KEY); } catch (e) {}
      emitChange();
    },
    dismissSuggestion: function () {
      setCookie(COOKIE_DISMISSED, '1', { hours: COOKIE_DISMISSED_HOURS });
      emitChange();
    },
    onChange: function (fn) { listeners.push(fn); }
  };

  // ---------- URL capture ----------
  // ?dealer=<slug> sets the dealer explicitly (visitor came from a co-branded
  // link the dealer shared, so the affiliation is intentional).
  function captureFromUrl() {
    try {
      var qs = new URLSearchParams(window.location.search);
      var slug = qs.get('dealer');
      if (slug) AD.setActiveDealer(slug);
    } catch (e) {}
  }

  // ==========================================================================
  // Header chip — TWO STATES
  //   confirmed  : solid red pin, "My Store: <City>", popover with full menu
  //   suggested  : dotted outline, "Suggested: <City>", popover with Set / Not now
  // ==========================================================================
  function paintChip(state, dealer) {
    var existing = document.getElementById('ad-store-chip');
    if (existing) existing.parentNode.removeChild(existing);
    if (!dealer) return;

    var header = document.querySelector('.site-header .site-header-inner');
    if (!header) return;

    var isSuggested = state === 'suggested';
    var pinSvg =
      '<svg viewBox="0 0 16 20" width="12" height="15" fill="currentColor" aria-hidden="true">' +
        '<path d="M8 0C3.6 0 0 3.4 0 7.6 0 13.3 8 20 8 20s8-6.7 8-12.4C16 3.4 12.4 0 8 0zm0 10.4a2.8 2.8 0 110-5.6 2.8 2.8 0 010 5.6z"/>' +
      '</svg>';
    var caretSvg = '<svg viewBox="0 0 10 6" width="10" height="6" fill="currentColor" aria-hidden="true"><path d="M5 6L0 0h10z"/></svg>';

    var wrap = document.createElement('div');
    wrap.id = 'ad-store-chip';
    wrap.className = 'ad-store-chip' + (isSuggested ? ' ad-store-chip--suggested' : '');

    var eyebrow = isSuggested ? 'Nearest Dealer' : 'My Store';
    var ariaLabel = isSuggested
      ? 'Nearest dealer: ' + dealer.name + '. Click to set as your store.'
      : 'My store: ' + dealer.name + '. Click to manage.';

    var popActions;
    if (isSuggested) {
      popActions =
        '<button type="button" class="ad-store-chip-set">Set as my store</button>' +
        '<a class="ad-store-chip-link" href="/dealers/' + encodeURIComponent(dealer.slug) + '.html">View dealer page</a>' +
        '<a class="ad-store-chip-link" href="/where-to-buy.html">Pick a different dealer</a>' +
        '<button type="button" class="ad-store-chip-dismiss">Not now</button>';
    } else {
      popActions =
        '<a class="ad-store-chip-link" href="/dealers/' + encodeURIComponent(dealer.slug) + '.html">View dealer page</a>' +
        (dealer.url_external ? '<a class="ad-store-chip-link" href="' + dealer.url_external + '" target="_blank" rel="noopener">Visit dealer site</a>' : '') +
        '<a class="ad-store-chip-link" href="/where-to-buy.html">Change store</a>' +
        '<button type="button" class="ad-store-chip-clear">Clear my store</button>';
    }

    wrap.innerHTML =
      '<button type="button" class="ad-store-chip-button" aria-haspopup="true" aria-expanded="false" aria-label="' + escapeHtml(ariaLabel) + '">' +
        '<span class="ad-store-chip-pin" aria-hidden="true">' + pinSvg + '</span>' +
        '<span class="ad-store-chip-label">' +
          '<span class="ad-store-chip-eyebrow">' + eyebrow + '</span>' +
          '<span class="ad-store-chip-name">' + escapeHtml(cityOnly(dealer.location_label)) + '</span>' +
        '</span>' +
        '<span class="ad-store-chip-caret" aria-hidden="true">' + caretSvg + '</span>' +
      '</button>' +
      '<div class="ad-store-chip-pop" role="dialog" aria-label="Store details" hidden>' +
        '<p class="ad-store-chip-pop-name">' + escapeHtml(dealer.name) + '</p>' +
        '<p class="ad-store-chip-pop-loc">' + escapeHtml(dealer.location_label) + '</p>' +
        '<p class="ad-store-chip-pop-phone"><a href="tel:' + dealer.phone.replace(/[^0-9]/g, '') + '">' + escapeHtml(dealer.phone) + '</a></p>' +
        '<div class="ad-store-chip-pop-actions">' + popActions + '</div>' +
      '</div>';

    var cta = header.querySelector('.site-header-cta');
    if (cta) header.insertBefore(wrap, cta); else header.appendChild(wrap);

    var btn = wrap.querySelector('.ad-store-chip-button');
    var pop = wrap.querySelector('.ad-store-chip-pop');

    function closePop() {
      pop.hidden = true;
      btn.setAttribute('aria-expanded', 'false');
      document.removeEventListener('click', onDocClick, true);
      document.removeEventListener('keydown', onKey, true);
    }
    function openPop() {
      pop.hidden = false;
      btn.setAttribute('aria-expanded', 'true');
      document.addEventListener('click', onDocClick, true);
      document.addEventListener('keydown', onKey, true);
    }
    function onDocClick(e) { if (!wrap.contains(e.target)) closePop(); }
    function onKey(e) { if (e.key === 'Escape') { closePop(); btn.focus(); } }

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (pop.hidden) openPop(); else closePop();
    });

    var setBtn = wrap.querySelector('.ad-store-chip-set');
    if (setBtn) setBtn.addEventListener('click', function () {
      AD.setActiveDealer(dealer.slug);
      closePop();
    });

    var dismissBtn = wrap.querySelector('.ad-store-chip-dismiss');
    if (dismissBtn) dismissBtn.addEventListener('click', function () {
      AD.dismissSuggestion();
      closePop();
    });

    var clearBtn = wrap.querySelector('.ad-store-chip-clear');
    if (clearBtn) clearBtn.addEventListener('click', function () {
      AD.clear();
      closePop();
      if (window.location.pathname.indexOf('where-to-buy') === -1) {
        window.location.href = '/where-to-buy.html';
      } else {
        window.location.reload();
      }
    });
  }

  // ==========================================================================
  // Banner — confirmed-pick state OR suggestion state
  // First-visit only; sessionStorage suppresses repeats within the session.
  // ==========================================================================
  function paintBanner(state, dealer) {
    var existing = document.getElementById('ad-dealer-banner');
    if (existing) existing.parentNode.removeChild(existing);
    if (!dealer) return;
    try { if (sessionStorage.getItem(BANNER_DISMISS_KEY) === '1') return; } catch (e) {}

    var bar = document.createElement('div');
    bar.id = 'ad-dealer-banner';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', 'Local dealer');

    if (state === 'suggested') {
      bar.className = 'ad-dealer-banner-suggested';
      bar.innerHTML =
        '<div class="ad-dealer-banner-inner">' +
          '<span class="ad-dealer-banner-loc">Nearest dealer:</span> ' +
          '<strong>' + escapeHtml(dealer.name) + '</strong> ' +
          '<span class="ad-dealer-banner-loc">(' + escapeHtml(dealer.location_label) + ')</span>' +
          '<button type="button" class="ad-dealer-banner-set">Set as my store</button>' +
          '<button type="button" class="ad-dealer-banner-dismiss" aria-label="Dismiss">&times;</button>' +
        '</div>';
    } else {
      bar.innerHTML =
        '<div class="ad-dealer-banner-inner">' +
          '<strong>' + escapeHtml(dealer.name) + '</strong> ' +
          '<span class="ad-dealer-banner-loc">is set as your store (' + escapeHtml(dealer.location_label) + ')</span>' +
          '<a class="ad-dealer-banner-action" href="/where-to-buy.html">Change</a>' +
          '<button type="button" class="ad-dealer-banner-dismiss" aria-label="Dismiss">&times;</button>' +
        '</div>';
    }

    document.body.insertBefore(bar, document.body.firstChild);

    var setBtn = bar.querySelector('.ad-dealer-banner-set');
    if (setBtn) setBtn.addEventListener('click', function () {
      AD.setActiveDealer(dealer.slug);
    });

    bar.querySelector('.ad-dealer-banner-dismiss').addEventListener('click', function () {
      try { sessionStorage.setItem(BANNER_DISMISS_KEY, '1'); } catch (e) {}
      if (state === 'suggested') AD.dismissSuggestion();
      bar.parentNode.removeChild(bar);
    });
  }

  // ==========================================================================
  // Form stamping (AmeriDex-only inbox, dealer attribution via metadata)
  // Stamps ONLY for confirmed picks. Suggestions don't stamp the form because
  // the visitor hasn't agreed to the dealer affiliation yet.
  // ==========================================================================
  function stampForms(dealer) {
    var forms = document.querySelectorAll('form[action*="formspree"]');
    forms.forEach(function (form) {
      // Defensive cleanup: strip any stale dealer-email fields. Policy is
      // AmeriDex-only inbox; we never CC the dealer.
      removeHidden(form, '_cc');
      removeHidden(form, 'routed_to_dealer_email');

      if (!dealer) {
        removeHidden(form, 'routed_to_dealer');
        removeHidden(form, 'routed_to_dealer_name');
        var subj0 = form.querySelector('input[name="_subject"]');
        if (subj0) subj0.value = subj0.value.replace(/^\[[^\]]+\]\s*/, '');
        return;
      }

      ensureHidden(form, 'routed_to_dealer', dealer.slug);
      ensureHidden(form, 'routed_to_dealer_name', dealer.name + ' (' + dealer.location_label + ')');

      var prefix = '[' + dealer.slug + '] ';
      var existingSubject = form.querySelector('input[name="_subject"]');
      if (existingSubject) {
        var bare = existingSubject.value.replace(/^\[[^\]]+\]\s*/, '');
        existingSubject.value = prefix + bare;
      } else {
        ensureHidden(form, '_subject', prefix + (document.title || 'AmeriDex submission'));
      }
    });

    var noteHosts = document.querySelectorAll('[data-dealer-note]');
    noteHosts.forEach(function (host) {
      if (!dealer) { host.style.display = 'none'; host.innerHTML = ''; return; }
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
  function removeHidden(form, name) {
    var el = form.querySelector('input[name="' + cssEsc(name) + '"][type="hidden"]');
    if (el) el.parentNode.removeChild(el);
  }
  function cssEsc(s) { return String(s).replace(/"/g, '\\"'); }

  // ==========================================================================
  // CTA relabeling — only for confirmed picks (suggestions stay neutral)
  // ==========================================================================
  function relabelCtas(dealer) {
    document.querySelectorAll('[data-dealer-cta]').forEach(function (el) {
      if (!el.hasAttribute('data-dealer-cta-original')) {
        el.setAttribute('data-dealer-cta-original', el.textContent.trim());
      }
      if (dealer) {
        var city = cityOnly(dealer.location_label);
        el.textContent = 'Quote from ' + city;
        el.setAttribute('aria-label', 'Get a quote from ' + dealer.name + ' (' + dealer.location_label + ')');
      } else {
        el.textContent = el.getAttribute('data-dealer-cta-original');
        el.removeAttribute('aria-label');
      }
    });
  }

  // ==========================================================================
  // Main repaint pipeline
  // ==========================================================================
  function repaint() {
    AD.getActiveDealer().then(function (picked) {
      if (picked) {
        paintChip('confirmed', picked);
        paintBanner('confirmed', picked);
        stampForms(picked);
        relabelCtas(picked);
        return;
      }

      // No explicit pick — try a suggestion path, but only if not dismissed.
      stampForms(null);
      relabelCtas(null);

      if (getCookie(COOKIE_DISMISSED)) {
        // Visitor said "not now" within the last 24h. Stay quiet.
        paintChip(null, null);
        paintBanner(null, null);
        return;
      }

      // Try IP-based ZIP detection.
      detectZip().then(function (zip) {
        if (!zip) return;
        loadDealers().then(function (data) {
          var d = matchByZip(data, zip);
          if (!d) return;
          paintChip('suggested', d);
          paintBanner('suggested', d);
        });
      });
    });
  }

  // ---------- boot ----------
  document.addEventListener('DOMContentLoaded', function () {
    captureFromUrl();
    repaint();
    AD.onChange(repaint);
  });
})();
