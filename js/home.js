(() => {
  'use strict';
  const theme = document.querySelector('.theme-switch');
  theme.addEventListener('click', () => {
    const dark = document.body.dataset.theme !== 'dark';
    document.body.dataset.theme = dark ? 'dark' : 'light';
    theme.textContent = dark ? 'Light' : 'Dark';
    theme.setAttribute('aria-pressed', String(dark));
    theme.setAttribute('aria-label', 'Switch to ' + (dark ? 'light' : 'dark') + ' theme');
  });
  const menuButton = document.querySelector('.home-menu-toggle');
  const menu = document.querySelector('.home-mobile-nav');
  function closeMenu() { menu.hidden = true; menuButton.setAttribute('aria-expanded','false'); menuButton.textContent = 'Menu'; }
  menuButton.addEventListener('click', () => {
    menu.hidden = !menu.hidden;
    menuButton.setAttribute('aria-expanded', String(!menu.hidden));
    menuButton.textContent = menu.hidden ? 'Menu' : 'Close';
  });
  menu.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !menu.hidden) { closeMenu(); menuButton.focus(); }
  });
  const mq = matchMedia('(min-width:851px)');
  mq.addEventListener('change', e => { if (e.matches) closeMenu(); });
  const dialog = document.getElementById('color-dialog');
  let trigger;
  document.querySelectorAll('.color-card').forEach(button => {
    button.addEventListener('click', () => {
      trigger = button;
      const name = button.dataset.color;
      const img = document.getElementById('color-dialog-image');
      img.src = 'assets/img/swatches-flat/' + button.dataset.slug + '.jpg';
      img.alt = name + ' cellular PVC decking texture close-up';
      document.getElementById('color-dialog-title').textContent = name;
      document.getElementById('color-dialog-sample').href = 'samples-request.html?color=' + encodeURIComponent(name);
      dialog.showModal();
      document.body.style.overflow = 'hidden';
    });
  });
  dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => {
    const r = dialog.getBoundingClientRect();
    if (e.target === dialog && (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => { document.body.style.overflow = ''; if (trigger) trigger.focus(); });
})();
