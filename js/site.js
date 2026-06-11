// AmeriDex Dryspace System - site.js
// Sticky header, mobile menu, reveal-on-scroll, query-param prefill, samples picker

(function() {
  'use strict';

  // Mark JS available so reveal anims activate
  document.documentElement.classList.add('js');

  // ===== Mobile menu toggle =====
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');
  const mobileClose = document.querySelector('.mobile-menu-close');

  function openMenu() {
    if (!mobileMenu) return;
    mobileMenu.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeMenu() {
    if (!mobileMenu) return;
    mobileMenu.classList.remove('open');
    document.body.style.overflow = '';
  }
  if (hamburger) hamburger.addEventListener('click', openMenu);
  if (mobileClose) mobileClose.addEventListener('click', closeMenu);
  if (mobileMenu) {
    mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  }

  // ===== Reveal on scroll =====
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
  }

  // ===== Quote page query-param prefill =====
  // ?type=dealer flips H1 + sub copy and hides the deck size fields.
  const qs = new URLSearchParams(window.location.search);
  if (qs.get('type') === 'dealer') {
    const h1 = document.querySelector('[data-quote-h1]');
    if (h1) h1.textContent = 'Become an AmeriDex Dealer';
    const sub = document.querySelector('[data-quote-sub]');
    if (sub) sub.textContent = "Tell us about your business. We'll get back to you within one business day.";
    const cardSub = document.querySelector('[data-quote-cardsub]');
    if (cardSub) cardSub.textContent = "Fill out the form below and our dealer team will be in touch within 1 business day.";
    document.querySelectorAll('[data-dealer-hide]').forEach(el => { el.style.display = 'none'; });
    const businessBlock = document.querySelector('[data-dealer-show]');
    if (businessBlock) businessBlock.style.display = '';
  }

  // ===== Samples request: size radio cards (visual selection) =====
  document.querySelectorAll('.size-radio').forEach(card => {
    const input = card.querySelector('input[type="radio"]');
    card.addEventListener('click', (ev) => {
      if (!input) return;
      input.checked = true;
      document.querySelectorAll('.size-radio').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    });
  });
  // Pre-select the first size radio that has [checked]
  const checkedSize = document.querySelector('.size-radio input[type="radio"]:checked');
  if (checkedSize) checkedSize.closest('.size-radio').classList.add('selected');

  // ===== Samples request: color toggle =====
  const colorPicks = document.querySelectorAll('.color-pick');
  const colorCounter = document.querySelector('.color-pick-counter');
  const hiddenColors = document.querySelector('input[name="selected_colors"]');
  function updateColorState() {
    const selected = Array.from(document.querySelectorAll('.color-pick.selected'))
      .map(el => el.getAttribute('data-color'));
    if (colorCounter) colorCounter.textContent = selected.length + (selected.length === 1 ? ' color selected' : ' colors selected');
    if (hiddenColors) hiddenColors.value = selected.join(', ');
  }
  colorPicks.forEach(el => {
    el.addEventListener('click', () => {
      el.classList.toggle('selected');
      updateColorState();
    });
  });
  const selectAll = document.querySelector('.select-all-pill');
  if (selectAll) {
    selectAll.addEventListener('click', () => {
      const allSelected = Array.from(colorPicks).every(c => c.classList.contains('selected'));
      colorPicks.forEach(c => c.classList.toggle('selected', !allSelected));
      selectAll.textContent = allSelected ? 'Select All' : 'Clear All';
      updateColorState();
    });
  }
  if (colorPicks.length) updateColorState();

  // ===== Floating dealer pill: hide when footer is in view so it never covers footer links =====
  var floatingPill = document.querySelector('.dealer-pill');
  var siteFooter = document.querySelector('.site-footer') || document.querySelector('footer');
  if (floatingPill && siteFooter && 'IntersectionObserver' in window) {
    var pillObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        floatingPill.classList.toggle('is-hidden', entry.isIntersecting);
      });
    }, { rootMargin: '0px 0px -40px 0px' });
    pillObserver.observe(siteFooter);
  }

  // ===== Warranty form: prefill today's date in signature_date if empty =====
  const sigDate = document.querySelector('input[name="signature_date"]');
  if (sigDate && !sigDate.value) {
    const t = new Date();
    const yyyy = t.getFullYear();
    const mm = String(t.getMonth() + 1).padStart(2, '0');
    const dd = String(t.getDate()).padStart(2, '0');
    sigDate.value = yyyy + '-' + mm + '-' + dd;
  }
})();
