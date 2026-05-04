// AmeriDex Dryspace System - site.js
// Sticky header, mobile menu, reveal-on-scroll, quote query-param prefill

(function() {
  'use strict';

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
  // If ?type=dealer, swap H1 and pre-select "Dealer prospect"
  const qs = new URLSearchParams(window.location.search);
  if (qs.get('type') === 'dealer') {
    const h1 = document.querySelector('[data-quote-h1]');
    if (h1) h1.textContent = 'Become an AmeriDex Dealer';
    const select = document.querySelector('select[name="role"]');
    if (select) {
      const opt = Array.from(select.options).find(o => /dealer/i.test(o.value) || /dealer/i.test(o.textContent));
      if (opt) select.value = opt.value;
    }
    const sub = document.querySelector('[data-quote-sub]');
    if (sub) sub.textContent = "Tell us about your business. We'll get back to you within one business day.";
  }
})();
