/* AmeriDex background form submit (Formspree).
   Opt-in per form: <form data-ajax-submit data-thanks="thanks-x.html"
     data-lead-name="..." (fires Meta Lead on success)
     data-ads-event="..." (fires that Google Ads event on success)>
   - Posts the same fields to the same Formspree endpoint as a normal submit.
   - Tracking fires only after Formspree confirms success, then redirects.
   - On ANY failure (network, timeout, reCAPTCHA, plan or validation error)
     it falls back to a normal form post, so the lead is never dropped.
   - Without JavaScript the form still posts normally. */
(function () {
  'use strict';
  if (!window.fetch || !window.FormData || !window.Promise) return;

  function track(form) {
    return new Promise(function (resolve) {
      var done = false;
      function finish() { if (!done) { done = true; resolve(); } }
      var lead = form.getAttribute('data-lead-name');
      var ads = form.getAttribute('data-ads-event');
      try { if (lead && typeof window.fbq === 'function') window.fbq('track', 'Lead', { content_name: lead }); } catch (e) {}
      if (ads && typeof window.gtag === 'function') {
        try { window.gtag('event', ads, { event_callback: finish, event_timeout: 1500 }); } catch (e) { finish(); }
        setTimeout(finish, 1600);
      } else {
        setTimeout(finish, lead ? 500 : 0);
      }
    });
  }

  function bind(form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (form.getAttribute('data-submitting') === '1') return;
      form.setAttribute('data-submitting', '1');
      var btn = form.querySelector('button[type="submit"], input[type="submit"]');
      var label = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }
      var accepted = false;

      function fallback() {
        if (accepted) return;
        form.removeAttribute('data-submitting');
        if (btn) { btn.disabled = false; btn.textContent = label; }
        HTMLFormElement.prototype.submit.call(form);
      }

      var body;
      try { body = new FormData(form); } catch (e) { fallback(); return; }
      var ctrl = window.AbortController ? new AbortController() : null;
      var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 60000);

      fetch(form.getAttribute('action'), {
        method: 'POST',
        body: body,
        headers: { Accept: 'application/json' },
        signal: ctrl ? ctrl.signal : undefined
      }).then(function (res) {
        clearTimeout(timer);
        if (!res.ok) throw new Error('Formspree status ' + res.status);
        accepted = true;
        return track(form).then(function () {
          window.location.href = form.getAttribute('data-thanks');
        });
      }).catch(function () {
        clearTimeout(timer);
        fallback();
      });
    });
  }

  document.querySelectorAll('form[data-ajax-submit][action*="formspree.io"]').forEach(bind);
})();
