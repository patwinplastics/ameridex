/* AmeriDex blog: interactive checklist progress.
   Persists each step's checked state in localStorage, keyed per page,
   and drives a progress bar + count. No dependencies. */
(function () {
  function init() {
    var lists = document.querySelectorAll('[data-checklist]');
    if (!lists.length) return;

    lists.forEach(function (list) {
      var key = 'ameridex-checklist:' + (list.getAttribute('data-checklist') || location.pathname);
      var boxes = Array.prototype.slice.call(list.querySelectorAll('input[type="checkbox"][data-step]'));
      if (!boxes.length) return;

      var saved = {};
      try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) { saved = {}; }

      var bar = document.querySelector('[data-checklist-bar="' + list.getAttribute('data-checklist') + '"] .blog-progress-fill');
      var label = document.querySelector('[data-checklist-bar="' + list.getAttribute('data-checklist') + '"] [data-checklist-count]');
      var total = boxes.length;

      function syncCard(box) {
        var card = box.closest('.blog-step');
        if (card) card.classList.toggle('is-done', box.checked);
      }

      function update() {
        var done = boxes.filter(function (b) { return b.checked; }).length;
        var pct = total ? Math.round((done / total) * 100) : 0;
        if (bar) bar.style.width = pct + '%';
        if (label) label.textContent = done + ' of ' + total + ' done';
      }

      boxes.forEach(function (box) {
        var id = box.getAttribute('data-step');
        if (saved[id]) box.checked = true;
        syncCard(box);
        box.addEventListener('change', function () {
          saved[id] = box.checked;
          try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {}
          syncCard(box);
          update();
        });
      });

      update();

      var reset = document.querySelector('[data-checklist-reset="' + list.getAttribute('data-checklist') + '"]');
      if (reset) {
        reset.addEventListener('click', function () {
          boxes.forEach(function (box) { box.checked = false; syncCard(box); });
          saved = {};
          try { localStorage.removeItem(key); } catch (e) {}
          update();
        });
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
