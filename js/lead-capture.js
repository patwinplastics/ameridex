/* AmeriDex lead capture: planning-guide download and calculator estimate.
   Submits only when the visitor presses the button. Posts to the AmeriDex
   Formspree inbox, then fires the existing Google Ads and Meta Pixel events. */
(() => {
  'use strict';
  const ENDPOINT = 'https://formspree.io/f/xreljrrd';

  function track(type) {
    try { if (typeof gtag === 'function') gtag('event', 'generate_lead', { form_type: type }); } catch (e) {}
    try { if (typeof fbq === 'function') fbq('track', 'Lead', { content_name: type }); } catch (e) {}
  }

  function setHidden(form, name, value) {
    let el = form.querySelector('input[type="hidden"][name="' + name + '"]');
    if (!el) { el = document.createElement('input'); el.type = 'hidden'; el.name = name; form.appendChild(el); }
    el.value = value == null ? '' : String(value);
  }

  document.querySelectorAll('form[data-lead-form]').forEach(form => {
    const type = form.dataset.leadForm;
    const status = form.querySelector('[data-lead-status]');
    const button = form.querySelector('button[type="submit"]');
    const success = document.getElementById(form.dataset.leadSuccess || '');

    form.addEventListener('submit', async e => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      if (type === 'estimate' && typeof form.leadBeforeSubmit === 'function' && !form.leadBeforeSubmit()) return;
      setHidden(form, 'page', location.pathname);
      setHidden(form, 'referrer', document.referrer);
      const original = button.textContent;
      button.disabled = true; button.textContent = 'Sending...';
      if (status) status.textContent = '';
      try {
        const res = await fetch(ENDPOINT, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        track(type);
        form.hidden = true;
        if (success) { success.hidden = false; success.focus({ preventScroll: false }); }
      } catch (err) {
        button.disabled = false; button.textContent = original;
        if (status) status.textContent = 'Something went wrong. Please try again, or call 800-217-9206.';
      }
    });
  });
})();
