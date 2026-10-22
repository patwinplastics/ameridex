/* DexerDry install help: instant answer search. Vanilla JS, no dependencies.
 * Data: data/dexerdry-install.json (same file tools/build-install-help.py renders
 * into the page). If the JSON cannot be fetched, search falls back to the answers
 * already in the page. Deep links: ?q=search+words and #answer-id.
 */
(function () {
  'use strict';
  var input = document.getElementById('ih-q');
  var list = document.getElementById('ih-list');
  if (!input || !list) return;
  var form = input.form;
  var statusEl = document.getElementById('ih-status');
  var emptyEl = document.getElementById('ih-empty');
  var moreWrap = document.querySelector('.ih-more');
  var moreBtn = document.getElementById('ih-more');
  var clearBtn = document.querySelector('.ih-clear');
  var catsEl = document.querySelector('.ih-cats');
  var PAGE = 15;
  var items = [];
  var category = '';
  var limit = PAGE;
  var timer = 0;

  var STOP = ' a an and are as at be can do does for from how i if in is it my of on or should so that the then this to what when where which who why will with you your me we our need use using get '.split(' ');
  var STOPSET = {};
  STOP.forEach(function (w) { if (w) STOPSET[w] = 1; });

  function normalize(s) {
    return String(s || '').toLowerCase()
      .replace(/[\u2018\u2019']/g, '')
      .replace(/(\d)\s*\/\s*(\d)/g, '$1/$2')
      .replace(/[^a-z0-9/.]+/g, ' ')
      .replace(/(^|\s)\.|\.(\s|$)/g, ' ')
      .trim();
  }
  function stem(w) {
    if (w.length > 5 && /ing$/.test(w)) return w.slice(0, -3);
    if (w.length > 4 && /ied$|ies$/.test(w)) return w.slice(0, -3) + 'y';
    if (w.length > 4 && /ed$/.test(w)) return w.slice(0, -2);
    if (w.length > 4 && /es$/.test(w) && /(s|x|z|ch|sh)es$/.test(w)) return w.slice(0, -2);
    if (w.length > 3 && /s$/.test(w) && !/ss$/.test(w)) return w.slice(0, -1);
    return w;
  }
  function tokens(s, keepStop) {
    var out = [];
    normalize(s).split(' ').forEach(function (w) {
      if (!w) return;
      if (!keepStop && STOPSET[w]) return;
      out.push(stem(w));
    });
    return out;
  }
  // Damerau-Levenshtein distance with an early exit once it exceeds max.
  function dist(a, b, max) {
    if (Math.abs(a.length - b.length) > max) return max + 1;
    var prev2 = null, prev = [], cur, i, j;
    for (j = 0; j <= b.length; j++) prev[j] = j;
    for (i = 1; i <= a.length; i++) {
      cur = [i];
      var rowMin = i;
      for (j = 1; j <= b.length; j++) {
        var cost = a[i - 1] === b[j - 1] ? 0 : 1;
        var v = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost);
        if (prev2 && i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) v = Math.min(v, prev2[j - 2] + 1);
        cur[j] = v;
        if (v < rowMin) rowMin = v;
      }
      if (rowMin > max) return max + 1;
      prev2 = prev; prev = cur;
    }
    return prev[b.length];
  }
  // How well one query word matches a set of field words (0 to 1).
  function wordScore(q, words, isLast) {
    if (words[q]) return 1;
    var best = 0, w;
    var maxTypo = q.length >= 8 ? 2 : (q.length >= 4 ? 1 : 0);
    for (w in words) {
      if (w.length > q.length && w.indexOf(q) === 0 && q.length >= 2) {
        // Prefix match. The word still being typed gets full credit sooner.
        var p = (isLast ? 0.9 : 0.75);
        if (p > best) best = p;
      } else if (maxTypo && dist(q, w, maxTypo) <= maxTypo) {
        if (0.65 > best) best = 0.65;
      } else if (q.length >= 5 && w.length >= 5 && q.indexOf(w) === 0) {
        if (0.6 > best) best = 0.6;
      }
      if (best >= 0.9) break;
    }
    return best;
  }
  var FIELDS = [['q', 6], ['alt', 4.5], ['kw', 5], ['short', 2], ['ans', 1]];
  // Everyday words builders use for the same thing. Matches through a synonym
  // count slightly less than a direct match.
  var SYN = {
    spacing: ['space', 'gap', 'apart', 'distance', 'center', 'per'], apart: ['spacing', 'gap', 'space'], gap: ['spacing', 'space', 'apart'],
    slope: ['pitch', 'fall', 'angle'], pitch: ['slope', 'fall'], fall: ['slope', 'pitch'],
    seam: ['splice', 'joint', 'butt', 'gutter'], splice: ['seam', 'joint'], joint: ['seam', 'splice'],
    screw: ['fasten', 'fastener', 'fastening', 'plug'], fastener: ['screw', 'fasten', 'fastening'], nail: ['screw', 'fasten', 'fastener'],
    caulk: ['sealant', 'seal', 'glue'], sealant: ['caulk'], glue: ['caulk', 'adhesive'],
    power: ['pressure'], pressure: ['power'], wash: ['clean', 'cleaning'], clean: ['wash', 'cleaning'],
    gutter: ['drain', 'drainage', 'trough'], drain: ['gutter', 'drainage'], leak: ['drip', 'water', 'wet', 'troubleshoot'],
    strip: ['flange', 'dexerdry', 'seal'], flange: ['strip', 'seal'], seal: ['flange', 'strip', 'caulk'],
    tool: ['wrench', 'bender', 'compression'], compress: ['compression', 'tight', 'wrench'], tight: ['compression', 'compress'],
    ledger: ['house', 'wall'], house: ['ledger', 'wall'], wall: ['ledger', 'house'],
    board: ['decking', 'plank'], plank: ['board', 'decking'], joist: ['framing', 'frame'], frame: ['framing', 'joist']
  };
  var SYNSTEM = {};
  Object.keys(SYN).forEach(function (k) { SYNSTEM[stem(k)] = SYN[k].map(stem); });
  var NOISE = { far: 1, much: 1, many: 1, long: 0, big: 1, between: 1, there: 1, any: 1, put: 1, go: 1, goes: 1, have: 1, has: 1, off: 1, out: 1 };

  function index(raw) {
    function set(text) { var o = {}; tokens(text).forEach(function (t) { o[t] = 1; }); return o; }
    var alts = (raw.alt_questions || []).join(' | ');
    var kws = (raw.keywords || []).join(' | ');
    return {
      raw: raw,
      q: set(raw.question), alt: set(alts), kw: set(kws + ' ' + raw.category),
      short: set(raw.short_answer), ans: set(raw.answer),
      phrase: ' ' + normalize(raw.question + ' | ' + alts + ' | ' + kws) + ' ',
      el: null
    };
  }

  function score(it, qt, qPhrase) {
    var total = 0, matched = 0;
    for (var i = 0; i < qt.length; i++) {
      var best = 0;
      var alts = SYNSTEM[qt[i]] || [];
      for (var f = 0; f < FIELDS.length; f++) {
        var s = wordScore(qt[i], it[FIELDS[f][0]], i === qt.length - 1) * FIELDS[f][1];
        for (var a = 0; a < alts.length && s < FIELDS[f][1]; a++) {
          var sa = (it[FIELDS[f][0]][alts[a]] ? 0.8 : 0) * FIELDS[f][1];
          if (sa > s) s = sa;
        }
        if (s > best) best = s;
      }
      if (best > 0) matched++;
      total += best;
    }
    if (!matched) return 0;
    var coverage = matched / qt.length;
    total = total * (0.4 + 0.6 * coverage);
    if (qPhrase.indexOf(' ') > 0 && it.phrase.indexOf(' ' + qPhrase) !== -1) total += 8;
    return total;
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function buildEl(raw) {
    var d = el('details', 'ih-item');
    d.id = raw.id;
    d.setAttribute('data-cat', raw.category);
    var s = el('summary');
    s.appendChild(el('span', 'ih-q', raw.question));
    s.appendChild(el('span', 'ih-short', raw.short_answer));
    s.appendChild(el('span', 'ih-cat', raw.category));
    d.appendChild(s);
    var b = el('div', 'ih-body');
    var tmp = document.createElement('template');
    tmp.innerHTML = String(raw.answer_html || '').replace(/<(?!\/?(p|strong)>)[^>]*>/g, '');
    b.appendChild(tmp.content);
    if (raw.video_url) {
      var p = el('p');
      var a = el('a', 'ih-watch');
      a.href = raw.video_url; a.target = '_blank'; a.rel = 'noopener';
      a.appendChild(document.createTextNode('\u25B6 Watch this step '));
      a.appendChild(el('small', null, raw.video_title + ' at ' + raw.timestamp_label + ' (opens in a new tab)'));
      p.appendChild(a); b.appendChild(p);
    }
    d.appendChild(b);
    return d;
  }
  // Fallback when the JSON is unavailable: read the answers already in the page.
  function fromDom() {
    return Array.prototype.map.call(list.querySelectorAll('.ih-item'), function (d) {
      var body = d.querySelector('.ih-body');
      return {
        id: d.id,
        question: d.querySelector('.ih-q').textContent,
        short_answer: d.querySelector('.ih-short').textContent,
        answer: body ? body.textContent : '',
        category: d.getAttribute('data-cat') || '',
        alt_questions: [], keywords: []
      };
    });
  }

  function setup(rawItems, cats) {
    items = rawItems.map(index);
    var existing = {};
    Array.prototype.forEach.call(list.querySelectorAll('.ih-item'), function (d) { existing[d.id] = d; });
    items.forEach(function (it) { it.el = existing[it.raw.id] || buildEl(it.raw); });
    // Drop static answers that are no longer in the data.
    Object.keys(existing).forEach(function (id) {
      if (!items.some(function (it) { return it.raw.id === id; })) existing[id].remove();
    });
    buildChips(cats && cats.length ? cats : uniqueCats());
  }
  function uniqueCats() {
    var seen = {}, out = [];
    items.forEach(function (it) { var c = it.raw.category; if (c && !seen[c]) { seen[c] = 1; out.push(c); } });
    return out;
  }
  function buildChips(cats) {
    if (!catsEl) return;
    var counts = {};
    items.forEach(function (it) { counts[it.raw.category] = (counts[it.raw.category] || 0) + 1; });
    function chip(value, label, n) {
      var b = el('button', 'ih-chip');
      b.type = 'button';
      b.setAttribute('data-cat', value);
      b.setAttribute('aria-pressed', value === category ? 'true' : 'false');
      b.appendChild(document.createTextNode(label));
      var c = el('span', 'n', String(n)); c.setAttribute('aria-hidden', 'true');
      b.appendChild(c);
      b.setAttribute('aria-label', label + ', ' + n + ' answers');
      catsEl.appendChild(b);
    }
    chip('', 'All topics', items.length);
    cats.forEach(function (c) { if (counts[c]) chip(c, c, counts[c]); });
    catsEl.hidden = false;
    catsEl.addEventListener('click', function (e) {
      var b = e.target.closest('.ih-chip');
      if (!b) return;
      category = b.getAttribute('data-cat');
      Array.prototype.forEach.call(catsEl.querySelectorAll('.ih-chip'), function (x) {
        x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
      });
      limit = PAGE;
      run();
    });
  }

  function run() {
    var query = input.value;
    var qt = tokens(query).filter(function (t) { return !NOISE[t]; });
    if (!qt.length && normalize(query)) qt = tokens(query, true);
    var qPhrase = normalize(query);
    var pool = items.filter(function (it) { return !category || it.raw.category === category; });
    var results;
    if (qt.length) {
      results = pool.map(function (it) { return { it: it, s: score(it, qt, qPhrase) }; })
        .filter(function (r) { return r.s >= 2; })
        .sort(function (a, b) { return b.s - a.s; });
      var top = results.length ? results[0].s : 0;
      results = results.filter(function (r) { return r.s >= top * 0.3; })
        .map(function (r) { return r.it; });
    } else {
      results = pool;
    }
    var shown = results.slice(0, limit);
    var frag = document.createDocumentFragment();
    shown.forEach(function (it) { frag.appendChild(it.el); });
    // Keep hidden answers in the DOM (so #id links and find-in-page still work).
    items.forEach(function (it) { it.el.hidden = shown.indexOf(it) === -1; });
    results.slice(limit).concat(items.filter(function (it) { return results.indexOf(it) === -1; }))
      .forEach(function (it) { frag.appendChild(it.el); });
    list.appendChild(frag);

    emptyEl.hidden = results.length > 0;
    moreWrap.hidden = results.length <= limit;
    if (!moreWrap.hidden) moreBtn.textContent = 'Show ' + Math.min(PAGE, results.length - limit) + ' more of ' + (results.length - limit) + ' remaining';
    clearBtn.hidden = !query;

    var where = category ? ' in ' + category : '';
    var msg;
    if (!qt.length) msg = 'Showing ' + shown.length + ' of ' + results.length + ' install answers' + where + '. Type a question to search.';
    else if (!results.length) msg = 'No answers found for \u201C' + query.trim() + '\u201D' + where + '.';
    else msg = results.length + (results.length === 1 ? ' answer' : ' answers') + ' for \u201C' + query.trim() + '\u201D' + where + (results.length > shown.length ? ', showing the top ' + shown.length : '') + '.';
    statusEl.textContent = msg;
    return results;
  }

  function syncUrl() {
    var url = new URL(window.location.href);
    var q = input.value.trim();
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    try { history.replaceState(null, '', url.pathname + url.search + url.hash); } catch (e) { /* file:// or sandbox */ }
  }

  function openHash() {
    var id = decodeURIComponent((window.location.hash || '').slice(1));
    if (!id) return;
    var it = items.filter(function (x) { return x.raw.id === id; })[0];
    if (!it) return;
    if (it.el.hidden) {
      // Make sure the linked answer is visible even if the search would hide it.
      category = ''; markChip(''); input.value = ''; limit = PAGE; run();
      list.insertBefore(it.el, list.firstChild);
      it.el.hidden = false;
    }
    it.el.open = true;
    it.el.scrollIntoView({ block: 'start' });
    var s = it.el.querySelector('summary');
    if (s) s.focus({ preventScroll: true });
  }
  function markChip(value) {
    if (!catsEl) return;
    Array.prototype.forEach.call(catsEl.querySelectorAll('.ih-chip'), function (x) {
      x.setAttribute('aria-pressed', x.getAttribute('data-cat') === value ? 'true' : 'false');
    });
  }

  function wire() {
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { limit = PAGE; run(); syncUrl(); }, 140);
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearTimeout(timer); limit = PAGE; run(); syncUrl();
      var first = list.querySelector('.ih-item:not([hidden]) summary');
      if (first && input.value.trim()) first.focus();
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && input.value) { input.value = ''; limit = PAGE; run(); syncUrl(); }
    });
    clearBtn.addEventListener('click', function () { input.value = ''; limit = PAGE; run(); syncUrl(); input.focus(); });
    moreBtn.addEventListener('click', function () {
      var before = limit;
      limit += PAGE; run();
      var next = list.querySelectorAll('.ih-item:not([hidden]) summary')[before];
      if (next) next.focus();
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-try]'), function (b) {
      b.addEventListener('click', function () { input.value = b.getAttribute('data-try'); limit = PAGE; run(); syncUrl(); input.focus(); });
    });
    // Opening an answer updates the address bar so it can be shared.
    list.addEventListener('toggle', function (e) {
      var d = e.target;
      if (!d.classList || !d.classList.contains('ih-item') || !d.open) return;
      try { history.replaceState(null, '', location.pathname + location.search + '#' + d.id); } catch (err) { /* ignore */ }
      if (window.gtag) { try { window.gtag('event', 'install_help_open', { answer_id: d.id, search_term: input.value.trim() }); } catch (err) { /* ignore */ } }
    }, true);
    window.addEventListener('hashchange', openHash);
  }

  function start(rawItems, cats) {
    setup(rawItems, cats);
    wire();
    var params = new URLSearchParams(window.location.search);
    if (params.get('q')) input.value = params.get('q');
    run();
    openHash();
  }

  var src = list.getAttribute('data-src') || 'data/dexerdry-install.json';
  if (window.fetch) {
    fetch(src, { credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) { start(d.qa || [], d.categories || []); })
      .catch(function () { start(fromDom(), null); });
  } else {
    start(fromDom(), null);
  }
})();
