/* Single behavior controller for navigation on every static page. */
(() => {
  const header = document.querySelector('.shared-header');
  if (!header) return;
  const theme = header.querySelector('.theme-switch');
  theme.addEventListener('click', () => {
    const dark = document.body.dataset.theme !== 'dark';
    document.body.dataset.theme = dark ? 'dark' : 'light';
    theme.textContent = dark ? 'Light' : 'Dark';
    theme.setAttribute('aria-pressed', String(dark));
    theme.setAttribute('aria-label', 'Switch navigation to ' + (dark ? 'light' : 'dark') + ' theme');
  });
  const button = header.querySelector('.home-menu-toggle');
  const menu = header.querySelector('.home-mobile-nav');
  function close() { menu.hidden = true; button.textContent = 'Menu'; button.setAttribute('aria-expanded','false'); }
  button.addEventListener('click', () => {
    menu.hidden = !menu.hidden;
    button.textContent = menu.hidden ? 'Menu' : 'Close';
    button.setAttribute('aria-expanded', String(!menu.hidden));
  });
  menu.querySelectorAll('a').forEach(a => a.addEventListener('click',close));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !menu.hidden) { close(); button.focus(); }
  });
  document.addEventListener('click', e => { if (!menu.hidden && !header.contains(e.target)) close(); });
  matchMedia('(min-width:1101px)').addEventListener('change', e => { if(e.matches) close(); });
})();
