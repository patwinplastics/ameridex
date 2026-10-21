/* Phone and email click tracking (non-conversion events) using the site's
   existing Google tag (AW-11349043089) and Meta Pixel. No new IDs. */
(function () {
  'use strict';
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[href^="tel:"], a[href^="mailto:"]') : null;
    if (!a) return;
    var isTel = a.getAttribute('href').indexOf('tel:') === 0;
    var params = { link_url: a.getAttribute('href').split('?')[0], page_path: location.pathname };
    try { if (typeof window.gtag === 'function') window.gtag('event', isTel ? 'phone_click' : 'email_click', params); } catch (e) {}
    try { if (typeof window.fbq === 'function') window.fbq('trackCustom', isTel ? 'PhoneClick' : 'EmailClick', params); } catch (e) {}
  }, true);
})();
