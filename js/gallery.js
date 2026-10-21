// Gallery lightbox: click or tap to enlarge, Esc to close, arrow keys or swipe to move.
// Without JS (or without <dialog> support) each thumbnail links to the full image.
(function () {
  var dlg = document.getElementById('galLightbox');
  var links = Array.prototype.slice.call(document.querySelectorAll('.gal-link'));
  if (!dlg || !links.length || typeof dlg.showModal !== 'function') return;
  var img = dlg.querySelector('.gal-lb-img');
  var source = dlg.querySelector('.gal-lb-source');
  var cap = dlg.querySelector('.gal-lb-caption');
  var count = dlg.querySelector('.gal-lb-count');
  var current = 0, opener = null;

  function show(i) {
    current = (i + links.length) % links.length;
    var a = links[current];
    var thumb = a.querySelector('img');
    var fig = a.closest('figure');
    var text = fig && fig.querySelector('figcaption') ? fig.querySelector('figcaption').textContent : '';
    source.setAttribute('srcset', a.getAttribute('data-webp') || '');
    img.src = a.getAttribute('href');
    img.width = +a.getAttribute('data-w') || 0;
    img.height = +a.getAttribute('data-h') || 0;
    img.alt = thumb ? thumb.alt : '';
    cap.textContent = '';
    if (a.querySelector('.gal-tag')) {
      var t = document.createElement('span'); t.className = 'gal-tag'; t.textContent = 'Design inspiration';
      cap.appendChild(t);
    }
    cap.appendChild(document.createTextNode(text));
    count.textContent = 'Photo ' + (current + 1) + ' of ' + links.length;
  }
  function open(i, el) { opener = el; show(i); dlg.showModal(); dlg.querySelector('.gal-lb-close').focus(); document.documentElement.style.overflow = 'hidden'; }

  links.forEach(function (a, i) {
    a.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
      e.preventDefault(); open(i, a);
    });
  });
  dlg.querySelector('.gal-lb-close').addEventListener('click', function () { dlg.close(); });
  dlg.querySelector('.gal-lb-prev').addEventListener('click', function () { show(current - 1); });
  dlg.querySelector('.gal-lb-next').addEventListener('click', function () { show(current + 1); });
  dlg.addEventListener('close', function () { document.documentElement.style.overflow = ''; if (opener) opener.focus(); });
  dlg.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); show(current + 1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); show(current - 1); }
  });
  // Click on the dark backdrop (outside the photo and buttons) closes.
  dlg.addEventListener('click', function (e) { if (e.target === dlg || e.target.classList.contains('gal-lb-inner')) dlg.close(); });
  // Swipe left or right on touch screens.
  var x0 = null, y0 = null;
  dlg.addEventListener('touchstart', function (e) { if (e.touches.length === 1) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; } }, { passive: true });
  dlg.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) show(current + (dx < 0 ? 1 : -1));
    x0 = y0 = null;
  }, { passive: true });
})();
