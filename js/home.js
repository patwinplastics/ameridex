(() => {
  'use strict';
  const dialog = document.getElementById('color-dialog');
  if (!dialog) return;
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
